"""Demostración manual del dominio: python -m cine.main desde la raíz."""

from datetime import datetime, timedelta

from cine.models.pelicula import Pelicula
from cine.services.cine_service import CineService


def main() -> None:
    cine = CineService()
    pelicula = cine.agregar_pelicula(Pelicula("La Bola Negra", 120, "Comedia"))
    sala_id = next(iter(cine.salas))
    sesion = cine.crear_sesion(
        pelicula.id, sala_id, datetime.now() + timedelta(days=1), 8.50
    )
    reserva = cine.crear_reserva(sesion.id, ["A1", "A2"], "ana@mail.com", "Ana")
    print(reserva.butacas_reservadas, reserva.precio_total)
    print(sesion)


if __name__ == "__main__":
    main()
