import pytest
from fastapi.testclient import TestClient

from app.main import create_app

SECRETO = "secreto-de-pruebas-con-mas-de-32-caracteres"
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "contraseña-segura-1"


@pytest.fixture
def db_url(tmp_path):
    # Base SQLite temporal: no toca backend/data/cine.db
    return f"sqlite:///{(tmp_path / 'cine_test.db').as_posix()}"


@pytest.fixture
def client(db_url, monkeypatch):
    monkeypatch.setenv("ADMIN_EMAIL", ADMIN_EMAIL)
    monkeypatch.setenv("ADMIN_PASSWORD", ADMIN_PASSWORD)
    with TestClient(create_app(db_url, jwt_secret=SECRETO)) as test_client:
        yield test_client


def login(client, email=ADMIN_EMAIL, password=ADMIN_PASSWORD):
    return client.post("/auth/login", data={"username": email, "password": password})


@pytest.fixture
def auth(client):
    token = login(client).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
