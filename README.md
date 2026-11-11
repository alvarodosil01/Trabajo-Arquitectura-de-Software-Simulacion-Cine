# Web Cine: Sistema de reservas de un cine

Proyecto final de la asignatura **Arquitectura del Software** (UIE).
Autores :
- Álvaro Dosil
- Xabier Girón 
- Helena Pérez
- Pablo Ferro
- Lucía Pardo

Fecha límite de entrega y presentación: **11/12/2026, 14:59**.

## 1. Descripción

Aplicación en Python para gestionar un cine: cartelera de películas, salas, sesiones y reservas de entradas con **elección de butaca**. El objetivo del proyecto es resolver un problema real del sector empresarial aplicando principios de ingeniería del software, Programación Orientada a Objetos, arquitectura orientada a microservicios (API REST con FastAPI), ciberseguridad (autenticación con tokens JWT) y contenerización con Docker.

### Decisiones de diseño principales

- **Los clientes no inician sesión. (en principio)** Compran como invitados: indican nombre y email al reservar.
- **Se guardan los datos del cliente** (nombre y email, usando el email como identificador) para poder usarlos en futuras promociones.
- **Las salas son fijas.** Se definen una sola vez al arrancar y no se gestionan desde la API.
- **Los objetos se relacionan por id**, no por referencia: una sesión guarda `pelicula_id` y `sala_id`; una reserva guarda `cliente_id` y `sesion_id`.
- **Las butacas ocupadas viven en la sesión**, no en la sala, porque la misma sala está libre u ocupada según la sesión.
- **Una reserva puede incluir varias butacas** (una compra = una reserva).
- **Los datos se guardan en memoria** (diccionarios). Al reiniciar la aplicación se pierden; una versión real usaría una base de datos.

## 2. Estructura del proyecto

```
cine/
├── models/
│   ├── cliente.py
│   ├── pelicula.py
│   ├── sala.py
│   ├── sesion.py
│   └── reserva.py
├── services/
│   └── cine_service.py
└── main.py
```

- `models/`: clases del dominio (solo datos y comportamiento propio).
- `services/`: lógica de negocio, centralizada en `CineService`.
- `main.py`: punto de entrada. Por ahora se usa para probar el servicio manualmente; más adelante expondrá la API.

## 3. Modelo de clases

Todas las clases generan su identificador con `uuid.uuid4()`.

| Clase | Atributos | Métodos |
|---|---|---|
| `Cliente` | `id`, `nombre`, `email` | `__str__` |
| `Pelicula` | `id`, `nombre`, `duracion` (min), `genero` | `__str__` |
| `Sala` | `id`, `numero`, `filas`, `columnas` | `aforo()`, `butacas()` (lista de textos tipo `"A1"`, `"B3"`) |
| `Sesion` | `id`, `pelicula_id`, `sala_id`, `fecha`, `precio`, `butacas_ocupadas` (set) | `butaca_libre(butaca)`, `ocupar_butacas(butacas)`, `__str__` |
| `Reserva` | `id`, `cliente_id`, `sesion_id`, `fecha_reserva`, `precio_total`, `butacas_reservadas` (lista) | n/a |

### Relaciones

```
Pelicula 1 ──── * Sesion * ──── 1 Sala
                    │
                    1
                    │
                    *
Cliente  1 ──── * Reserva
```

- Una película puede tener muchas sesiones.
- Una sala puede tener muchas sesiones (en distintos horarios).
- Una sesión puede tener muchas reservas.
- Un cliente puede tener muchas reservas.

## 4. Servicio de negocio: `CineService`

Clase que guarda el estado y aplica las reglas del negocio. No imprime ni conoce HTTP: ante un error lanza `ValueError`, y la API lo traducirá a un código HTTP.

### Datos (diccionarios en memoria)

| Atributo | Clave | Valor |
|---|---|---|
| `clientes` | email | `Cliente` |
| `peliculas` | id | `Pelicula` |
| `salas` | id | `Sala` |
| `sesiones` | id | `Sesion` |
| `reservas` | id | `Reserva` |

### Salas fijas (por ahora ejemplos)

La constante `SALAS_INICIALES` define las salas (número, filas, columnas) y el método interno `_cargar_salas()` las crea al instanciar el servicio:

| Sala | Filas | Columnas | Aforo |
|---|---|---|---|
| 1 | 8 | 6 | 48 |
| 2 | 6 | 7 | 42 |
| 3 | 10 | 5 | 50 |

### Métodos implementados

- **`agregar_pelicula(peli)`**: guarda la película por su id y la devuelve.
- **`crear_sesion(pelicula_id, sala_id, fecha, precio)`**: comprueba que la película y la sala existen (si no, `ValueError`), crea la sesión, la guarda y la devuelve.
- **`crear_reserva(sesion_id, butacas, email, nombre)`**: valida, en este orden y antes de modificar nada:
  1. que la sesión existe;
  2. que se ha elegido al menos una butaca;
  3. que no hay butacas duplicadas;
  4. que cada butaca existe en la sala y está libre.

  Después reutiliza o crea el cliente por email, calcula el total (`precio × nº de butacas`), ocupa las butacas en la sesión, guarda la reserva y la devuelve.

## 5. Requisitos y ejecución

- Python 3.12 o superior.
- Por ahora no hay dependencias externas (el fichero `requirements.txt` se añadirá con FastAPI y JWT).

Prueba manual del servicio desde `main.py`:

```python
from datetime import datetime
from models.pelicula import Pelicula
from services.cine_service import CineService

cine = CineService()
p = cine.agregar_pelicula(Pelicula("La Bola Negra", 120, "Comedia"))
sala_id = list(cine.salas.keys())[0]
sesion = cine.crear_sesion(p.id, sala_id, datetime(2026, 11, 14, 21, 0), 8.50)
reserva = cine.crear_reserva(sesion.id, ["A1", "A2"], "ana@mail.com", "Ana")
print(sesion)   # A1 y A2 aparecen como ocupadas
```

Ejecutar con `python main.py` desde la carpeta `cine`.

## 6. Estado del proyecto

### Hecho

- [x] Diseño de clases del dominio.
- [x] Modelos: `Cliente`, `Pelicula`, `Sala`, `Sesion`, `Reserva`.
- [x] Control de aforo y generación de butacas por sala.
- [x] `CineService`: estructura, carga de salas fijas, `agregar_pelicula`, `crear_sesion`, `crear_reserva` (con validaciones).
- [x] Pruebas manuales del flujo película → sesión → reserva.

### Pendiente

**Servicio**
- [ ] Métodos de consulta: `listar_peliculas`, `listar_salas`, `listar_sesiones` (con filtro opcional por película), `butacas_disponibles(sesion_id)` y `listar_reservas_por_email(email)`.
- [ ] `eliminar_pelicula` (decidir qué ocurre con sus sesiones).
- [ ] Opcional: normalizar mayúsculas en butacas y email.

**API REST (microservicios)**
- [ ] Esquemas Pydantic de entrada y salida.
- [ ] Endpoints con FastAPI en `main.py`: consulta de películas, salas y sesiones; butacas disponibles; creación de reservas; consulta de reservas de un cliente; gestión de películas y sesiones.
- [ ] Gestión de códigos HTTP (traducir los `ValueError` del servicio).
- [ ] Probar con `/docs`.

**Seguridad**
- [ ] Autenticación con tokens JWT (requisito del enunciado), prevista para las operaciones de administración.
- [ ] Contraseñas hasheadas y secretos en variables de entorno.

**Contenerización y entrega**
- [ ] `requirements.txt` con versiones fijadas.
- [ ] `Dockerfile` (imagen `python:3.12-slim`) y `.dockerignore`.
- [ ] Frontend web sencillo que consuma la API.
- [ ] Diagramas (clases, arquitectura) y presentación de 5 minutos (problema, diseño de la solución y programa desarrollado).
- [ ] Subida al repositorio de GitHub con ramas y Pull Request.

## 7. Entrega

Según el enunciado de la asignatura se entrega:

- Proyecto Python con el producto desarrollado.
- `requirements.txt`.
- `Dockerfile`.
- Presentación en `.ppt` o `.pdf` (máximo 5 minutos en la sesión 15).