from models.pelicula import Pelicula
from models.sala import Sala
from models.sesion import Sesion
from services.cine_service import CineService
from datetime import datetime

# pelicula = Pelicula("La Bola Negra", 150, "Drama")

# sala = Sala(1, 4, 3)
# print(sala.aforo())
# print(sala.butacas())

# sitio = Sesion(pelicula.id, sala.id, datetime(2026, 11, 8, 18, 30), 8.5)
# print(sitio.butaca_libre('A1'))

# sitio.butacas_ocupadas.append('A2')
# print(sitio.butaca_libre('A2'))

# s = Sesion("p1", "sala1", datetime(2026, 11, 14, 21, 0), 8.0)
# s.ocupar_butacas(["A5", "A6"])
# print(s)

# p = Pelicula("LQSA", 120, "Comedia")
# print(p.id)

# cine = CineService()
# p = cine.agregar_pelicula(Pelicula("La Bola Negra", 120, "Comedia"))
# print(cine.peliculas)

# cine = CineService()
# print(len(cine.salas))

# cine = CineService()
# un_id = list(cine.salas.keys())[0]   # coge la primera etiqueta que haya
# print(cine.salas[un_id].filas)

cine = CineService()
p = cine.agregar_pelicula(Pelicula("La Bola Negra", 120, "Comedia"))
sala_id = list(cine.salas.keys())[0]
sesion1 = cine.crear_sesion(p.id, sala_id, datetime(2026, 11, 14, 21, 0), 8.50)
# sesion1.ocupar_butacas('A2')
# print(sesion1)

# cine.crear_reserva(sesion1.id, ['A3', 'A3'], 'ana@mail.com', 'Ana')   # duplicadas
cine.crear_reserva(sesion1.id, [], 'ana@mail.com', 'Ana')             # vacía