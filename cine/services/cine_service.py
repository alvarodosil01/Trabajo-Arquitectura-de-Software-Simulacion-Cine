from models.pelicula import Pelicula
from models.sala import Sala
from models.sesion import Sesion
from models.pelicula import Pelicula

class CineService : 
    def __init__(self) -> None :
        self.clientes : dict[str, Cliente] = {}
        self.pelicula = {}
        self.sala = {}
        self.sesion = {}
        self.reserva = {}