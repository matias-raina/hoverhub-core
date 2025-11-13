# Guía de Desarrollo

Esta guía cubre la configuración del entorno de desarrollo, el arranque de la API y la gestión de migraciones.

## Requisitos previos

- Docker y Docker Compose instalados

## Inicialización del stack

Levantar los servicios:

```bash
cd stack
docker compose up -d
```

Verificar que los servicios estén corriendo:

```bash
docker compose ps
```

## Inicialización de la API

Ejecutar el servidor de desarrollo:

```bash
fastapi dev app/main.py
```

Acceder a:

- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Migraciones de base de datos

Generar una nueva migración:

```bash
alembic revision --autogenerate -m "mensaje de migración"
```

Aplicar migraciones pendientes:

```bash
alembic upgrade head
```

Ver historial de migraciones:

```bash
alembic history --verbose
```

Revertir la última migración:

```bash
alembic downgrade -1
```
