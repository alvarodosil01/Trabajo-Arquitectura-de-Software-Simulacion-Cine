from cine.models.pelicula import Pelicula
from cine.models.sala import Sala
from cine.models.sesion import Sesion
from cine.models.cliente import Cliente
from cine.models.reserva import Reserva
from datetime import datetime, timedelta
from cine.services.errors import ConflictError, NotFoundError

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
            raise NotFoundError("La película no existe")
        if sala_id not in self.salas:
            raise NotFoundError("La sala no existe")
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
                raise ConflictError("La sala ya tiene una sesión en ese horario")
        sesion = Sesion(pelicula_id, sala_id, fecha, precio)
        self.sesiones[sesion.id] = sesion
        return sesion
    
    def crear_reserva(self, sesion_id: str, butacas: list[str], email: str, nombre: str) -> Reserva : 
        
        # validar sesión
        
        if sesion_id not in self.sesiones : 
            raise NotFoundError('La sesión no existe')
        sesion = self.sesiones[sesion_id] 
        if sesion.fecha <= datetime.now():
            raise ConflictError('La sesión ya ha comenzado')
        email = email.strip().lower()
        nombre = nombre.strip()
        butacas = [b.strip().upper() for b in butacas]

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
                raise ConflictError(f'La butaca {b} está ocupada')
            
        # validar cliente : reutilizar o crear    
            
        if email not in self.clientes:
            self.clientes[email] = Cliente(nombre, email)
        cliente = self.clientes[email]
        
        # Crear reserva, ocupar butaca, guardar y devolver
        
        total = round(sesion.precio * len(butacas), 2)
        reserva = Reserva(cliente_id=cliente.id, sesion_id=sesion.id, precio_total=total, butacas_reservadas=butacas)
        sesion.ocupar_butacas(butacas)
        
        self.reservas[reserva.id] = reserva
        return reserva

    def obtener(self, coleccion: str, identificador: str):
        objeto = getattr(self, coleccion).get(identificador)
        if objeto is None:
            raise NotFoundError('No existe el recurso solicitado')
        return objeto

    def listar_sesiones(self, pelicula_id: str | None = None):
        return sorted(
            (s for s in self.sesiones.values()
             if pelicula_id is None or s.pelicula_id == pelicula_id),
            key=lambda s: s.fecha,
        )

    def butacas_disponibles(self, sesion_id: str):
        sesion = self.obtener('sesiones', sesion_id)
        return [b for b in self.salas[sesion.sala_id].butacas() if sesion.butaca_libre(b)]

    def listar_reservas_por_email(self, email: str):
        cliente = self.clientes.get(email.strip().lower())
        if cliente is None:
            return []
        return [r for r in self.reservas.values() if r.cliente_id == cliente.id]

    def actualizar_pelicula(self, pelicula_id: str, nombre: str, duracion: int, genero: str):
        pelicula = self.obtener('peliculas', pelicula_id)
        if duracion != pelicula.duracion and any(
            s.pelicula_id == pelicula_id for s in self.sesiones.values()
        ):
            raise ConflictError('No se puede cambiar la duración de una película con sesiones')
        pelicula.nombre, pelicula.duracion, pelicula.genero = nombre, duracion, genero
        return pelicula

    def eliminar_pelicula(self, pelicula_id: str):
        self.obtener('peliculas', pelicula_id)
        if any(s.pelicula_id == pelicula_id for s in self.sesiones.values()):
            raise ConflictError('No se puede eliminar una película con sesiones')
        del self.peliculas[pelicula_id]

    def eliminar_sesion(self, sesion_id: str):
        self.obtener('sesiones', sesion_id)
        if any(r.sesion_id == sesion_id for r in self.reservas.values()):
            raise ConflictError('No se puede eliminar una sesión con reservas')
        del self.sesiones[sesion_id]

    def actualizar_sesion(self, sesion_id: str, pelicula_id: str, sala_id: str,
                         fecha: datetime, precio: float):
        original = self.obtener('sesiones', sesion_id)
        if any(r.sesion_id == sesion_id for r in self.reservas.values()):
            raise ConflictError('No se puede modificar una sesión con reservas')
        del self.sesiones[sesion_id]
        try:
            nueva = self.crear_sesion(pelicula_id, sala_id, fecha, precio)
        except Exception:
            self.sesiones[sesion_id] = original
            raise
        del self.sesiones[nueva.id]
        nueva.id = sesion_id
        self.sesiones[sesion_id] = nueva
        return nueva
