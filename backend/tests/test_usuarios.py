"""Pruebas del dominio: herencia de usuarios y gestión de administradores."""

from datetime import datetime, timedelta

import pytest

from cine.models.usuario import Administrador, Cliente, Usuario
from cine.models.pelicula import Pelicula
from cine.services.cine_service import CineService
from cine.services.errors import ConflictError


def test_usuario_es_abstracto():
    with pytest.raises(TypeError):
        Usuario("Ana", "ana@mail.com")


def test_cliente_hereda_de_usuario():
    cliente = Cliente("Ana", "ana@mail.com")
    assert isinstance(cliente, Usuario)
    assert cliente.rol == "cliente"
    assert cliente.id and cliente.email == "ana@mail.com"


def test_administrador_hereda_de_usuario_y_no_guarda_la_contraseña():
    admin = Administrador("Gestor", "gestor@cine.com", "una-clave-larga")
    assert isinstance(admin, Usuario)
    assert admin.rol == "admin"
    assert "una-clave-larga" not in admin.password_hash
    assert admin.verificar_password("una-clave-larga")
    assert not admin.verificar_password("otra-clave")


def test_misma_contraseña_produce_hashes_distintos():
    a = Administrador("A", "a@cine.com", "misma-clave-123")
    b = Administrador("B", "b@cine.com", "misma-clave-123")
    assert a.password_hash != b.password_hash


def test_registrar_y_autenticar_administrador():
    cine = CineService()
    admin = cine.registrar_administrador("Gestor", " Gestor@Cine.com ", "clave-segura-1")
    assert admin.email == "gestor@cine.com"
    assert cine.autenticar_administrador("GESTOR@cine.com", "clave-segura-1") is admin
    assert cine.autenticar_administrador("gestor@cine.com", "incorrecta") is None
    assert cine.autenticar_administrador("nadie@cine.com", "clave-segura-1") is None
    assert cine.obtener_administrador(admin.id) is admin


def test_no_se_repite_el_email_de_administrador():
    cine = CineService()
    cine.registrar_administrador("Gestor", "gestor@cine.com", "clave-segura-1")
    with pytest.raises(ConflictError):
        cine.registrar_administrador("Otro", "gestor@cine.com", "clave-segura-2")


def test_contraseña_demasiado_corta():
    with pytest.raises(ValueError):
        CineService().registrar_administrador("Gestor", "gestor@cine.com", "corta")


def test_la_reserva_crea_un_cliente_que_es_usuario():
    cine = CineService()
    pelicula = cine.agregar_pelicula(Pelicula("Interstellar", 169, "Ciencia ficción"))
    sala_id = next(iter(cine.salas))
    sesion = cine.crear_sesion(pelicula.id, sala_id, datetime.now() + timedelta(days=1), 8.5)
    cine.crear_reserva(sesion.id, ["A1"], "ana@mail.com", "Ana")
    cliente = cine.clientes["ana@mail.com"]
    assert isinstance(cliente, Cliente) and isinstance(cliente, Usuario)
