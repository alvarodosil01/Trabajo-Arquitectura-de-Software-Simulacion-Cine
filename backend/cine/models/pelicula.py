import uuid

class Pelicula: 
    """Clase para cualquier película existente en cartelera"""
    def __init__(self, nombre: str, duracion : int, genero : str) -> None :
        self.id: str = str(uuid.uuid4())
        self.nombre: str = nombre
        self.duracion : int = duracion
        self.genero : str = genero
    
    def __str__(self) -> str :
        return f'La película {self.nombre} es del género {self.genero} y dura {self.duracion} minutos'