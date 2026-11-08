import uuid 

class Sala : 
    def __init__(self, numero : int, filas : int, columnas : int):
        self.id : str = str(uuid.uuid4())
        self.numero : int = numero
        self.filas : int = filas
        self.columnas : int = columnas

    def aforo(self) -> int : 
        return self.filas * self.columnas
    
    def butacas(self) -> int : 
        resultado: list[str] = []
        for f in range(self.filas) :
            for c in range(self.columnas) : 
                resultado.append(f'{chr(65 + f)}{c+1}') # devuelve la butaca en formato letra y número, para no liarse poniendo solo números. 
                                                        # después para mostrarlo al usuario se puede revertir y ya
        return resultado