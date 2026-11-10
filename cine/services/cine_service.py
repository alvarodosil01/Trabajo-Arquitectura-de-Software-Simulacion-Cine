from models.pelicula import Pelicula
from models.sala import Sala
from models.sesion import Sesion
from models.cliente import Cliente
from models.reserva import Reserva
from datetime import datetime

class CineService : 
    def __init__(self) -> None :
        self.clientes: dict[str, Cliente] = {}  # clave : email, el resto usan el id como clave
        self.peliculas: dict[str, Pelicula]  = {}
        self.salas: dict[str, Sala] = {}
        self.sesiones: dict[str, Sesion] = {}
        self.reservas: dict[str, Reserva] = {}
        
    def agregar_pelicula(self, peli: Pelicula) -> Pelicula:
        return self.peliculas.update(peli)
        ... 

    

        