from models.pelicula import Pelicula
from models.sala import Sala

p = Pelicula("La Bola Negra", 150, "Drama")
print(p)


sala = Sala(1, 4, 3)
print(sala.aforo())
print(sala.butacas())