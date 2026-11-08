import uuid
from datetime import datetime

class Sesion :
    def __init__(self, pelicula_id: str, sala_id : str, fecha: datetime, precio: float, butacas_ocupadas: list[str] ):
        self.id: str = str(uuid.uuid4())
        self.pelicula_id: str = pelicula_id
        self.sala_id: str = sala_id
        self.fecha: datetime = fecha
        self.precio: int = precio
        self.butacas_ocupadas: list[str] = butacas_ocupadas
    
        