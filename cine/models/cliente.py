import uuid

class Cliente : 
    def __init__(self, nombre: str, email: str) -> None:
        self.id: str = str(uuid.uuid4())
        self.nombre: str = nombre
        self.email: str = email
        
    def __str__(self) -> str:
        return f'El email de {self.nombre} es : {self.email}'