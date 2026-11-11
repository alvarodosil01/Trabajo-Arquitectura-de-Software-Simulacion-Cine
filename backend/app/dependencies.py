"""Dependencias compartidas por las rutas HTTP."""

from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.crud import load_service, save_service
from app.security import decodificar_token
from cine.models.usuario import Administrador
from cine.services.cine_service import CineService


def get_cine_service(request: Request):
    """Carga, valida y guarda en una sola transacción; revierte ante errores."""
    with Session(request.app.state.engine) as db, db.begin():
        service = load_service(db)
        yield service
        if request.method not in {"GET", "HEAD", "OPTIONS"}:
            save_service(db, service)


Service = Annotated[CineService, Depends(get_cine_service, scope="function")]

# Habilita el botón "Authorize" de Swagger, que llama a POST /auth/login
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_admin_actual(
    request: Request,
    token: Annotated[str, Depends(oauth2_scheme)],
    service: Service,
) -> Administrador:
    """Exige un token JWT válido de un administrador que siga existiendo."""
    no_autenticado = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token no válido o caducado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decodificar_token(token, request.app.state.jwt_secret)
    except jwt.InvalidTokenError:
        raise no_autenticado
    if payload.get("rol") != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Se necesita rol de administrador")
    admin = service.obtener_administrador(payload["sub"])
    if admin is None:
        raise no_autenticado
    return admin


AdminActual = Annotated[Administrador, Depends(get_admin_actual)]
