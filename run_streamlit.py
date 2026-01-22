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
    
    # Añadir el directorio del proyecto al PYTHONPATH para que los módulos puedan ser importados
    sys.path.insert(0, script_dir)
    
    # Verificar si existe el entorno virtual en varias ubicaciones comunes
    venv_locations = [
        os.path.join(script_dir, "env", "bin", "python"),
        os.path.join(script_dir, ".venv", "bin", "python"),
        os.path.join(script_dir, "venv", "bin", "python"),
    ]
    
    python_executable = sys.executable
    for venv_path in venv_locations:
        if os.path.exists(venv_path):
            # Usar el Python del entorno virtual
            python_executable = venv_path
            print(f"Usando Python del entorno virtual: {venv_path}")
            break
    
    print(f"Python ejecutable: {python_executable}")
    
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
        python_executable,
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
    
    print(f"Comando a ejecutar: {' '.join(streamlit_args)}")
    print(f"Directorio actual: {os.getcwd()}")
    print(f"Archivos en directorio: {os.listdir('.')}")
    
    # Ejecutar Streamlit
    try:
        result = subprocess.run(streamlit_args, check=True)
    except subprocess.CalledProcessError as e:
        print(f"\nError al ejecutar Streamlit:")
        print(f"  Código de salida: {e.returncode}")
        print(f"  Comando: {' '.join(streamlit_args)}")
        print(f"  Python: {python_executable}")
        print(f"  Existe Python: {os.path.exists(python_executable)}")
        
        # Intentar verificar si Streamlit está instalado
        try:
            check_streamlit = subprocess.run(
                [python_executable, "-c", "import streamlit; print('Streamlit OK')"],
                capture_output=True,
                text=True
            )
            print(f"  Verificación de Streamlit: {check_streamlit.stdout}")
            if check_streamlit.stderr:
                print(f"  Error en verificación: {check_streamlit.stderr}")
        except Exception as verify_error:
            print(f"  No se pudo verificar Streamlit: {verify_error}")
        
        # Intentar ejecutar Streamlit con capture_output para ver el error real
        print("\n--- Intentando obtener la salida de error completa ---")
        try:
            debug_run = subprocess.run(
                streamlit_args,
                capture_output=True,
                text=True,
                timeout=30
            )
            print(f"Salida estándar:\n{debug_run.stdout}")
            print(f"Salida de error:\n{debug_run.stderr}")
        except subprocess.TimeoutExpired:
            print("El comando se tiempo fuera al intentar obtener la salida de error")
        except Exception as debug_error:
            print(f"Error al intentar obtener salida de error: {debug_error}")
        
        # Verificar si el archivo Inicio.py existe y es válido
        print("\n--- Verificando archivo Inicio.py ---")
        if os.path.exists("frontend/Inicio.py"):
            print("✓ frontend/Inicio.py existe")
            try:
                with open("frontend/Inicio.py", "r") as f:
                    content = f.read()
                    print(f"✓ Tamaño del archivo: {len(content)} bytes")
                    # Verificar si hay errores sintácticos
                    compile(content, "frontend/Inicio.py", "exec")
                    print("✓ No hay errores de sintaxis")
            except SyntaxError as syntax_error:
                print(f"✗ Error de sintaxis: {syntax_error}")
            except Exception as file_error:
                print(f"✗ Error al leer archivo: {file_error}")
        else:
            print("✗ frontend/Inicio.py NO existe")
        
        # Verificar si los módulos personalizados existen
        print("\n--- Verificando módulos personalizados ---")
        modules_to_check = [
            "app.database.config",
            "app.crud",
            "app.models"
        ]
        
        for module in modules_to_check:
            try:
                __import__(module)
                print(f"✓ {module} se importó correctamente")
            except ImportError as import_error:
                print(f"✗ {module} NO se pudo importar: {import_error}")
            except Exception as module_error:
                print(f"✗ {module} generó error: {module_error}")
        
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nStreamlit detenido por el usuario.")
        sys.exit(0)


if __name__ == "__main__":
    main()