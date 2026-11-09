from models.pelicula import Pelicula
from models.sala import Sala
from models.sesion import Sesion
from datetime import datetime

# pelicula = Pelicula("La Bola Negra", 150, "Drama")

# sala = Sala(1, 4, 3)
# print(sala.aforo())
# print(sala.butacas())

# sitio = Sesion(pelicula.id, sala.id, datetime(2026, 11, 8, 18, 30), 8.5)
# print(sitio.butaca_libre('A1'))

# sitio.butacas_ocupadas.append('A2')
# print(sitio.butaca_libre('A2'))

s = Sesion("p1", "sala1", datetime(2026, 11, 14, 21, 0), 8.0)
s.ocupar_butacas(["A5", "A6"])
print(s)


