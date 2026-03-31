"""
Configuracion Django del modulo `shared`.

Este modulo contiene recursos compartidos que pueden ser utilizados
por los demas modulos del sistema (utilidades, helpers, configuraciones, etc).
"""

# ===== Importaciones | Dependencias necesarias para registrar el modulo dentro de Django. =====
from django.apps import AppConfig



# ===== Clase `SharedConfig` | Modulo `shared` | Define la configuracion base del modulo compartido. =====
class SharedConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"  # Tipo de ID automatico por defecto
    name = "bongusto.modules.shared"  # Ruta del modulo dentro del proyecto
    label = "modules_shared"  # Identificador interno en Django
    verbose_name = "Modulo Shared"  # Nombre visible en el panel administrativo