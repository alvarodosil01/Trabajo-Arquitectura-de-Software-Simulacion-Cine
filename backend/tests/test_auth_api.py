"""Pruebas de la API: login JWT y protección de los endpoints de gestión."""

import sqlite3
from datetime import datetime, timedelta

import jwt
from fastapi.testclient import TestClient

from app.main import create_app
from app.security import crear_token
from cine.models.usuario import Administrador
from tests.conftest import ADMIN_EMAIL, ADMIN_PASSWORD, SECRETO, login

PELICULA = {"nombre": "La Bola Negra", "duracion": 120, "genero": "Comedia"}


def test_consultas_publicas_sin_token(client):
    assert client.get("/peliculas").status_code == 200
    assert client.get("/salas").status_code == 200
    assert client.get("/sesiones").status_code == 200


def test_gestion_sin_token_da_401(client):
    respuesta = client.post("/peliculas", json=PELICULA)
    assert respuesta.status_code == 401
    assert respuesta.headers["www-authenticate"] == "Bearer"
    assert client.delete("/peliculas/x").status_code == 401
    assert client.post("/sesiones", json={}).status_code == 401


def test_login_incorrecto_da_401(client):
    assert login(client, password="incorrecta").status_code == 401
    assert login(client, email="nadie@example.com").status_code == 401


def test_login_devuelve_un_jwt_valido(client):
    respuesta = login(client)
    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert datos["token_type"] == "bearer"
    payload = jwt.decode(datos["access_token"], SECRETO, algorithms=["HS256"])
    assert payload["email"] == ADMIN_EMAIL and payload["rol"] == "admin"


def test_auth_me(client, auth):
    respuesta = client.get("/auth/me", headers=auth)
    assert respuesta.status_code == 200
    assert respuesta.json()["email"] == ADMIN_EMAIL
    assert respuesta.json()["rol"] == "admin"


def test_flujo_completo_admin_y_cliente(client, auth):
    pelicula = client.post("/peliculas", json=PELICULA, headers=auth)
    assert pelicula.status_code == 201
    sala_id = client.get("/salas").json()[0]["id"]
    fecha = (datetime.now() + timedelta(days=5)).replace(microsecond=0).isoformat()
    sesion = client.post("/sesiones", headers=auth, json={
        "pelicula_id": pelicula.json()["id"], "sala_id": sala_id,
        "fecha": fecha, "precio": 8.5,
    })
    assert sesion.status_code == 201
    # La compra sigue siendo pública: el cliente no necesita token
    reserva = client.post("/reservas", json={
        "sesion_id": sesion.json()["id"], "butacas": ["A1", "A2"],
        "email": "ana@example.com", "nombre": "Ana",
    })
    assert reserva.status_code == 201
    assert reserva.json()["precio_total"] == 17


def test_token_manipulado_o_de_otro_secreto_da_401(client, auth):
    token = auth["Authorization"].removeprefix("Bearer ")
    manipulado = token[:-2] + ("AA" if not token.endswith("AA") else "BB")
    assert client.get("/auth/me", headers={"Authorization": f"Bearer {manipulado}"}).status_code == 401
    ajeno = jwt.encode({"sub": "x", "rol": "admin", "exp": datetime.now().timestamp() + 60},
                       "otro-secreto-distinto-de-32-caracteres-o-mas", algorithm="HS256")
    assert client.get("/auth/me", headers={"Authorization": f"Bearer {ajeno}"}).status_code == 401


def test_token_caducado_da_401(client):
    admin = Administrador("X", ADMIN_EMAIL, "da-igual-123")
    caducado = crear_token(admin, SECRETO, minutos=-1)
    assert client.get("/auth/me", headers={"Authorization": f"Bearer {caducado}"}).status_code == 401


def test_token_sin_rol_admin_da_403(client):
    token = jwt.encode({"sub": "x", "rol": "cliente", "exp": datetime.now().timestamp() + 60},
                       SECRETO, algorithm="HS256")
    respuesta = client.post("/peliculas", json=PELICULA, headers={"Authorization": f"Bearer {token}"})
    assert respuesta.status_code == 403


def test_alta_de_otro_administrador(client, auth):
    nuevo = {"nombre": "Lucía", "email": "lucia@example.com", "password": "otra-clave-segura"}
    assert client.post("/administradores", json=nuevo).status_code == 401
    respuesta = client.post("/administradores", json=nuevo, headers=auth)
    assert respuesta.status_code == 201
    assert "password" not in respuesta.json() and "password_hash" not in respuesta.json()
    assert login(client, "lucia@example.com", "otra-clave-segura").status_code == 200
    assert client.post("/administradores", json=nuevo, headers=auth).status_code == 409


def test_contraseña_guardada_como_hash_y_persistente(db_url, monkeypatch, client):
    ruta = db_url.removeprefix("sqlite:///")
    with sqlite3.connect(ruta) as conexion:
        (guardado,) = conexion.execute(
            "SELECT password_hash FROM administradores WHERE email = ?", (ADMIN_EMAIL,)
        ).fetchone()
    assert guardado.startswith("scrypt$") and ADMIN_PASSWORD not in guardado
    # Tras "reiniciar" sin variables de entorno, el administrador sigue existiendo
    monkeypatch.delenv("ADMIN_EMAIL")
    monkeypatch.delenv("ADMIN_PASSWORD")
    with TestClient(create_app(db_url, jwt_secret=SECRETO)) as reiniciado:
        assert login(reiniciado).status_code == 200
