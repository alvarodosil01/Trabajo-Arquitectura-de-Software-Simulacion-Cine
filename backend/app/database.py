"""SQLite local, configurable con DATABASE_URL."""

import os
from pathlib import Path

from sqlalchemy import create_engine, event

from app.models import Base


def create_database_engine(url: str | None = None):
    default_path = Path(__file__).resolve().parent.parent / "data" / "cine.db"
    url = url or os.getenv("DATABASE_URL") or f"sqlite:///{default_path.as_posix()}"
    if not url.startswith("sqlite:///"):
        raise ValueError("Esta primera versión utiliza SQLite (sqlite:///...).")
    filename = url.removeprefix("sqlite:///")
    if filename != ":memory:":
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(url, connect_args={"check_same_thread": False, "timeout": 30})

    @event.listens_for(engine, "connect")
    def configure_sqlite(connection, _):
        connection.isolation_level = None
        connection.execute("PRAGMA foreign_keys=ON")

    @event.listens_for(engine, "begin")
    def begin_transaction(connection):
        # Serializa la lectura-validación-escritura incluso entre varios procesos.
        connection.exec_driver_sql("BEGIN IMMEDIATE")

    return engine


def initialize_database(engine):
    from sqlalchemy.orm import Session
    from app.crud import load_service, save_service

    Base.metadata.create_all(engine)
    with Session(engine) as db, db.begin():
        save_service(db, load_service(db))


def crear_admin_inicial(engine, email: str | None, password: str | None,
                        nombre: str = "Administrador") -> bool:
    """Crea el primer administrador a partir de ADMIN_EMAIL y ADMIN_PASSWORD.

    Así ninguna contraseña queda escrita en el código. Si el administrador ya
    existe no se modifica. Devuelve True si se ha creado.
    """
    from sqlalchemy.orm import Session
    from app.crud import load_service, save_service

    if not email or not password:
        return False
    with Session(engine) as db, db.begin():
        service = load_service(db)
        if email.strip().lower() in service.administradores:
            return False
        service.registrar_administrador(nombre, email, password)
        save_service(db, service)
    return True
