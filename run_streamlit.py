#!/usr/bin/env python
"""
Script para ejecutar automáticamente Streamlit con la aplicación Gestor de Herramientas.
Este script se utiliza como punto de entrada para el instalador.
"""

import subprocess
import sys
import os
import platform


def main():
    """Ejecuta Streamlit con la aplicación Gestor de Herramientas."""
    
    # Obtener el directorio donde se encuentra este script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Cambiar al directorio del proyecto
    os.chdir(script_dir)
    
    # Verificar que estamos en el directorio correcto
    if not os.path.exists("frontend/Inicio.py"):
        print("Error: No se encontró el archivo frontend/Inicio.py")
        print(f"Directorio actual: {os.getcwd()}")
        sys.exit(1)
    
    # Verificar que Streamlit está instalado
    try:
        import streamlit
    except ImportError:
        print("Error: Streamlit no está instalado.")
        print("Por favor, instálalo con: pip install streamlit")
        sys.exit(1)
    
    # Verificar que Python tiene los permisos necesarios
    if platform.system() == "Windows":
        # En Windows, asegurarse de que el script se ejecute con los permisos correctos
        pass
    
    # Ejecutar Streamlit
    print("Iniciando Gestor de Herramientas...")
    print("Abrir en el navegador: http://localhost:8501")
    
    # Construir la lista de argumentos para Streamlit
    streamlit_args = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        "frontend/Inicio.py",
        "--server.port=8501",
        "--server.address=0.0.0.0",
        "--browser.serverAddress=localhost",
        "--server.headless=false",
        "--server.enableCORS=false",
        "--server.enableXsrfProtection=false"
    ]
    
    # Ejecutar Streamlit
    try:
        subprocess.run(streamlit_args, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar Streamlit: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nStreamlit detenido por el usuario.")
        sys.exit(0)


if __name__ == "__main__":
    main()