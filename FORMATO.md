# Formato de Código

Este proyecto usa **Ruff** para formatear y verificar el código Python.

## Instalación

Las herramientas ya están instaladas en `requirements.txt`. Si necesitas instalarlas:

```bash
source .venv/bin/activate
pip install ruff black
```

## Uso

### Formatear código

Formatear todos los archivos:
```bash
ruff format .
```

Formatear un archivo específico:
```bash
ruff format app/services/user.py
```

### Verificar y corregir errores

Verificar y corregir automáticamente:
```bash
ruff check --fix .
```

Solo verificar (sin corregir):
```bash
ruff check .
```

### Todo en uno

Formatear y corregir en un solo comando:
```bash
ruff format . && ruff check --fix .
```

## Configuración de Cursor/VS Code

El proyecto está configurado para formatear automáticamente al guardar. Solo necesitas:

1. Instalar la extensión **Ruff** en Cursor/VS Code
2. El código se formateará automáticamente al guardar (`Cmd+S` / `Ctrl+S`)

## Configuración

La configuración está en `pyproject.toml`:
- Longitud de línea: 100 caracteres
- Versión de Python: 3.11+

## Antes de hacer commit

Es recomendable formatear el código antes de hacer commit:

```bash
ruff format . && ruff check --fix .
```

