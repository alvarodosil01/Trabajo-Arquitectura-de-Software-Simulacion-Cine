"""Tablas de persistencia; los modelos del dominio permanecen en cine/models."""

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class PeliculaDB(Base):
    __tablename__ = "peliculas"
    id = Column(String, primary_key=True)
    nombre = Column(String, nullable=False)
    duracion = Column(Integer, nullable=False)
    genero = Column(String, nullable=False)


class SalaDB(Base):
    __tablename__ = "salas"
    id = Column(String, primary_key=True)
    numero = Column(Integer, nullable=False, unique=True)
    filas = Column(Integer, nullable=False)
    columnas = Column(Integer, nullable=False)


class ClienteDB(Base):
    __tablename__ = "clientes"
    id = Column(String, primary_key=True)
    nombre = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)


class SesionDB(Base):
    __tablename__ = "sesiones"
    id = Column(String, primary_key=True)
    pelicula_id = Column(ForeignKey("peliculas.id"), nullable=False)
    sala_id = Column(ForeignKey("salas.id"), nullable=False)
    fecha = Column(DateTime, nullable=False)
    precio = Column(Float, nullable=False)


class ReservaDB(Base):
    __tablename__ = "reservas"
    id = Column(String, primary_key=True)
    cliente_id = Column(ForeignKey("clientes.id"), nullable=False)
    sesion_id = Column(ForeignKey("sesiones.id"), nullable=False)
    fecha_reserva = Column(DateTime, nullable=False)
    precio_total = Column(Float, nullable=False)
    butacas_reservadas = Column(JSON, nullable=False)


class ButacaReservadaDB(Base):
    __tablename__ = "butacas_reservadas"
    sesion_id = Column(ForeignKey("sesiones.id"), primary_key=True)
    butaca = Column(String, primary_key=True)
    reserva_id = Column(ForeignKey("reservas.id"), nullable=False)
