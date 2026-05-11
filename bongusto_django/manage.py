#!/usr/bin/env python
"""Punto de entrada principal de Django para ejecutar comandos del proyecto BonGusto."""

import os
import sys
from pathlib import Path

def main():
    # Se obtiene la ruta base del proyecto (donde esta este archivo).
    base_dir = Path(__file__).resolve().parent

    # Se construye la ruta hacia la carpeta `src`, donde esta el paquete `bongusto`.
    src_dir = base_dir / "src"

    # Se agrega `src` al path de Python para que Django pueda encontrar el proyecto.
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

    # Se define el archivo de configuracion principal de Django.
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bongusto.infrastructure.settings")

    try:
        # Se importa la funcion que permite ejecutar comandos de Django desde consola.
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        # Si Django no esta instalado o hay problema en el entorno, se lanza este error.
        raise ImportError(
            "No se pudo importar Django. Verifica el entorno virtual y las dependencias."
        ) from exc

    # Aqui se ejecuta el comando que se haya enviado (runserver, migrate, createsuperuser, etc).
    execute_from_command_line(sys.argv)

# Punto de entrada del script cuando se ejecuta directamente.
if __name__ == "__main__":
    main()