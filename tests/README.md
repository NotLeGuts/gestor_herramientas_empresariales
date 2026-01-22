# Tests para el proyecto Gestor de Herramientas

Este directorio contiene todos los tests del proyecto.

## Estructura

- `init_db_test.py` - Script para inicializar la base de datos con las tablas necesarias
- `test_empleado.py` - Tests para la gestión de empleados
- `test_herramienta.py` - Tests para la gestión de herramientas
- `test_prestamo.py` - Tests para la gestión de préstamos
- `test_stock_simple.py` - Test simple para verificar la lógica de stock
- `test_stock_prestamos.py` - Test para verificar la lógica de stock en préstamos

## Cómo ejecutar los tests

### 1. Inicializar la base de datos

Antes de ejecutar cualquier test, debe inicializar la base de datos:

```bash
python tests/init_db_test.py
```

### 2. Ejecutar tests individuales

Puede ejecutar cada test individualmente:

```bash
# Test simple de stock
python tests/test_stock_simple.py

# Test de préstamos
python tests/test_stock_prestamos.py

# Test de empleados
python tests/test_empleado.py

# Test de herramientas
python tests/test_herramienta.py

# Test de préstamos
python tests/test_prestamo.py
```

### 3. Ejecutar todos los tests

Para ejecutar todos los tests manualmente, puede usar los siguientes comandos:

```bash
# Borrar base de datos existente
rm -f gestor_herramientas.db

# Inicializar base de datos
python tests/init_db_test.py

# Ejecutar tests individualmente
echo "Ejecutando test_stock_simple.py..."
python tests/test_stock_simple.py

echo "Ejecutando test_empleado.py..."
python tests/test_empleado.py

echo "Ejecutando test_herramienta.py..."
python tests/test_herramienta.py

echo "Ejecutando test_prestamo.py..."
python tests/test_prestamo.py
```

## Notas importantes

- Los tests modifican la base de datos, por lo que es recomendable ejecutarlos en un entorno aislado
- Algunos tests pueden fallar si las tablas no están correctamente inicializadas
- El test `test_stock_prestamos.py` tiene problemas con las claves foráneas en SQLite, por lo que se recomienda usar `test_stock_simple.py` para verificar la lógica de stock
