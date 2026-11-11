# Modelado del sistema de reservas del cine

Sección de **Modelado** de la propuesta (Proyecto, entrega 1). Incluye el diagrama
de casos de uso, el diagrama de clases y los diagramas de secuencia de los tres casos
de uso principales: **Registrar película**, **Programar sesión** y **Reservar butacas**.
Como apoyo se añade la secuencia de **Iniciar sesión**, de la que dependen las
operaciones del administrador.

Los diagramas están escritos en Mermaid, así que GitHub los muestra directamente en
este archivo. La versión para el documento está en `Modelado_cine.pdf`. Reflejan el
código con la herencia de usuarios y la autenticación JWT (`backend/cine` y
`backend/app`).

## 1. Diagrama de casos de uso

Hay dos actores. El **cliente invitado** compra sin registrarse y se identifica por
su email. El **administrador** gestiona la cartelera y la programación, y para ello
debe iniciar sesión y obtener un token JWT. Las relaciones `include` indican pasos
que siempre forman parte de otro caso de uso.

```mermaid
flowchart LR
    cliente["👤 Cliente invitado"]
    admin["👤 Administrador"]

    subgraph sistema["Sistema de reservas del cine (API REST)"]
        direction TB
        uc1(["Consultar cartelera"])
        uc2(["Consultar sesiones de una película"])
        uc3(["Ver butacas disponibles"])
        uc4(["Reservar butacas"])
        uc5(["Consultar mis reservas"])
        uc6(["Iniciar sesión (token JWT)"])
        uc7(["Registrar película"])
        uc8(["Modificar o eliminar película"])
        uc9(["Programar sesión"])
        uc10(["Modificar o eliminar sesión"])
        uc11(["Dar de alta administrador"])
    end

    cliente --- uc1
    cliente --- uc2
    cliente --- uc3
    cliente --- uc4
    cliente --- uc5

    admin --- uc6
    admin --- uc7
    admin --- uc8
    admin --- uc9
    admin --- uc10
    admin --- uc11

    uc4 -. "«include»" .-> uc3
    uc7 -. "«include»" .-> uc6
    uc8 -. "«include»" .-> uc6
    uc9 -. "«include»" .-> uc6
    uc10 -. "«include»" .-> uc6
    uc11 -. "«include»" .-> uc6
```

## 2. Diagrama de clases

- **Generalización (herencia):** `Cliente` y `Administrador` heredan de la clase
  abstracta `Usuario` (`cine/models/usuario.py`). Cada subclase implementa la
  propiedad abstracta `rol`. Los errores del dominio `NotFoundError` y
  `ConflictError` heredan de `ValueError`; la API los traduce a 404 y 409.
- **Agregación:** `CineService` agrupa las colecciones de películas, salas,
  sesiones, clientes, administradores y reservas. Las partes existen por sí mismas
  (se guardan en la base de datos) y el servicio solo las reúne para aplicar las
  reglas.
- **Asociaciones con multiplicidad:** una película se proyecta en `0..*` sesiones,
  una sala alberga `0..*` sesiones, una sesión tiene `0..*` reservas y un cliente
  realiza `0..*` reservas. En el código se guardan como identificadores (`*_id`).
- `Administrador` guarda solo el hash de la contraseña (`password_hash`, con
  scrypt y sal), nunca la contraseña en claro.

```mermaid
classDiagram
    direction TB

    class Usuario {
        <<abstract>>
        +id: str
        +nombre: str
        +email: str
        +rol: str*
    }
    class Cliente {
        +rol: str = "cliente"
    }
    class Administrador {
        +password_hash: str
        +rol: str = "admin"
        +verificar_password(password) bool
    }
    Usuario <|-- Cliente
    Usuario <|-- Administrador

    class Pelicula {
        +id: str
        +nombre: str
        +duracion: int
        +genero: str
    }
    class Sala {
        +id: str
        +numero: int
        +filas: int
        +columnas: int
        +aforo() int
        +butacas() list~str~
    }
    class Sesion {
        +id: str
        +pelicula_id: str
        +sala_id: str
        +fecha: datetime
        +precio: float
        +butacas_ocupadas: set~str~
        +butaca_libre(butaca) bool
        +ocupar_butacas(butacas) None
    }
    class Reserva {
        +id: str
        +cliente_id: str
        +sesion_id: str
        +fecha_reserva: datetime
        +precio_total: float
        +butacas_reservadas: list~str~
    }

    class CineService {
        +clientes: dict
        +administradores: dict
        +peliculas: dict
        +salas: dict
        +sesiones: dict
        +reservas: dict
        +PASSWORD_MINIMA: int = 8
        -_cargar_salas() None
        +agregar_pelicula(peli) Pelicula
        +actualizar_pelicula(pelicula_id, nombre, duracion, genero) Pelicula
        +eliminar_pelicula(pelicula_id) None
        +crear_sesion(pelicula_id, sala_id, fecha, precio) Sesion
        +listar_sesiones(pelicula_id) list~Sesion~
        +actualizar_sesion(sesion_id, pelicula_id, sala_id, fecha, precio) Sesion
        +eliminar_sesion(sesion_id) None
        +butacas_disponibles(sesion_id) list~str~
        +crear_reserva(sesion_id, butacas, email, nombre) Reserva
        +listar_reservas_por_email(email) list~Reserva~
        +registrar_administrador(nombre, email, password) Administrador
        +autenticar_administrador(email, password) Administrador o None
        +obtener_administrador(admin_id) Administrador o None
        +obtener(coleccion, identificador) object
    }

    class ValueError
    class NotFoundError
    class ConflictError
    ValueError <|-- NotFoundError
    ValueError <|-- ConflictError

    CineService o-- "0..*" Pelicula
    CineService o-- "3" Sala
    CineService o-- "0..*" Sesion
    CineService o-- "0..*" Cliente
    CineService o-- "0..*" Administrador
    CineService o-- "0..*" Reserva

    Pelicula "1" -- "0..*" Sesion : se proyecta en
    Sala "1" -- "0..*" Sesion : alberga
    Sesion "1" -- "0..*" Reserva : tiene
    Cliente "1" -- "0..*" Reserva : realiza

    CineService ..> NotFoundError : lanza
    CineService ..> ConflictError : lanza
```

En `Usuario`, el atributo `rol` aparece en cursiva: en UML la cursiva indica un
miembro abstracto, que `Usuario` declara y cada subclase implementa con su valor.

## 3. Diagramas de secuencia

Siguen el recorrido real de una petición: el cliente HTTP llama a la API (FastAPI),
la dependencia `get_cine_service` carga el `CineService` desde SQLite en una
transacción, el servicio aplica las reglas y, si todo va bien, la transacción se
guarda. En las operaciones de gestión, la dependencia `get_admin_actual` comprueba
antes el token JWT. Los recuadros `alt` muestran el camino de éxito y los de error.
El tiempo avanza de arriba abajo.

### 3.1 Registrar película

```mermaid
sequenceDiagram
    autonumber
    actor A as Administrador
    participant API as API FastAPI
    participant DB as get_cine_service / SQLite
    participant S as cine: CineService
    participant P as p: Pelicula

    A->>API: POST /peliculas {nombre, duracion, genero} + Bearer token
    API->>DB: abrir transacción
    DB->>S: load_service(db)
    API->>API: get_admin_actual: verificar firma, caducidad y rol del JWT
    API->>S: obtener_administrador(sub)
    alt token ausente, no válido o caducado, o administrador inexistente
        API-->>A: 401 Unauthorized
    else el rol del token no es admin
        API-->>A: 403 Forbidden
    else administrador autenticado
        API->>API: validar PeliculaInput (Pydantic)
        alt datos no válidos (duración <= 0, nombre vacío...)
            API-->>A: 422 Unprocessable Entity
        else datos válidos
            API->>P: Pelicula(nombre, duracion, genero)
            P-->>API: p (id = uuid4)
            API->>S: agregar_pelicula(p)
            S-->>API: p
            API->>DB: save_service(db, cine) y commit
            API-->>A: 201 Created + PeliculaOutput
        end
    end
```

### 3.2 Programar sesión

```mermaid
sequenceDiagram
    autonumber
    actor A as Administrador
    participant API as API FastAPI
    participant DB as get_cine_service / SQLite
    participant S as cine: CineService
    participant SE as nueva: Sesion

    A->>API: POST /sesiones {pelicula_id, sala_id, fecha, precio} + Bearer token
    API->>DB: abrir transacción
    DB->>S: load_service(db)
    API->>API: get_admin_actual: verificar JWT y rol admin
    alt token no válido
        API-->>A: 401 o 403
    else administrador autenticado
        API->>API: validar SesionInput (precio > 0, máx. 2 decimales)
        API->>S: crear_sesion(pelicula_id, sala_id, fecha, precio)
        alt película o sala inexistente
            S-->>API: NotFoundError
            API-->>A: 404 Not Found
        else fecha pasada o precio no válido
            S-->>API: ValueError
            API-->>A: 422 Unprocessable Entity
        else datos correctos
            loop para cada sesión existente en la misma sala
                S->>S: comprobar solape [fecha, fecha + duración)
            end
            alt se solapa con otra sesión
                S-->>API: ConflictError
                API-->>A: 409 Conflict
            else horario libre
                S->>SE: Sesion(pelicula_id, sala_id, fecha, precio)
                SE-->>S: nueva
                S-->>API: nueva
                API->>DB: save_service(db, cine) y commit
                API-->>A: 201 Created + SesionOutput
            end
        end
    end
```

### 3.3 Reservar butacas

Es una operación pública: el cliente invitado no necesita token.

```mermaid
sequenceDiagram
    autonumber
    actor C as Cliente invitado
    participant API as API FastAPI
    participant DB as get_cine_service / SQLite
    participant S as cine: CineService
    participant SE as sesion: Sesion
    participant SA as sala: Sala
    participant R as reserva: Reserva

    C->>API: POST /reservas {sesion_id, butacas, email, nombre}
    API->>API: validar ReservaInput (email válido, al menos 1 butaca)
    API->>DB: abrir transacción (BEGIN IMMEDIATE)
    DB->>S: load_service(db)
    API->>S: crear_reserva(sesion_id, butacas, email, nombre)
    alt la sesión no existe
        S-->>API: NotFoundError
        API-->>C: 404 Not Found
    else la sesión ya ha comenzado
        S-->>API: ConflictError
        API-->>C: 409 Conflict
    else sesión válida
        S->>S: normalizar email y butacas, rechazar duplicadas
        S->>SA: butacas()
        SA-->>S: butacas válidas de la sala
        loop para cada butaca b
            S->>SE: butaca_libre(b)
            SE-->>S: libre u ocupada
        end
        alt alguna butaca no existe
            S-->>API: ValueError
            API-->>C: 422 Unprocessable Entity
        else alguna butaca está ocupada
            S-->>API: ConflictError
            API-->>C: 409 Conflict
        else todas existen y están libres
            S->>S: reutilizar o crear Cliente(nombre, email) por email
            S->>R: Reserva(cliente_id, sesion_id, total, butacas)
            S->>SE: ocupar_butacas(butacas)
            S-->>API: reserva
            API->>DB: save_service(db, cine) y commit
            API-->>C: 201 Created + ReservaOutput
        end
    end
```

### 3.4 Iniciar sesión (apoyo)

```mermaid
sequenceDiagram
    autonumber
    actor A as Administrador
    participant API as API FastAPI
    participant DB as get_cine_service / SQLite
    participant S as cine: CineService
    participant AD as admin: Administrador
    participant SEC as security

    A->>API: POST /auth/login (username = email, password)
    API->>DB: abrir transacción
    DB->>S: load_service(db)
    API->>S: autenticar_administrador(email, password)
    alt el email no existe
        S->>S: calcular un hash ficticio (mismo tiempo de respuesta)
        S-->>API: None
        API-->>A: 401 Email o contraseña incorrectos
    else el email existe
        S->>AD: verificar_password(password)
        AD-->>S: True o False
        alt contraseña incorrecta
            S-->>API: None
            API-->>A: 401 Email o contraseña incorrectos
        else contraseña correcta
            S-->>API: admin
            API->>SEC: crear_token(admin, JWT_SECRET, minutos)
            SEC-->>API: JWT firmado (sub, email, rol, iat, exp)
            API-->>A: 200 OK {access_token, token_type, expires_in}
        end
    end
```
