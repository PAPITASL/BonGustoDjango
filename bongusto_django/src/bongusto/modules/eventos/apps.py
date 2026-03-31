"""Configuracion del modulo eventos en Django, aqui se manejan las reservas y eventos del sistema."""

# ===== Importacion base | Se usa AppConfig para registrar el modulo dentro del proyecto. =====
from django.apps import AppConfig


# ===== Clase principal del modulo eventos | Aqui se define como Django reconoce este modulo. =====
class EventosConfig(AppConfig):

    # Tipo de ID automatico para los modelos (llave primaria)
    default_auto_field = "django.db.models.BigAutoField"

    # Ruta donde esta ubicado el modulo dentro del proyecto
    name = "bongusto.modules.eventos"

    # Nombre interno para evitar conflictos con otros modulos
    label = "modules_eventos"

    # Nombre que se muestra en el admin de Django
    verbose_name = "Modulo Eventos"