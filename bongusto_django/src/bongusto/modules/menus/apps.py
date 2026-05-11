"""Configuracion del modulo menus."""

# ===== Importacion base =====
from django.apps import AppConfig


# ===== Clase principal del modulo menus =====
class MenusConfig(AppConfig):

    # Tipo de ID automatico para los modelos
    # Esto define que las llaves primarias sean grandes (recomendado actualmente)
    default_auto_field = "django.db.models.BigAutoField"

    # Ruta donde esta ubicado el modulo dentro del proyecto
    # IMPORTANTE: debe coincidir exactamente con la estructura de carpetas
    name = "bongusto.modules.menus"

    # Nombre interno del modulo
    # Django lo usa por debajo para evitar conflictos con otros modulos
    label = "modules_menus"

    # Nombre visible en el admin
    # Es el nombre que ve el usuario o administrador en el panel
    verbose_name = "Modulo Menus"