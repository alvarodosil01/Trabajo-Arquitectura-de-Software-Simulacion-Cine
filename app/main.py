"""Punto de entrada: python -m uvicorn app.main:app --reload."""

from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, Query, Request, Response
from fastapi.responses import JSONResponse
from pydantic import EmailStr
from sqlalchemy.exc import IntegrityError, OperationalError

from app.database import create_database_engine, initialize_database
from app.dependencies import get_cine_service
from app.schemas import (
    DisponibilidadOutput, PeliculaInput, PeliculaOutput, ReservaInput,
    ReservaOutput, SalaOutput, SesionInput, SesionOutput,
)
from cine.models.pelicula import Pelicula
from cine.services.cine_service import CineService
from cine.services.errors import ConflictError, NotFoundError


Service = Annotated[CineService, Depends(get_cine_service, scope="function")]


def create_app(database_url: str | None = None) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        engine = create_database_engine(database_url)
        app.state.engine = engine
        try:
            initialize_database(engine)
            yield
        finally:
            engine.dispose()

    application = FastAPI(
        title="API del cine",
        description="Películas, salas, sesiones y reservas. Primera prueba sin autenticación.",
        lifespan=lifespan,
    )

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


    @application.get("/peliculas", response_model=list[PeliculaOutput], tags=["Películas"])
    def peliculas(service: Service):
        return list(service.peliculas.values())


    @application.post("/peliculas", response_model=PeliculaOutput, status_code=201, tags=["Películas"])
    def crear_pelicula(data: PeliculaInput, service: Service):
        return service.agregar_pelicula(Pelicula(**data.model_dump()))


    @application.get("/peliculas/{pelicula_id}", response_model=PeliculaOutput, tags=["Películas"])
    def pelicula(pelicula_id: str, service: Service):
        return service.obtener("peliculas", pelicula_id)


    @application.put("/peliculas/{pelicula_id}", response_model=PeliculaOutput, tags=["Películas"])
    def actualizar_pelicula(pelicula_id: str, data: PeliculaInput, service: Service):
        return service.actualizar_pelicula(pelicula_id, **data.model_dump())


    @application.delete("/peliculas/{pelicula_id}", status_code=204, tags=["Películas"])
    def eliminar_pelicula(pelicula_id: str, service: Service):
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
    def crear_sesion(data: SesionInput, service: Service):
        return service.crear_sesion(**data.model_dump())


    @application.get("/sesiones/{sesion_id}", response_model=SesionOutput, tags=["Sesiones"])
    def sesion(sesion_id: str, service: Service):
        return service.obtener("sesiones", sesion_id)


    @application.put("/sesiones/{sesion_id}", response_model=SesionOutput, tags=["Sesiones"])
    def actualizar_sesion(sesion_id: str, data: SesionInput, service: Service):
        return service.actualizar_sesion(sesion_id, **data.model_dump())


    @application.delete("/sesiones/{sesion_id}", status_code=204, tags=["Sesiones"])
    def eliminar_sesion(sesion_id: str, service: Service):
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
