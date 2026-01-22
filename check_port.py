#!/usr/bin/env python
"""
Script para verificar si el puerto 8501 está escuchando.
Este script se ejecuta después de iniciar Streamlit para confirmar que el servidor está funcionando.
"""

import socket
import time
import sys
import subprocess


def is_port_open(port, host='0.0.0.0', timeout=5):
    """Verificar si un puerto está abierto."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception as e:
        print(f"Error al verificar puerto: {e}")
        return False


def main():
    """Verificar si Streamlit está escuchando en el puerto 8501."""
    
    print("Esperando a que Streamlit inicie...")
    
    # Esperar hasta 60 segundos por el puerto
    max_attempts = 60
    for attempt in range(max_attempts):
        if is_port_open(8501, '0.0.0.0'):
            print(f"✓ Puerto 8501 está abierto y escuchando!")
            print("Streamlit se está ejecutando correctamente.")
            return 0
        
        time.sleep(1)
    
    print(f"✗ Puerto 8501 no se abrió después de {max_attempts} segundos")
    print("Streamlit podría no estar ejecutándose correctamente.")
    
    # Intentar obtener procesos activos
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        print("\nProcesos activos:")
        for line in result.stdout.split('\n'):
            if 'streamlit' in line.lower() or 'python' in line.lower():
                print(line)
    except Exception as e:
        print(f"No se pudo obtener lista de procesos: {e}")
    
    return 1


if __name__ == "__main__":
    sys.exit(main())
