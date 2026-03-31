"""Configuracion del modulo menus en Django, aqui se maneja todo lo relacionado con los menus del sistema."""

# ===== Importacion base | Se usa AppConfig para registrar el modulo dentro del proyecto. =====
from django.apps import AppConfig


# ===== Clase principal del modulo menus | Define como Django reconoce este modulo. =====
class MenusConfig(AppConfig):

    # Tipo de ID automatico para los modelos
    default_auto_field = "django.db.models.BigAutoField"

    # Ruta donde esta ubicado el modulo
    name = "bongusto.modules.menus"

    # Nombre interno del modulo
    label = "modules_menus"

    # Nombre visible en el admin
    verbose_name = "Modulo Menus"