import uuid
from datetime import datetime

class Reserva: 
    def __init__(self, cliente_id: str, sesion_id: str, precio_total: float, butacas_reservadas: list[str]) -> None:
        self.id: str = str(uuid.uuid4())
        self.cliente_id: str = cliente_id
        self.sesion_id: str = sesion_id
        self.fecha_reserva: datetime = datetime.now()
        self.precio_total: float = precio_total
        self.butacas_reservadas: list[str] = butacas_reservadas
        
        