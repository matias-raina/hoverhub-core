# HoverHub

API REST para conectar clientes y proveedores de servicios con drones.

---

## Descripción

**HoverHub** es una plataforma que conecta a personas o empresas que ofrecen servicios con drones (filmación aérea, agricultura de precisión, relevamientos topográficos, inspecciones industriales, entre otros) con clientes que los necesitan.

La aplicación actúa como un intermediario digital que permite la publicación, búsqueda y contratación de servicios, facilitando el encuentro entre la oferta y la demanda dentro de un entorno confiable y especializado.

---

## Objetivo

Crear un sistema que simplifique la conexión entre clientes y proveedores de servicios con drones, ofreciendo una alternativa profesional frente a redes sociales o plataformas generalistas.

---

## Problema que resuelve

El mercado de servicios con drones se encuentra en expansión, con creciente demanda en sectores como la agricultura, construcción, eventos y logística. Sin embargo:

- No existe una plataforma especializada para este tipo de servicios.
- Los proveedores dependen de redes sociales o contactos informales.
- Los clientes tienen dificultades para comparar opciones y verificar la reputación de los oferentes.

**HoverHub** busca resolver esta brecha ofreciendo una plataforma específica, confiable y de fácil uso.

---

## Características implementadas

### Autenticación y usuarios

- Registro de usuarios (`/auth/signup`)
- Inicio de sesión (`/auth/signin`)
- Cierre de sesión (`/auth/signout`)
- Renovación de tokens (`/auth/refresh`)
- Gestión de sesiones activas
- Obtención del perfil del usuario autenticado

### Cuentas (Accounts)

- Creación de cuentas con tipos: `DRONER` (proveedor) y `EMPLOYER` (cliente)
- Gestión de múltiples cuentas por usuario
- Actualización de información de cuentas
- Listado de cuentas del usuario

### Trabajos (Jobs)

- Creación de trabajos con título, descripción, presupuesto, ubicación y fechas
- Listado de trabajos con paginación y filtros
- Búsqueda de trabajos por ubicación y palabra clave
- Obtención de detalle de trabajo
- Actualización de trabajos
- Eliminación de trabajos

### Aplicaciones (Applications)

- Postulación a trabajos por parte de droners
- Gestión de estado de aplicaciones (PENDING, ACCEPTED, REJECTED, WITHDRAWN)
- Listado de aplicaciones por trabajo (para empleadores)
- Listado de mis aplicaciones (para droners)
- Eliminación de aplicaciones

### Favoritos (Favorites)

- Guardar trabajos como favoritos
- Listado de trabajos favoritos
- Eliminación de favoritos

---

## Tecnologías

### Backend

- **Framework:** FastAPI
- **Lenguaje:** Python 3.11+
- **ORM:** SQLModel
- **Base de datos:** PostgreSQL 18
- **Cache:** Redis 8
- **Autenticación:** JWT (access tokens + refresh tokens)
- **Hashing de contraseñas:** Argon2 (via pwdlib)

### Herramientas de desarrollo

- **Migraciones:** Alembic
- **Testing:** pytest, pytest-asyncio, pytest-cov
- **Type checking:** mypy
- **Linting y formato:** ruff, black
- **Serialización JSON:** orjson

### Infraestructura

- **Contenedores:** Docker y Docker Compose
- **Control de versiones:** Git y GitHub

---

## Arquitectura

El proyecto sigue una **arquitectura en capas** con separación clara de responsabilidades:

```
app/
├── config/          # Configuración (settings, database, cache, dependencies)
├── domain/          # Capa de dominio
│   ├── models/      # Modelos de dominio (SQLModel)
│   └── repositories/ # Interfaces y implementaciones de repositorios
├── services/        # Lógica de negocio
├── routers/         # Endpoints de la API (FastAPI)
└── dto/             # Data Transfer Objects para validación
```

### Principios de diseño

- **Separación de responsabilidades:** cada capa tiene una función específica
- **Inversión de dependencias:** servicios dependen de interfaces, no de implementaciones
- **Inyección de dependencias:** uso de FastAPI dependencies para gestión de servicios
- **Type safety:** tipado estático con mypy

---

## Requisitos previos

- Python 3.11 o superior
- Docker y Docker Compose
- Git

---

## Instalación y configuración

### 1. Clonar el repositorio

```bash
git clone <repository-url>
cd hoverhub-core
```

### 2. Crear entorno virtual

```bash
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Crear un archivo `.env` en la raíz del proyecto:

```env
# Aplicación
ENVIRONMENT="development"
HOST="0.0.0.0"
PORT="8000"

# Base de datos
DB_CONNECTION_STRING="postgresql://postgres:hoverhub@localhost:5432/hoverhub"

# Redis
CACHE_CONNECTION_STRING="redis://localhost:6379"

# JWT
SECRET_KEY="3c5b3affe2b910d64e00ab92783c1bbf08b8976253e788ddbdf0d41f83540e4a"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES="15"
REFRESH_TOKEN_EXPIRE_MINUTES="1440"

```

### 5. Iniciar servicios con Docker

```bash
cd stack
docker compose up -d
```

Esto iniciará PostgreSQL y Redis en contenedores.

### 6. Aplicar migraciones

```bash
alembic upgrade head
```

### 7. Ejecutar la API

```bash
fastapi dev app/main.py
```

La API estará disponible en:

- **API:** http://localhost:8000
- **Documentación interactiva (Swagger):** http://localhost:8000/docs
- **Documentación alternativa (ReDoc):** http://localhost:8000/redoc
- **Health check:** http://localhost:8000/health

---

## Desarrollo

### Estructura del proyecto

- `app/` - Código fuente de la aplicación
- `tests/` - Pruebas unitarias e integración
- `migrations/` - Migraciones de base de datos (Alembic)
- `stack/` - Configuración de Docker Compose
- `docs/` - Documentación adicional

### Comandos útiles

#### Migraciones

```bash
# Crear nueva migración
alembic revision --autogenerate -m "descripción del cambio"

# Aplicar migraciones
alembic upgrade head

# Revertir última migración
alembic downgrade -1

# Ver historial
alembic history --verbose
```

#### Testing

```bash
# Ejecutar todas las pruebas
pytest tests/

# Con salida detallada
pytest tests/ -v

# Con cobertura
pytest tests/ --cov=app --cov-report=term-missing

# Generar reporte HTML de cobertura
pytest tests/ --cov=app --cov-report=html
```

#### Formato y linting

```bash
# Formatear código
ruff format .

# Verificar linting
ruff check .

# Type checking
mypy app/
```

---

## Endpoints principales

### Autenticación

- `POST /auth/signup` - Registro de usuario
- `POST /auth/signin` - Inicio de sesión
- `POST /auth/signout` - Cierre de sesión
- `POST /auth/refresh` - Renovación de token

### Usuarios

- `GET /users/me` - Obtener usuario autenticado
- `GET /users/sessions` - Listar sesiones activas

### Cuentas

- `POST /accounts/` - Crear cuenta
- `GET /accounts/` - Listar mis cuentas
- `GET /accounts/{account_id}` - Obtener cuenta
- `PUT /accounts/{account_id}` - Actualizar cuenta

### Trabajos

- `POST /jobs/` - Crear trabajo
- `GET /jobs/` - Listar trabajos (con filtros y paginación)
- `GET /jobs/{job_id}` - Obtener trabajo
- `PUT /jobs/{job_id}` - Actualizar trabajo
- `DELETE /jobs/{job_id}` - Eliminar trabajo

### Aplicaciones

- `POST /applications/jobs/{job_id}` - Aplicar a trabajo
- `GET /applications/jobs/{job_id}` - Listar aplicaciones de un trabajo
- `GET /applications/` - Listar mis aplicaciones
- `PATCH /applications/{application_id}` - Actualizar aplicación
- `DELETE /applications/{application_id}` - Eliminar aplicación

### Favoritos

- `POST /favorites/` - Agregar favorito
- `GET /favorites/` - Listar favoritos
- `DELETE /favorites/{favorite_id}` - Eliminar favorito

Para ver la documentación completa de la API, visita http://localhost:8000/docs cuando la aplicación esté corriendo.

---

## Testing

El proyecto cuenta con una suite de pruebas completa:

- **Total de pruebas:** 150+
- **Cobertura:** ~95%
- **Archivos de prueba:** 7 módulos principales

Las pruebas cubren:

- Endpoints de autenticación
- Gestión de usuarios
- CRUD de trabajos
- Gestión de cuentas
- Aplicaciones a trabajos
- Sistema de favoritos
- Health checks

---

## Requerimientos no funcionales

- **Escalabilidad:** arquitectura modular que permite agregar nuevas funcionalidades
- **Mantenibilidad:** código documentado, tipado y versionado con GitHub
- **Seguridad:** autenticación JWT, hashing seguro de contraseñas, validación de datos
- **Rendimiento:** uso de Redis para cache, consultas optimizadas con SQLModel
- **Calidad:** alta cobertura de pruebas, type checking, linting y formateo automático

---

## Estado del proyecto

### ✅ Implementado

- Sistema de autenticación completo (signup, signin, signout, refresh tokens)
- Gestión de usuarios y sesiones
- Sistema de cuentas (DRONER/EMPLOYER)
- CRUD completo de trabajos
- Sistema de aplicaciones a trabajos
- Sistema de favoritos
- Búsqueda y filtrado de trabajos
- Documentación automática de API (Swagger/ReDoc)
- Suite completa de pruebas

### 🚧 Pendiente

- Frontend (NextJS mencionado en especificación inicial)
- Sistema de notificaciones
- Chat interno entre usuarios
- Pasarela de pagos
- Sistema de reseñas y calificaciones
- Alertas de trabajos personalizadas

---

## Contribución

Este es un proyecto en desarrollo activo. Para contribuir:

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request
