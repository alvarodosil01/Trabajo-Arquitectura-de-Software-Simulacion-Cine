"""Autenticación con tokens JWT (HS256).

El secreto se lee de la variable de entorno JWT_SECRET. Si no existe, se genera
uno aleatorio al arrancar: sirve para probar en local, pero los tokens dejan de
valer al reiniciar el servidor. En Docker o en producción hay que definirlo.
"""

import logging
import os
import secrets
from datetime import datetime, timedelta, timezone

import jwt

from cine.models.usuario import Administrador


ALGORITMO = "HS256"
EXPIRACION_POR_DEFECTO = 60  # minutos
logger = logging.getLogger("uvicorn.error")


def cargar_secreto(secreto: str | None = None) -> str:
    secreto = secreto or os.getenv("JWT_SECRET")
    if secreto:
        if len(secreto) < 32:
            raise ValueError("JWT_SECRET debe tener al menos 32 caracteres")
        return secreto
    logger.warning(
        "JWT_SECRET no está definido: se usa un secreto temporal y los tokens "
        "dejarán de valer al reiniciar el servidor."
    )
    return secrets.token_urlsafe(32)


def minutos_expiracion() -> int:
    return int(os.getenv("JWT_EXPIRE_MINUTES", EXPIRACION_POR_DEFECTO))


def crear_token(admin: Administrador, secreto: str, minutos: int) -> str:
    ahora = datetime.now(timezone.utc)
    payload = {
        "sub": admin.id,
        "email": admin.email,
        "rol": admin.rol,
        "iat": ahora,
        "exp": ahora + timedelta(minutes=minutos),
    }
    return jwt.encode(payload, secreto, algorithm=ALGORITMO)


def decodificar_token(token: str, secreto: str) -> dict:
    """Lanza jwt.InvalidTokenError si la firma no es válida o el token ha caducado."""
    return jwt.decode(
        token, secreto, algorithms=[ALGORITMO], options={"require": ["exp", "sub"]}
    )
