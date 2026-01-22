#!/usr/bin/env python
"""
Script simplificado para ejecutar Streamlit en Render.

Este script está optimizado para ejecutarse en Render, donde el entorno
es diferente al desarrollo local.

Uso recomendado para Render:
1. Configurar el comando de inicio en Render como:
   python run_streamlit_render.py

2. Asegurarse de que las variables de entorno estén configuradas:
   - DATABASE_URL: URL de la base de datos
   - STREAMLIT_SERVER_PORT: Puerto para Streamlit (default: 8501)
   - STREAMLIT_SERVER_ADDRESS: Dirección para Streamlit (default: 0.0.0.0)
"""

import os
import sys
import time
from pathlib import Path


def main():
    """Ejecuta Streamlit con configuración optimizada para Render."""
    
    # Obtener el directorio del proyecto
    project_dir = Path(__file__).parent.absolute()
    os.chdir(project_dir)
    
    # Añadir el directorio del proyecto al PYTHONPATH
    sys.path.insert(0, str(project_dir))
    
    # Configurar variables de entorno por defecto si no están definidas
    if not os.getenv("DATABASE_URL"):
        os.environ["DATABASE_URL"] = "sqlite:///gestor_herramientas.db"
    
    if not os.getenv("STREAMLIT_SERVER_PORT"):
        os.environ["STREAMLIT_SERVER_PORT"] = "8501"
    
    if not os.getenv("STREAMLIT_SERVER_ADDRESS"):
        os.environ["STREAMLIT_SERVER_ADDRESS"] = "0.0.0.0"
    
    # Verificar que el archivo de inicio existe
    if not os.path.exists("frontend/Inicio.py"):
        print("Error: No se encontró frontend/Inicio.py", file=sys.stderr)
        sys.exit(1)
    
    # Verificar que Streamlit está instalado
    try:
        import streamlit
    except ImportError:
        print("Error: Streamlit no está instalado", file=sys.stderr)
        sys.exit(1)
    
    # Verificar que los módulos personalizados pueden importarse
    try:
        from app.database.config import engine
        from app.crud import get_empleados, get_herramientas, get_prestamos_activos
        print("✓ Módulos personalizados cargados correctamente")
    except Exception as e:
        print(f"Error al cargar módulos: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Mostrar información de configuración
    print(f"Directorio del proyecto: {project_dir}")
    print(f"Base de datos: {os.getenv('DATABASE_URL')}")
    print(f"Puerto: {os.getenv('STREAMLIT_SERVER_PORT')}")
    print(f"Dirección: {os.getenv('STREAMLIT_SERVER_ADDRESS')}")
    
    # Iniciar Streamlit directamente
    # Usamos sys.argv para pasar los argumentos directamente a Streamlit
    # Esto evita problemas con subprocess y es más compatible con Render
    sys.argv = [
        "streamlit",
        "run",
        "frontend/Inicio.py",
        "--server.port",
        os.getenv("STREAMLIT_SERVER_PORT", "8501"),
        "--server.address",
        os.getenv("STREAMLIT_SERVER_ADDRESS", "0.0.0.0"),
        "--global.developmentMode",
        "false",
        "--browser.serverAddress",
        "0.0.0.0",
    ]
    
    # Importar y ejecutar Streamlit
    try:
        import streamlit.web.cli as stcli
        stcli.main()
    except Exception as e:
        print(f"Error al ejecutar Streamlit: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
