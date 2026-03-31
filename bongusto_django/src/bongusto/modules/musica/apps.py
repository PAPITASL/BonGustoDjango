"""Configuracion del modulo musica en Django, aqui se maneja todo lo relacionado con canciones y solicitudes."""

# ===== Importacion base | Se usa AppConfig para registrar el modulo en el proyecto. =====
from django.apps import AppConfig


# ===== Clase principal del modulo musica | Define como Django reconoce este modulo. =====
class MusicaConfig(AppConfig):

    # Tipo de ID automatico para los modelos
    default_auto_field = "django.db.models.BigAutoField"

    # Ruta del modulo dentro del proyecto
    name = "bongusto.modules.musica"

    # Nombre interno del modulo
    label = "modules_musica"

    # Nombre visible en el admin
    verbose_name = "Modulo Musica"