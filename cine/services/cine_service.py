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
    
    def crear_sesion(self, pelicula_id: str, sala_id: str, fecha: datetime, precio: float) -> Sesion : 
        if pelicula_id not in self.peliculas:
            raise ValueError("La película no existe")
        if sala_id not in self.salas:
            raise ValueError("La sala no existe")
        sesion = Sesion(pelicula_id, sala_id, fecha, precio)
        self.sesiones[sesion.id] = sesion
        return sesion
    
    def crear_reserva(self, sesion_id: str, butacas: list[str], email: str, nombre: str) -> Reserva : 
        
        # validar sesión
        
        if sesion_id not in self.sesiones : 
            raise ValueError('La Sesión no existe')
        sesion = self.sesiones[sesion_id] 

        # validar butacas
        
        if not butacas: # por si no se escoge ninguna butaca
            raise ValueError('Debes elegir al menos 1 butaca') 
        if len(butacas) != len(set(butacas)): # por si se escoge más de 1 vez la misma butaca
            raise ValueError('Hay butacas duplicadas') 
        
        butaca_valida = self.salas[sesion.sala_id].butacas()
        for b in butacas : 
            if b not in butaca_valida : 
                raise ValueError(f'La butaca {b} no existe')
            if not sesion.butaca_libre(b) : 
                raise ValueError(f'La butaca {b} está ocupada')
            
        # validar cliente : reutilizar o crear    
            
        if email not in self.clientes:
            self.clientes[email] = Cliente(nombre, email)
        cliente = self.clientes[email]
        
        # Crear reserva, ocupar butaca, guardar y devolver
        
        total = sesion.precio*len(butacas) 
        reserva = Reserva(cliente_id=cliente.id, sesion_id=sesion.id, precio_total=total, butacas_reservadas=butacas)
        sesion.ocupar_butacas(butacas)
        
        self.reservas[reserva.id] = reserva
        return reserva
        
    def listar_peliculas(self) -> list[Pelicula] : 
        return list(self.peliculas.values())
    
    def listar_salas(self) -> list[Sala] : 
        return list(self.salas.values())

    def listar_sesiones(self) -> list[Sesion] : 
        return list(self.sesiones.values())

    def listar_reservas(self) -> list[Reserva] : 
        return list(self.reservas.values())

    def butacas_disponibles(self, sesion_id) -> list[str] :
        if sesion_id not in self.sesiones:
            raise ValueError('Esta sesión no existe')
        sesion = self.sesiones[sesion_id]
        sala = self.salas[sesion.sala_id]
        todas = sala.butacas()
        return [b for b in todas if b not in sesion.butacas_ocupadas]
    
    def reservas_por_email(self, email) :
        if email not in self.clientes[email] : 
            return []
        cliente = self.clientes[email]
        return [r for r in self.reservas.values() if r.cliente_id == cliente.id]
    
    
    # MÉTODO ELIMINAR PELÍCULA