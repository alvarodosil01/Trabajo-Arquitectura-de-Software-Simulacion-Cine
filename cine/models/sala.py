import uuid 

class Sala : 
    def __init__(self, numero : int, filas : int, columnas : int):
        self.id : str = str(uuid.uuid4())
        self.numero : int = numero
        self.filas : int = filas
        self.columnas : int = columnas

    def aforo(filas : int, columnas : int) : 
        return filas * columnas
    