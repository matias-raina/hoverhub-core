# Guía de Pruebas

## Requisitos Previos

Asegúrate de tener el entorno virtual activado:

```bash
source .venv/bin/activate
```

## Ejecutar Pruebas

### Ejecutar todas las pruebas

```bash
pytest tests/
```

### Ejecutar pruebas con salida detallada

```bash
pytest tests/ -v
```

### Ejecutar un archivo de prueba específico

```bash
pytest tests/test_auth.py
```

### Ejecutar una prueba específica

```bash
pytest tests/test_auth.py::TestSignup::test_signup_success
```

## Advertencias y Deprecaciones

### Mostrar todas las advertencias (por defecto)

```bash
pytest tests/ -v
```

Las advertencias se muestran por defecto en el resumen al final.

### Hacer que las advertencias fallen las pruebas

```bash
pytest tests/ -W error
```

Esto hará que la suite de pruebas falle si se encuentran advertencias.

### Mostrar solo advertencias de deprecación

```bash
pytest tests/ -W default::DeprecationWarning
```

### Mostrar todas las advertencias incluyendo las de dependencias

```bash
pytest tests/ -W default -W ignore::DeprecationWarning:fastapi
```

### Filtrar advertencias específicas

```bash
# Mostrar solo advertencias de deprecación de Pydantic
pytest tests/ -W default::pydantic

# Ignorar advertencias específicas
pytest tests/ -W ignore::DeprecationWarning:fastapi.status
```

### Mostrar advertencias como errores para categorías específicas

```bash
# Fallar en deprecaciones de Pydantic pero permitir otras
pytest tests/ -W error::DeprecationWarning:pydantic -W default
```

## Cobertura

### Instalar herramienta de cobertura (si no está instalada)

```bash
pip install pytest-cov
```

### Ejecutar pruebas con reporte de cobertura

```bash
pytest tests/ --cov=app --cov-report=term-missing
```

### Generar reporte de cobertura HTML

```bash
pytest tests/ --cov=app --cov-report=html
```

El reporte HTML se generará en `htmlcov/index.html`. Ábrelo en tu navegador para ver información detallada de cobertura.

### Ejecutar pruebas con reportes en terminal y HTML

```bash
pytest tests/ --cov=app --cov-report=term-missing --cov-report=html
```

## Estadísticas de Pruebas

- **Total de Pruebas**: 108
- **Cobertura**: 95%
- **Archivos de Prueba**: 7
  - `test_auth.py` - Endpoints de autenticación
  - `test_users.py` - Endpoints de usuarios
  - `test_jobs.py` - Endpoints de trabajos
  - `test_accounts.py` - Endpoints de cuentas
  - `test_applications.py` - Endpoints de aplicaciones
  - `test_favorites.py` - Endpoints de favoritos
  - `test_health.py` - Endpoint de estado de salud

## Opciones Comunes de Advertencias

| Opción                           | Descripción                                                 |
| -------------------------------- | ----------------------------------------------------------- |
| `-W default`                     | Mostrar todas las advertencias (comportamiento por defecto) |
| `-W error`                       | Tratar advertencias como errores (fallar pruebas)           |
| `-W ignore`                      | Ignorar todas las advertencias                              |
| `-W error::DeprecationWarning`   | Fallar solo en advertencias de deprecación                  |
| `-W default::DeprecationWarning` | Mostrar solo advertencias de deprecación                    |
