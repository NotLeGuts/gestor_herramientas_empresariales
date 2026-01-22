"""
Funciones utilitarias para la aplicación Streamlit.

Este módulo contiene funciones de ayuda para formateo, validación y manipulación de datos.
"""

import streamlit as st
from datetime import datetime
import json
from pathlib import Path


def show_success(message):
    """Mostrar mensaje de éxito."""
    st.success(message)


def show_error(message):
    """Mostrar mensaje de error."""
    st.error(message)


def show_warning(message):
    """Mostrar mensaje de advertencia."""
    st.warning(message)


def show_info(message):
    """Mostrar mensaje informativo."""
    st.info(message)


def format_date(date):
    """Formatear fecha para display."""
    if date:
        return date.strftime("%d/%m/%Y %H:%M")
    return "N/A"


def format_date_short(date):
    """Formatear fecha corta para display."""
    if date:
        return date.strftime("%d/%m/%Y")
    return "N/A"


def confirm_action(action_name):
    """Confirmar acción con diálogo."""
    return st.button(f"Confirmar {action_name}")


def get_session():
    """Obtener sesión de base de datos."""
    from sqlmodel import Session
    from app.database.config import engine
    
    @st.cache_resource
    def _get_session():
        return Session(engine)
    
    return _get_session()


def validate_email(email):
    """Validar formato de correo electrónico."""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_required_fields(**fields):
    """Validar que todos los campos requeridos tengan valores."""
    for field_name, value in fields.items():
        if not value or str(value).strip() == "":
            return False, f"El campo {field_name} es requerido"
    return True, "Todos los campos son válidos"


def get_employee_name_by_id(employee_id, session):
    """Obtener nombre de empleado por ID."""
    from app.crud import get_empleado_by_id
    
    employee = get_empleado_by_id(session, employee_id)
    if employee:
        return f"{employee.nombre} {employee.apellido}"
    return "Empleado no encontrado"


def get_tool_name_by_id(tool_id, session):
    """Obtener nombre de herramienta por ID."""
    from app.crud import get_herramienta_by_id
    
    tool = get_herramienta_by_id(session, tool_id)
    if tool:
        return tool.nombre
    return "Herramienta no encontrada"


def format_currency(amount):
    """Formatear monto como moneda."""
    return f"${amount:,.2f}"


def get_status_badge(status):
    """Obtener badge de estado."""
    if status == "activo":
        return "🟢 Activo"
    elif status == "devuelto":
        return "🔵 Devuelto"
    elif status == "cancelado":
        return "🔴 Cancelado"
    else:
        return "⚪ " + status
