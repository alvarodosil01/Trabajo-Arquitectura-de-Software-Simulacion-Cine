# Web Cine: Sistema de reservas de un cine

Proyecto final de Arquitectura del Software (UIE).

Autores: Álvaro Dosil, Xabier Girón, Helena Pérez, Pablo Ferro y Lucía Pardo.

Entrega: 11/12/2026, 14:59.

## Backend para la primera prueba

API REST con FastAPI, Pydantic 2 y SQLite mediante SQLAlchemy, basada en el ejemplo
`fast-api-uie-main` y en los modelos y reglas de nuestro `CineService`.
Esta versión no incluye autenticación JWT ni frontend. Las operaciones de gestión
están disponibles sin iniciar sesión para esta primera prueba local.

## Instalación y ejecución en Windows

Necesitas Python 3.12 o superior. Desde la raíz del proyecto, en PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend/requirements.txt
cd backend
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Si utilizas otra versión compatible, sustituye `py -3.12` por el comando de tu
instalación, por ejemplo `python`. No hace falta activar el entorno virtual.
Si el lanzador indica que no hay Python instalado, instala Python antes de empezar.

El entorno virtual existente se conserva en la raíz para no romper sus rutas y no
se sube a Git. Si ya está instalado, ejecuta solo los dos últimos comandos.
Si tenías el servidor abierto antes de mover las carpetas, detenlo con Ctrl+C
y arráncalo de nuevo desde backend/.

Abre **http://127.0.0.1:8000/docs**. En cada operación selecciona **Try it out**,
rellena los campos y pulsa **Execute**. Detén el servidor con `Ctrl+C`.

## Primera prueba manual

1. Ejecuta `GET /salas` y copia el `id` de una sala. Las tres salas fijas se crean
   automáticamente al iniciar por primera vez.
2. Ejecuta `POST /peliculas` con este cuerpo y copia el `id` devuelto:

```json
{
  "nombre": "La Bola Negra",
  "duracion": 120,
  "genero": "Comedia"
}
```

3. Ejecuta `POST /sesiones`, sustituyendo los identificadores. Elige una fecha
   futura en la hora local del cine, sin `Z` ni desplazamiento horario:

```json
{
  "pelicula_id": "ID_DE_LA_PELICULA",
  "sala_id": "ID_DE_LA_SALA",
  "fecha": "2027-01-15T18:00:00",
  "precio": 8.50
}
```

4. Copia el `id` de la sesión y ejecuta `POST /reservas`:

```json
{
  "sesion_id": "ID_DE_LA_SESION",
  "butacas": ["A1", "A2"],
  "email": "ana@example.com",
  "nombre": "Ana"
}
```

5. La reserva debe devolver un total de 17. Consulta
   `GET /sesiones/{sesion_id}/butacas` y `GET /reservas?email=ana@example.com`.
6. Si repites la compra de las mismas butacas, debes recibir `409`.
7. Reinicia el servidor: las salas, películas, sesiones y reservas deben conservarse.

### Comprobaciones realizadas

Se verificaron las 17 operaciones de la API mediante 49 comprobaciones de
respuestas HTTP, utilizando una base SQLite temporal independiente de los datos
locales. Se comprobaron las operaciones de creación, consulta, modificación y
borrado, las validaciones y los errores esperados.

También se verificó que dos compras simultáneas de la misma butaca producen una
reserva aceptada y otra rechazada, y que los datos y la ocupación se conservan
tras reiniciar el servidor. La comprobación de dependencias con `pip check`
no detectó incompatibilidades.

Estas fueron comprobaciones puntuales; no se incluye una suite de pruebas
automatizadas en el repositorio. Los pasos anteriores permiten repetir la prueba
manual desde Swagger.

## Endpoints

| Método | Ruta | Función |
|---|---|---|
| GET | `/` | Información y enlace a documentación |
| GET, POST | `/peliculas` | Listar y crear películas |
| GET, PUT, DELETE | `/peliculas/{pelicula_id}` | Consultar, sustituir datos y eliminar |
| GET | `/salas` | Listar salas fijas |
| GET | `/salas/{sala_id}` | Consultar una sala |
| GET, POST | `/sesiones` | Listar y crear sesiones |
| GET, PUT, DELETE | `/sesiones/{sesion_id}` | Consultar, sustituir datos y eliminar |
| GET | `/sesiones/{sesion_id}/butacas` | Butacas disponibles y ocupadas |
| POST | `/reservas` | Comprar una o varias butacas |
| GET | `/reservas?email=...` | Consultar las reservas de un cliente |
| GET | `/reservas/{reserva_id}` | Consultar una reserva |

`GET /sesiones` admite el filtro opcional `pelicula_id`. Los `PUT` requieren
los mismos campos que los `POST` correspondientes.

Respuestas: `201` al crear, `204` al borrar, `404` si el recurso no existe,
`409` ante conflictos, `422` para datos inválidos y `503` si SQLite no está disponible.

## Reglas de negocio y almacenamiento

- Salas fijas: sala 1 de 8 × 6, sala 2 de 6 × 7 y sala 3 de 10 × 5.
- Compra como invitado; se reutiliza el cliente por email normalizado a minúsculas.
- Las butacas se normalizan a mayúsculas; deben existir, estar libres y no repetirse.
- Una reserva incluye varias butacas. El total se redondea a dos decimales.
- Las sesiones deben ser futuras, con precio positivo de hasta dos decimales,
  y no pueden solaparse en la misma sala.
- No se reservan sesiones que ya han comenzado.
- No se elimina una película con sesiones ni se cambia su duración.
- No se modifica ni elimina una sesión con reservas.
- Las reservas y la ocupación se guardan en una única transacción. SQLite serializa
  las transacciones y una clave compuesta impide repetir una butaca en una sesión.

La base se crea en `backend/data/cine.db` y está excluida de Git. Puedes configurar otra
ruta SQLite con la variable `DATABASE_URL`, por ejemplo `sqlite:///data/prueba.db`.
Las fechas usan la hora local del servidor; configura el equipo con la hora del cine.

Para reutilizar la lógica original, el adaptador carga el catálogo completo en un
`CineService` por transacción. Es una implementación para la primera prueba con pocos
datos; para mayor volumen convendrá consultar únicamente los registros necesarios.
La demostración independiente `python -m cine.main`, desde `backend/`, sigue usando memoria y no modifica
la base de la API.

## Estructura

```text
backend/
  app/                 Aplicación FastAPI, endpoints, esquemas y persistencia
  cine/                Modelos y reglas de negocio del cine
  data/                Base SQLite local (ignorada por Git)
  requirements.txt     Dependencias con versiones fijadas
frontend/
  .gitkeep             Mantiene la carpeta en Git hasta crear la interfaz
README.md
.gitignore
```

Los endpoints están en `backend/app/main.py`. La carpeta `frontend/` está
preparada para desarrollar la interfaz más adelante.
