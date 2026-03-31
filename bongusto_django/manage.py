#!/usr/bin/env python
"""Punto de entrada de gestion de Django para BonGusto."""

import os
import sys
from pathlib import Path


def main():
    # Inserta `src/` en el path para que Django encuentre el paquete `bongusto`.
    base_dir = Path(__file__).resolve().parent
    src_dir = base_dir / "src"
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

    # Define el modulo de configuracion principal del proyecto.
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bongusto.infrastructure.settings")

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "No se pudo importar Django. Verifica el entorno virtual y las dependencias."
        ) from exc

    # Ejecuta comandos como `runserver`, `check`, `migrate` y similares.
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
