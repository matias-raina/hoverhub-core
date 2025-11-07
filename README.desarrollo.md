# Guía de Instalación y Configuración (Desarrollo)

Esta guía cubre la inicialización del stack, el arranque de la API en modo desarrollo y la gestión de migraciones con Alembic.

---

## Requisitos previos

- Docker y Docker Compose instalados

---

## Inicialización del stack

1. Levantar los servicios con Docker Compose:

   ```bash
   cd stack
   docker compose up -d
   ```

2. Verificar que los servicios estén corriendo:

   ```bash
   docker compose ps
   ```

---

## Inicialización de la API (desarrollo)

Ejecutar el servidor de desarrollo (recarga automática):

```powershell
fastapi dev app/main.py
```

Luego acceder a:

- API: <http://localhost:8000>
- Swagger UI: <http://localhost:8000/docs>
- ReDoc: <http://localhost:8000/redoc>

---

## Migraciones de base de datos (Alembic)

Generar una nueva migración (reemplaza el mensaje entre comillas):

```powershell
alembic revision --autogenerate -m "mensaje de migración"
```

Aplicar las migraciones pendientes:

```powershell
alembic upgrade head
```

Comprobar historial de migraciones:

```powershell
alembic history --verbose
```

Revertir la última migración (si fuera necesario):

```powershell
alembic downgrade -1
```
