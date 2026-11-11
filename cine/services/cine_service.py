from cine.models.pelicula import Pelicula
from cine.models.sala import Sala
from cine.models.sesion import Sesion
from cine.models.cliente import Cliente
from cine.models.reserva import Reserva
from datetime import datetime, timedelta

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
        if not isinstance(fecha, datetime) or fecha <= datetime.now():
            raise ValueError("La fecha de la sesión debe ser futura")
        if isinstance(precio, bool) or not isinstance(precio, (int, float)) or not 0 < precio < float('inf'):
            raise ValueError("El precio debe ser positivo y finito")
        nueva_fin = fecha + timedelta(minutes=self.peliculas[pelicula_id].duracion)
        for existente in self.sesiones.values():
            if existente.sala_id != sala_id:
                continue
            fin_existente = existente.fecha + timedelta(
                minutes=self.peliculas[existente.pelicula_id].duracion
            )
            if fecha < fin_existente and existente.fecha < nueva_fin:
                raise ValueError("La sala ya tiene una sesión en ese horario")
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
