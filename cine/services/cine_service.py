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
        self._cargar_salas() # esa _ es una convención, ya que es una función que se llama de forma interna
        
    def agregar_pelicula(self, peli: Pelicula) -> Pelicula:
        self.peliculas[peli.id] = peli
        return peli
    
    def _cargar_salas(self) -> None : 
        for numero, filas, columnas in SALAS_INICIALES : 
            sala = Sala(numero, filas, columnas) 
            self.salas[sala.id] = sala
    
    def crear_sesion(self, pelicula_id: str, sala_id: str, fecha: datetime, precio: float, ) -> Sesion : 
        if pelicula_id not in self.peliculas:
            raise ValueError("La película no existe")
        if sala_id not in self.salas:
            raise ValueError("La sala no existe")
        sesion = Sesion(pelicula_id, sala_id, fecha, precio)
        self.sesiones[sesion.id] = sesion
        return sesion
        