#!/usr/bin/env python3
import sys
import os

# Asegurar que el directorio actual es el del proyecto
project_root = os.path.dirname(os.path.realpath(__file__))
os.chdir(project_root)
sys.path.insert(0, project_root)

# Importamos la interfaz gráfica
from gui.main_window import MicrowaveLinkDesigner

def main():
    print("=" * 60)
    print("  HERRAMIENTA DE DISEÑO DE ENLACES SATELITALES")
    print("=" * 60)
    print("\nIniciando aplicación...\n")
    
    try:
        app = MicrowaveLinkDesigner()
        print("Aplicación iniciada correctamente.\n")
        app.mainloop()
    except Exception as e:
        print(f"Error al iniciar la aplicación: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print("\nAplicación cerrada.")

if __name__ == "__main__":
    main()