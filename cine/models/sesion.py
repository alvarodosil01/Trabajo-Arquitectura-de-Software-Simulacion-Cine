import uuid
from datetime import datetime

class Sesion :
    def __init__(self, pelicula_id: str, sala_id : str, fecha: datetime, precio: float) -> None:
        self.id: str = str(uuid.uuid4())
        self.pelicula_id: str = pelicula_id
        self.sala_id: str = sala_id
        self.fecha: datetime = fecha
        self.precio: float = precio
        self.butacas_ocupadas: set[str] = set()
    
    # Aquí solo verificamos si una butaca está libre (True) u ocupada (False)
    # Esta es la forma más eficiente de hacerlo
    
    def butaca_libre(self, butaca: str) -> bool: 
        # if butaca in self.butacas_ocupadas: 
        #     return False
        # else :
        #     return True
        return butaca not in self.butacas_ocupadas 
    
    def ocupar_butacas(self, butacas: list[str]) -> None : 
        for b in butacas : 
            self.butacas_ocupadas.add(b)
    
    def __str__(self) -> str:
        ocupadas = ", ".join(sorted(self.butacas_ocupadas))
        return f"Sesión : {self.fecha} - {self.precio}€ - Ocupadas: {ocupadas}"
   
