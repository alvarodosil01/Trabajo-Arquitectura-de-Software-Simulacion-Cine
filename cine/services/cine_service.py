from models.pelicula import Pelicula
from models.sala import Sala
from models.sesion import Sesion
from models.cliente import Cliente
from models.reserva import Reserva
from datetime import datetime

SALAS_INICIALES: list[tuple[int, int, int]] = [ # las salas son fijas. no tiene sentido cambiarlas
    (1,8,6),        # nº de sala, filas, columnas
    (2,6,7), 
    (3,10,5)
]

class CineService : 
    def __init__(self) -> None :
        self.clientes: dict[str, Cliente] = {}  # clave : email, el resto usan el id como clave
        self.peliculas: dict[str, Pelicula]  = {}
        self.salas: dict[str, Sala] = {}
        self.sesiones: dict[str, Sesion] = {}
        self.reservas: dict[str, Reserva] = {}
        self.cargar_salas()
        
    def agregar_pelicula(self, peli: Pelicula) -> Pelicula:
        self.peliculas[peli.id] = peli
        return peli
    
    def cargar_salas(self) -> None : 
        for n, c, f in SALAS_INICIALES : 
            sala = Sala(n,c,f) 
            self.salas[sala.id] = sala
    