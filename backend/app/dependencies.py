"""Dependencias compartidas por las futuras rutas HTTP."""

from fastapi import Request
from sqlalchemy.orm import Session

from app.crud import load_service, save_service


def get_cine_service(request: Request):
    """Carga, valida y guarda en una sola transacción; revierte ante errores."""
    with Session(request.app.state.engine) as db, db.begin():
        service = load_service(db)
        yield service
        if request.method not in {"GET", "HEAD", "OPTIONS"}:
            save_service(db, service)
