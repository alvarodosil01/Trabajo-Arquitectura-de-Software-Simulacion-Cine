# Usuarios, roles y autenticación JWT

## Herencia de usuarios

```text
Usuario (abstracta: id, nombre, email, rol)
├── Cliente        rol "cliente"  compra como invitado, se identifica por email
└── Administrador  rol "admin"    gestiona películas y sesiones; tiene contraseña
```

- Las tres clases están en `backend/cine/models/usuario.py`, como en la Práctica 1.
  `Usuario` es una clase abstracta (`ABC`) y no se
  puede instanciar. Cada subclase implementa la propiedad `rol`.
- `Administrador` guarda solo `password_hash`, nunca la contraseña. Se usa scrypt de
  la biblioteca estándar con una sal aleatoria por contraseña
  (funciones `hash_password` y `verify_password` del mismo archivo).
- `CineService` añade `registrar_administrador`, `autenticar_administrador` y
  `obtener_administrador`. Los administradores se guardan en la tabla
  `administradores` de SQLite.

## Qué está protegido

| Acceso | Endpoints |
|---|---|
| Público | `GET` de películas, salas, sesiones y butacas; `POST /reservas`; consultas de reservas |
| Solo administrador (token JWT) | `POST`, `PUT` y `DELETE` de `/peliculas` y `/sesiones`; `POST /administradores`; `GET /auth/me` |

Respuestas: `401` sin token, con token manipulado, firmado con otro secreto o
caducado; `403` si el token es válido pero el rol no es `admin`.

## Flujo

1. `POST /auth/login` con un formulario `username` (el email) y `password`.
2. La API comprueba la contraseña contra el hash y devuelve un JWT firmado con
   HS256: `{"access_token": "...", "token_type": "bearer", "expires_in": 3600}`.
3. El cliente envía `Authorization: Bearer <token>` en cada petición de gestión.
4. La dependencia `get_admin_actual` (`backend/app/dependencies.py`) verifica la
   firma, la caducidad (`exp`), el rol y que el administrador siga existiendo.

El token incluye `sub` (id del administrador), `email`, `rol`, `iat` y `exp`. No
lleva datos sensibles: un JWT está firmado, pero no cifrado.

## Configuración

Las claves no están en el código; se leen de variables de entorno (ver
`backend/.env.example`):

| Variable | Uso |
|---|---|
| `JWT_SECRET` | Secreto de firma, mínimo 32 caracteres. Si falta, se genera uno temporal y los tokens dejan de valer al reiniciar. |
| `JWT_EXPIRE_MINUTES` | Validez del token (60 por defecto). |
| `ADMIN_EMAIL`, `ADMIN_PASSWORD`, `ADMIN_NOMBRE` | Crean el primer administrador al arrancar, solo si no existe. |

Ejemplo en PowerShell, desde `backend/`:

```powershell
$env:JWT_SECRET = python -c "import secrets; print(secrets.token_urlsafe(48))"
$env:ADMIN_EMAIL = "admin@example.com"
$env:ADMIN_PASSWORD = "elige-una-contraseña-larga"
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

En `http://127.0.0.1:8000/docs`, pulsa **Authorize**, escribe el email en
`username` y la contraseña. Swagger añadirá el token a las peticiones protegidas.
Después se pueden crear más administradores con `POST /administradores`.

## Pruebas automáticas

```powershell
cd backend
..\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
..\.venv\Scripts\python.exe -m pytest
```

Los tests usan una base SQLite temporal y cubren la herencia, el hash de
contraseñas, el login, los tokens manipulados, caducados o sin rol, el alta de
administradores y la persistencia tras reiniciar.

## Medidas de seguridad aplicadas

- Contraseñas con hash scrypt y sal; comparación en tiempo constante.
- El login no revela si un email existe: mismo error y tiempo de respuesta parecido.
- Tokens con caducidad y algoritmo fijado (`HS256`), así no se acepta `alg: none`.
- Secretos fuera del código, en variables de entorno.
- Mínimo privilegio: los clientes no necesitan cuenta y solo los administradores
  modifican la cartelera.

Pendiente para más adelante: limitar los intentos de login, configurar CORS
cuando exista el frontend y proteger `GET /reservas?email=`, que ahora
devuelve las reservas de cualquier email.
