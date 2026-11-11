"""Contratos de entrada y salida (Pydantic 2)."""

from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class Schema(BaseModel):
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True, extra="forbid")


class PeliculaInput(Schema):
    nombre: str = Field(min_length=1, max_length=200)
    duracion: int = Field(gt=0, le=1440, strict=True)
    genero: str = Field(min_length=1, max_length=100)


class PeliculaOutput(PeliculaInput):
    id: str


class SalaOutput(Schema):
    id: str
    numero: int
    filas: int
    columnas: int


class SesionInput(Schema):
    pelicula_id: str = Field(min_length=1)
    sala_id: str = Field(min_length=1)
    fecha: datetime
    precio: float = Field(gt=0, allow_inf_nan=False)

    @field_validator("fecha")
    @classmethod
    def fecha_local(cls, value):
        if value.tzinfo is not None:
            raise ValueError("Usa la hora local del cine sin zona: 2027-01-15T18:00:00")
        return value

    @field_validator("precio", mode="before")
    @classmethod
    def precio_valido(cls, value):
        if isinstance(value, bool):
            raise ValueError("El precio debe ser un número")
        return value

    @field_validator("precio")
    @classmethod
    def centimos(cls, value):
        if round(value, 2) != value:
            raise ValueError("El precio admite como máximo dos decimales")
        return value


class SesionOutput(SesionInput):
    id: str
    butacas_ocupadas: list[str]


class ReservaInput(Schema):
    sesion_id: str = Field(min_length=1)
    butacas: list[Annotated[str, Field(min_length=2, max_length=8)]] = Field(min_length=1)
    email: EmailStr
    nombre: str = Field(min_length=1, max_length=200)


class ReservaOutput(Schema):
    id: str
    cliente_id: str
    sesion_id: str
    fecha_reserva: datetime
    precio_total: float
    butacas_reservadas: list[str]


class DisponibilidadOutput(Schema):
    sesion_id: str
    disponibles: list[str]
    ocupadas: list[str]
