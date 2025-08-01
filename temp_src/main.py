#!/usr/bin/env python3
"""
Punto de entrada principal para DotaTwin v3.0.

Este archivo actúa como el launcher principal de la aplicación,
configurando el entorno y iniciando la interfaz gráfica.
"""

import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path para imports
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

def setup_environment():
    """
    Configura el entorno de ejecución de la aplicación.
    """
    # Verificar versión de Python
    if sys.version_info < (3, 7):
        print("Error: Se requiere Python 3.7 o superior")
        sys.exit(1)
    
    # Verificar dependencias críticas
    try:
        import tkinter
        # Pillow es opcional para avatares - sin él funciona igual
        try:
            from PIL import Image, ImageTk
        except ImportError:
            print("Nota: Pillow no disponible - los avatares de Steam no se mostrarán")
    except ImportError as e:
        print(f"Error: Dependencia crítica faltante - {e}")
        print("Error: tkinter no está disponible. Verifica tu instalación de Python.")
        sys.exit(1)
    
    # Configurar variables de entorno si es necesario
    os.environ.setdefault('PYTHONPATH', str(PROJECT_ROOT))

def main():
    """
    Función principal del launcher.
    """
    try:
        # Configurar entorno
        setup_environment()
        
        # Importar y ejecutar aplicación
        from src.gui.main_app import main as app_main
        app_main()
        
    except KeyboardInterrupt:
        print("\nAplicación interrumpida por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"Error fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
