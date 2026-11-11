"""Aplicación FastAPI; las rutas del cine se incorporarán en la siguiente fase."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from cine.services.cine_service import CineService


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.cine = CineService()
    yield


app = FastAPI(
    title="API del cine",
    description="Backend de películas, salas, sesiones, clientes y reservas.",
    lifespan=lifespan,
)
