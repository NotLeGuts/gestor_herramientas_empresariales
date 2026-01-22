#!/usr/bin/env python
"""
Script para ejecutar automáticamente Streamlit con la aplicación Gestor de Herramientas.
Este script se utiliza como punto de entrada para el instalador.
"""

import subprocess
import sys
import os
import platform
import time


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
        "--browser.serverAddress=0.0.0.0",  # Cambiado a 0.0.0.0 para Render
        "--server.headless=true",  # Modo headless para producción
        "--server.enableCORS=false",
        "--server.enableXsrfProtection=false",
        "--server.enableWebsocketCompression=false",  # Deshabilitar compresión para evitar problemas
        "--global.developmentMode=false"  # Modo producción
    ]
    
    print(f"Comando a ejecutar: {' '.join(streamlit_args)}")
    print(f"Directorio actual: {os.getcwd()}")
    print(f"Archivos en directorio: {os.listdir('.')}")
    
    # Ejecutar Streamlit en segundo plano
    print("\n--- Iniciando Streamlit en segundo plano ---")
    try:
        # Ejecutar Streamlit en segundo plano
        streamlit_process = subprocess.Popen(
            streamlit_args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print(f"Streamlit proceso iniciado con PID: {streamlit_process.pid}")
        
        # Esperar un momento para que Streamlit inicie
        time.sleep(5)
        
        # Verificar si el puerto está abierto
        print("\n--- Verificando si el puerto 8501 está escuchando ---")
        import socket
        
        def is_port_open(port, host='0.0.0.0', timeout=5):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(timeout)
                result = sock.connect_ex((host, port))
                sock.close()
                return result == 0
            except Exception as e:
                print(f"Error al verificar puerto: {e}")
                return False
        
        if is_port_open(8501, '0.0.0.0'):
            print("✓ Puerto 8501 está abierto y escuchando!")
            print("Streamlit se está ejecutando correctamente.")
            
            # Mostrar salida de Streamlit
            print("\n--- Salida de Streamlit ---")
            time.sleep(2)  # Esperar un poco más para capturar salida
            
            # Leer salida del proceso
            stdout, stderr = streamlit_process.communicate(timeout=2)
            if stdout:
                print(f"Salida estándar:\n{stdout}")
            if stderr:
                print(f"Salida de error:\n{stderr}")
            
            # Mantener el proceso en ejecución
            print("\nStreamlit está en ejecución. Manteniendo el proceso activo...")
            streamlit_process.wait()
            sys.exit(0)
        else:
            print("✗ Puerto 8501 no está abierto")
            print("Streamlit podría no estar ejecutándose correctamente.")
            
            # Obtener salida de error
            stdout, stderr = streamlit_process.communicate(timeout=5)
            print(f"\nSalida estándar:\n{stdout}")
            print(f"\nSalida de error:\n{stderr}")
            
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
            
    except subprocess.CalledProcessError as e:
        print(f"\nError al ejecutar Streamlit:")
        print(f"  Código de salida: {e.returncode}")
        print(f"  Comando: {' '.join(streamlit_args)}")
        
        # Obtener salida de error
        print(f"\nSalida estándar:\n{e.stdout}")
        print(f"\nSalida de error:\n{e.stderr}")
        
        sys.exit(1)
    except Exception as e:
        print(f"\nError inesperado: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nStreamlit detenido por el usuario.")
        sys.exit(0)


if __name__ == "__main__":
    main()