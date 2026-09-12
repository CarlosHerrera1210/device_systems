# device_systems API

Evidencia **GA1-220501096-01-AA1-EV09 - FastAPI con SQLAlchemy: Persistencia de Datos y CRUD sobre Base de Datos**.

`device_systems` es una aplicacion backend creada con FastAPI para administrar usuarios mediante una API REST conectada a SQLite con SQLAlchemy. Esta version deja de usar listas en memoria y aplica persistencia real, modelos ORM, schemas Pydantic v2, validaciones, constraints, operaciones CRUD completas y documentacion Swagger/OpenAPI.

## Tecnologias utilizadas

- Python 3.13
- FastAPI
- Uvicorn
- SQLAlchemy
- SQLite
- Pydantic v2
- email-validator
- pytest
- TestClient con httpx

## Estructura del proyecto

```text
device_systems/
|-- app/
|   |-- __init__.py
|   |-- main.py
|   |-- database/
|   |   |-- __init__.py
|   |   `-- connection.py
|   |-- dependencies/
|   |   |-- __init__.py
|   |   |-- database_dependency.py
|   |   `-- user_dependencies.py
|   |-- models/
|   |   |-- __init__.py
|   |   `-- user_model.py
|   |-- routes/
|   |   |-- __init__.py
|   |   `-- user_routes.py
|   |-- schemas/
|   |   |-- __init__.py
|   |   `-- user_schema.py
|   `-- services/
|       |-- __init__.py
|       `-- user_service.py
|-- images/
|   |-- ev09_sqlalchemy_database.svg
|   `-- ev09_crud_endpoints.svg
|-- tests/
|   `-- test_users_api.py
|-- .gitignore
|-- pytest.ini
|-- requirements.txt
`-- README.md
```

## Instalacion

Crear y activar el entorno virtual:

```bash
python -m venv .venv
.\.venv\Scripts\activate
```

Instalar dependencias:

```bash
pip install -r requirements.txt
```

Dependencias principales:

- `fastapi`
- `uvicorn`
- `sqlalchemy`
- `pydantic[email]`
- `pytest`
- `httpx`

## Ejecucion del servidor

```bash
uvicorn app.main:app --reload
```

La API queda disponible en:

- API: `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

Al iniciar el servidor, SQLAlchemy crea la base de datos local:

```text
device_systems.db
```

## Configuracion de SQLAlchemy

La conexion se define en `app/database/connection.py`:

```python
DATABASE_URL = "sqlite:///./device_systems.db"
```

Elementos principales:

- `engine`: administra la conexion con SQLite.
- `SessionLocal`: crea sesiones de base de datos.
- `Base`: clase base para declarar modelos SQLAlchemy.
- `create_tables()`: crea las tablas al iniciar FastAPI.

La dependencia `get_db()` vive en `app/dependencies/database_dependency.py` y entrega una sesion de base de datos a cada endpoint usando `Depends()`.

## Modelo SQLAlchemy User

El modelo `User` esta en `app/models/user_model.py` y representa la tabla `users`.

| Campo | Tipo | Restriccion |
|---|---|---|
| `id` | Integer | Primary key e indice |
| `name` | String | Obligatorio |
| `email` | String | Unico, obligatorio e indexado |
| `role` | String | Obligatorio y limitado a `admin`, `support` o `user` |
| `is_active` | Boolean | Por defecto `True` |
| `created_at` | DateTime | Fecha automatica de creacion |

## Schemas Pydantic

Los schemas viven en `app/schemas/user_schema.py`.

- `UserCreate`: valida la creacion de usuarios.
- `UserUpdate`: valida actualizacion completa con `PUT`.
- `UserPatch`: valida actualizacion parcial con `PATCH`.
- `UserResponse`: controla la respuesta enviada al cliente.
- `UserListResponse`: estandariza el listado con `total` y `users`.

Validaciones:

- `name`: obligatorio, minimo 3 caracteres.
- `email`: formato valido.
- `role`: solo permite `admin`, `support` o `user`.
- `is_active`: valor booleano.

El modelo SQLAlchemy también aplica el constraint `ck_users_role_allowed`, que impide
guardar directamente en SQLite un rol diferente de `admin`, `support` o `user`.

## Diferencia entre modelo y schema

El modelo SQLAlchemy describe la tabla real de la base de datos: columnas, tipos, indices y restricciones. Se usa para guardar, consultar, actualizar y eliminar registros.

El schema Pydantic describe los datos que entran y salen por la API. Se usa para validar peticiones, controlar respuestas y generar documentacion clara en Swagger.

## Endpoints

| Metodo | Endpoint | Descripcion |
|---|---|---|
| GET | `/` | Verifica el estado de la API |
| GET | `/users` | Lista usuarios desde la base de datos |
| GET | `/users/{user_id}` | Consulta un usuario por ID |
| GET | `/users?role=admin` | Filtra usuarios por rol |
| GET | `/users?is_active=true` | Filtra usuarios activos o inactivos |
| GET | `/users?order_by=name` | Ordena usuarios por nombre |
| POST | `/users` | Crea un usuario |
| PUT | `/users/{user_id}` | Actualiza completamente un usuario |
| PATCH | `/users/{user_id}` | Actualiza parcialmente un usuario |
| DELETE | `/users/{user_id}` | Elimina un usuario |

## Ejemplos de peticiones

Listar usuarios:

```bash
curl http://127.0.0.1:8000/users
```

Buscar usuario por ID:

```bash
curl http://127.0.0.1:8000/users/1
```

Filtrar por rol:

```bash
curl "http://127.0.0.1:8000/users?role=admin"
```

Filtrar por estado:

```bash
curl "http://127.0.0.1:8000/users?is_active=true"
```

Crear usuario:

```bash
curl -X POST http://127.0.0.1:8000/users ^
  -H "Content-Type: application/json" ^
  -d "{\"name\":\"Maria Lopez\",\"email\":\"maria@example.com\",\"role\":\"user\",\"is_active\":true}"
```

Actualizar usuario completo:

```bash
curl -X PUT http://127.0.0.1:8000/users/1 ^
  -H "Content-Type: application/json" ^
  -d "{\"name\":\"Carlos Actualizado\",\"email\":\"carlos.actualizado@example.com\",\"role\":\"support\",\"is_active\":false}"
```

Actualizar usuario parcial:

```bash
curl -X PATCH http://127.0.0.1:8000/users/1 ^
  -H "Content-Type: application/json" ^
  -d "{\"role\":\"support\"}"
```

Eliminar usuario:

```bash
curl -X DELETE http://127.0.0.1:8000/users/1
```

## Codigos HTTP

| Caso | Codigo |
|---|---|
| Usuario creado | `201 Created` |
| Consulta correcta | `200 OK` |
| Actualizacion correcta | `200 OK` |
| Eliminacion correcta | `204 No Content` |
| Usuario no encontrado | `404 Not Found` |
| Email duplicado | `400 Bad Request` |
| Error de validacion | `422 Unprocessable Entity` |

## Cabeceras HTTP personalizadas

Los endpoints retornan:

```text
X-App-Name: device_systems
X-API-Version: 3.0.0
```

## Pruebas automatizadas

El proyecto incluye pruebas con `pytest` y `TestClient` para verificar CRUD, persistencia entre sesiones, filtros, cabeceras, validaciones, errores y documentacion OpenAPI.

```bash
pytest -q
```

Resultado validado:

```text
21 passed
```

## Evidencias

### Persistencia con SQLAlchemy

![Persistencia con SQLAlchemy](images/ev09_sqlalchemy_database.svg)

### CRUD completo

![CRUD completo](images/ev09_crud_endpoints.svg)

## Evidencias sugeridas para capturas reales

Para completar la entrega visual, toma capturas de:

- Estructura del proyecto en VS Code.
- Archivo `device_systems.db` generado.
- Swagger UI en `http://127.0.0.1:8000/docs`.
- Pruebas de `GET /users`, `GET /users/{user_id}`, `POST /users`, `PUT`, `PATCH` y `DELETE`.
- Error `400` por email duplicado.
- Error `404` por usuario inexistente.
- Error `422` por datos invalidos.

## Reflexion final

Usar persistencia en una API es importante porque los datos dejan de depender de la memoria del programa y permanecen disponibles aunque el servidor se reinicie. SQLAlchemy permite trabajar con la base de datos desde Python usando modelos claros, consultas ordenadas y operaciones CRUD mantenibles. FastAPI y Pydantic complementan esa persistencia con validaciones automaticas, documentacion Swagger y respuestas estructuradas para construir servicios backend mas profesionales.

