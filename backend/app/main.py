"""Punto de entrada: python -m uvicorn app.main:app --reload."""

from contextlib import asynccontextmanager
from typing import Annotated

import os

from fastapi import Depends, FastAPI, HTTPException, Query, Request, Response, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr
from sqlalchemy.exc import IntegrityError, OperationalError

from app.database import crear_admin_inicial, create_database_engine, initialize_database
from app.dependencies import AdminActual, Service
from app.schemas import (
    AdministradorInput, AdministradorOutput, DisponibilidadOutput, PeliculaInput,
    PeliculaOutput, ReservaInput, ReservaOutput, SalaOutput, SesionInput,
    SesionOutput, TokenOutput,
)
from app.security import cargar_secreto, crear_token, minutos_expiracion
from cine.models.pelicula import Pelicula
from cine.services.errors import ConflictError, NotFoundError


def create_app(database_url: str | None = None, jwt_secret: str | None = None) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        engine = create_database_engine(database_url)
        app.state.engine = engine
        try:
            initialize_database(engine)
            crear_admin_inicial(
                engine,
                os.getenv("ADMIN_EMAIL"),
                os.getenv("ADMIN_PASSWORD"),
                os.getenv("ADMIN_NOMBRE", "Administrador"),
            )
            yield
        finally:
            engine.dispose()

    application = FastAPI(
        title="API del cine",
        description=(
            "Películas, salas, sesiones y reservas. Las consultas y la compra de "
            "entradas son públicas; la gestión de películas, sesiones y "
            "administradores exige un token JWT de administrador "
            "(botón **Authorize**)."
        ),
        lifespan=lifespan,
    )
    application.state.jwt_secret = cargar_secreto(jwt_secret)
    application.state.jwt_minutes = minutos_expiracion()

    @application.exception_handler(ValueError)
    async def domain_error(request: Request, error: ValueError):
        status = 404 if isinstance(error, NotFoundError) else (
            409 if isinstance(error, ConflictError) else 422
        )
        return JSONResponse(status_code=status, content={"detail": str(error)})

    @application.exception_handler(IntegrityError)
    async def integrity_error(request: Request, error: IntegrityError):
        return JSONResponse(status_code=409, content={"detail": "Conflicto con los datos existentes"})

    @application.exception_handler(OperationalError)
    async def database_error(request: Request, error: OperationalError):
        return JSONResponse(status_code=503, content={"detail": "Base de datos no disponible; vuelve a intentarlo"})

    @application.get("/", tags=["Estado"])
    def root():
        return {"nombre": "API del cine", "docs": "/docs"}


    @application.post("/auth/login", response_model=TokenOutput, tags=["Autenticación"])
    def login(form: Annotated[OAuth2PasswordRequestForm, Depends()], service: Service,
              request: Request):
        """Inicia sesión de administrador. En `username` va el email."""
        admin = service.autenticar_administrador(form.username, form.password)
        if admin is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email o contraseña incorrectos",
                headers={"WWW-Authenticate": "Bearer"},
            )
        minutos = request.app.state.jwt_minutes
        token = crear_token(admin, request.app.state.jwt_secret, minutos)
        return {"access_token": token, "token_type": "bearer", "expires_in": minutos * 60}


    @application.get("/auth/me", response_model=AdministradorOutput, tags=["Autenticación"])
    def yo(admin: AdminActual):
        return admin


    @application.post("/administradores", response_model=AdministradorOutput,
                      status_code=201, tags=["Autenticación"])
    def crear_administrador(data: AdministradorInput, service: Service, admin: AdminActual):
        """Solo un administrador puede dar de alta a otro."""
        return service.registrar_administrador(**data.model_dump())


    @application.get("/peliculas", response_model=list[PeliculaOutput], tags=["Películas"])
    def peliculas(service: Service):
        return list(service.peliculas.values())


    @application.post("/peliculas", response_model=PeliculaOutput, status_code=201, tags=["Películas"])
    def crear_pelicula(data: PeliculaInput, service: Service, admin: AdminActual):
        return service.agregar_pelicula(Pelicula(**data.model_dump()))


    @application.get("/peliculas/{pelicula_id}", response_model=PeliculaOutput, tags=["Películas"])
    def pelicula(pelicula_id: str, service: Service):
        return service.obtener("peliculas", pelicula_id)


    @application.put("/peliculas/{pelicula_id}", response_model=PeliculaOutput, tags=["Películas"])
    def actualizar_pelicula(pelicula_id: str, data: PeliculaInput, service: Service, admin: AdminActual):
        return service.actualizar_pelicula(pelicula_id, **data.model_dump())


    @application.delete("/peliculas/{pelicula_id}", status_code=204, tags=["Películas"])
    def eliminar_pelicula(pelicula_id: str, service: Service, admin: AdminActual):
        service.eliminar_pelicula(pelicula_id)
        return Response(status_code=204)


    @application.get("/salas", response_model=list[SalaOutput], tags=["Salas"])
    def salas(service: Service):
        return sorted(service.salas.values(), key=lambda sala: sala.numero)


    @application.get("/salas/{sala_id}", response_model=SalaOutput, tags=["Salas"])
    def sala(sala_id: str, service: Service):
        return service.obtener("salas", sala_id)


    @application.get("/sesiones", response_model=list[SesionOutput], tags=["Sesiones"])
    def sesiones(service: Service, pelicula_id: str | None = None):
        return service.listar_sesiones(pelicula_id)


    @application.post("/sesiones", response_model=SesionOutput, status_code=201, tags=["Sesiones"])
    def crear_sesion(data: SesionInput, service: Service, admin: AdminActual):
        return service.crear_sesion(**data.model_dump())


    @application.get("/sesiones/{sesion_id}", response_model=SesionOutput, tags=["Sesiones"])
    def sesion(sesion_id: str, service: Service):
        return service.obtener("sesiones", sesion_id)


    @application.put("/sesiones/{sesion_id}", response_model=SesionOutput, tags=["Sesiones"])
    def actualizar_sesion(sesion_id: str, data: SesionInput, service: Service, admin: AdminActual):
        return service.actualizar_sesion(sesion_id, **data.model_dump())


    @application.delete("/sesiones/{sesion_id}", status_code=204, tags=["Sesiones"])
    def eliminar_sesion(sesion_id: str, service: Service, admin: AdminActual):
        service.eliminar_sesion(sesion_id)
        return Response(status_code=204)


    @application.get("/sesiones/{sesion_id}/butacas", response_model=DisponibilidadOutput, tags=["Sesiones"])
    def butacas(sesion_id: str, service: Service):
        sesion = service.obtener("sesiones", sesion_id)
        return {"sesion_id": sesion_id, "disponibles": service.butacas_disponibles(sesion_id),
                "ocupadas": sorted(sesion.butacas_ocupadas)}


    @application.post("/reservas", response_model=ReservaOutput, status_code=201, tags=["Reservas"])
    def crear_reserva(data: ReservaInput, service: Service):
        return service.crear_reserva(**data.model_dump())


    @application.get("/reservas", response_model=list[ReservaOutput], tags=["Reservas"])
    def reservas(service: Service, email: Annotated[EmailStr, Query()]):
        return service.listar_reservas_por_email(str(email))


    @application.get("/reservas/{reserva_id}", response_model=ReservaOutput, tags=["Reservas"])
    def reserva(reserva_id: str, service: Service):
        return service.obtener("reservas", reserva_id)

    return application


app = create_app()
