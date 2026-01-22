"""
Módulo principal para acceder a todas las operaciones CRUD del sistema.

Este módulo exporta todas las funciones disponibles para interactuar con la base de datos,
organizadas por entidad (empleados, herramientas, préstamos).

Ejemplo de uso:
    from app.crud import create_empleado, get_empleados, create_prestamo

    # Crear un empleado
    empleado = create_empleado(session, nombre="Juan", apellido="Perez", ...)

    # Obtener todos los empleados
    empleados = get_empleados(session)
"""

# Empleados
from .crud_empleado import (
    create_empleado,
    get_empleado_by_id,
    get_empleados,
    get_empleados_activos,
    get_empleados_por_area,
    update_empleado,
    inhabilitar_empleado,
    habilitar_empleado,
)

# Herramientas
from .crud_herramienta import (
    create_herramienta,
    get_herramienta_by_id,
    get_herramientas,
    get_herramientas_disponibles,
    get_herramientas_por_categoria,
    update_herramienta,
    inhabilitar_herramienta,
    habilitar_herramienta,
)

# Préstamos
from .crud_prestamo import (
    create_prestamo,
    get_prestamo_by_id,
    get_prestamos,
    get_prestamos_activos,
    get_prestamos_por_empleado,
    get_prestamos_por_herramienta,
    get_prestamos_vencidos,
    update_prestamo,
    devolver_prestamo,
    cancelar_prestamo,
)

# Documentación de la API
__all__ = [
    # Empleados
    'create_empleado',
    'get_empleado_by_id',
    'get_empleados',
    'get_empleados_activos',
    'get_empleados_por_area',
    'update_empleado',
    'inhabilitar_empleado',
    'habilitar_empleado',

    # Herramientas
    'create_herramienta',
    'get_herramienta_by_id',
    'get_herramientas',
    'get_herramientas_disponibles',
    'get_herramientas_por_categoria',
    'update_herramienta',
    'inhabilitar_herramienta',
    'habilitar_herramienta',

    # Préstamos
    'create_prestamo',
    'get_prestamo_by_id',
    'get_prestamos',
    'get_prestamos_activos',
    'get_prestamos_por_empleado',
    'get_prestamos_por_herramienta',
    'get_prestamos_vencidos',
    'update_prestamo',
    'devolver_prestamo',
    'cancelar_prestamo',
]