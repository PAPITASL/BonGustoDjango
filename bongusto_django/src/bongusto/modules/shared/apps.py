"""
Configuracion del modulo `shared`.

Este modulo funciona como una base comun del sistema, donde se agrupan
utilidades, helpers y configuraciones que pueden ser usadas por los
demas modulos de BonGusto.
"""

# ===== Importaciones | Se trae AppConfig para poder registrar el modulo. =====
from django.apps import AppConfig

# ===== Clase `SharedConfig` | Modulo `shared` | Define como se comporta este modulo dentro del proyecto. =====
class SharedConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"  # Define el tipo de ID automatico que se usara por defecto
    name = "bongusto.modules.shared"  # Ruta completa del modulo dentro del proyecto
    label = "modules_shared"  # Nombre interno que usa para identificar este modulo
    verbose_name = "Modulo Shared"  # Nombre que se muestra en el panel de administracion