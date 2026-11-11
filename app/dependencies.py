"""Dependencias compartidas por las futuras rutas HTTP."""

from fastapi import Request

from cine.services.cine_service import CineService


def get_cine_service(request: Request) -> CineService:
    """Reutiliza el servicio de la aplicación para conservar su estado en memoria."""
    return request.app.state.cine
