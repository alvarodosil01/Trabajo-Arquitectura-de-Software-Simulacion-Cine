"""Adaptador entre el servicio del dominio y SQLAlchemy.

La primera versión carga el pequeño catálogo completo dentro de una transacción.
El bloqueo de SQLite se mantiene hasta guardar: dos compras no pueden validar la
misma butaca libre a la vez. No se mantiene una caché global del dominio.
"""

from sqlalchemy import delete, select

from app.models import (
    ButacaReservadaDB, ClienteDB, PeliculaDB, ReservaDB, SalaDB, SesionDB,
)
from cine.models.cliente import Cliente
from cine.models.pelicula import Pelicula
from cine.models.reserva import Reserva
from cine.models.sala import Sala
from cine.models.sesion import Sesion
from cine.services.cine_service import CineService


MAPPINGS = (
    ("salas", SalaDB, Sala),
    ("peliculas", PeliculaDB, Pelicula),
    ("clientes", ClienteDB, Cliente),
    ("sesiones", SesionDB, Sesion),
    ("reservas", ReservaDB, Reserva),
)


def load_service(db):
    service = CineService()
    for attribute, table, domain_class in MAPPINGS:
        rows = db.scalars(select(table)).all()
        if attribute == "salas" and not rows:
            continue  # Solo la primera ejecución crea las salas fijas.
        values = {}
        for row in rows:
            obj = domain_class.__new__(domain_class)
            for column in table.__table__.columns:
                setattr(obj, column.name, getattr(row, column.name))
            if attribute == "sesiones":
                obj.butacas_ocupadas = set()
            values[obj.email if attribute == "clientes" else obj.id] = obj
        setattr(service, attribute, values)
    for reserva in service.reservas.values():
        service.sesiones[reserva.sesion_id].ocupar_butacas(reserva.butacas_reservadas)
    return service


def save_service(db, service):
    # Primero elimina hijos; las reglas del servicio impiden borrar datos usados.
    for attribute, table, _ in reversed(MAPPINGS):
        ids = [obj.id for obj in getattr(service, attribute).values()]
        db.execute(delete(table).where(table.id.not_in(ids)))
    for attribute, table, _ in MAPPINGS:
        for obj in getattr(service, attribute).values():
            db.merge(table(**{
                column.name: getattr(obj, column.name)
                for column in table.__table__.columns
            }))
        db.flush()
    for reserva in service.reservas.values():
        for butaca in reserva.butacas_reservadas:
            db.merge(ButacaReservadaDB(
                sesion_id=reserva.sesion_id, butaca=butaca, reserva_id=reserva.id
            ))
    db.flush()
