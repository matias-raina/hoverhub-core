# Verificación de Tipos

Este proyecto usa **mypy** para verificar que los tipos de Python sean correctos.

## Instalación

La herramienta ya está instalada en `requirements.txt`. Si necesitas instalarla:

```bash
source .venv/bin/activate
pip install mypy
```

## Uso

### Verificar tipos en todo el proyecto

```bash
mypy app/
```

### Verificar un archivo específico

```bash
mypy app/services/user.py
```

### Verificar solo los servicios

```bash
mypy app/services/
```

### Modo estricto (más detallado)

```bash
mypy --strict app/
```

## Configuración

La configuración está en `pyproject.toml` bajo `[tool.mypy]`.

## Errores comunes

- **Missing type annotation**: Falta anotación de tipo en una función
- **Incompatible types**: Los tipos no coinciden (ej: esperabas `str` pero recibiste `int`)
- **Union types**: Un valor puede ser de varios tipos (ej: `str | None`)

## Integración con Cursor/VS Code

1. Instala la extensión **Pylance** (ya viene con Python)
2. Los errores de tipo aparecerán automáticamente con subrayado rojo
3. Puedes ver los tipos al pasar el mouse sobre variables

## Antes de hacer commit

Es recomendable verificar tipos antes de hacer commit:

```bash
mypy app/
```

