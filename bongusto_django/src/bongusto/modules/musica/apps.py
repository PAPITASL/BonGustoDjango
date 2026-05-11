"""Configuracion del modulo musica en Django, aqui se maneja todo lo de canciones."""

# Se importa AppConfig que es lo que usa Django para registrar modulos
from django.apps import AppConfig


# Clase principal del modulo musica (asi Django lo reconoce)
class MusicaConfig(AppConfig):

    # Tipo de ID automatico que se va a usar en los modelos
    default_auto_field = "django.db.models.BigAutoField"

    # Ruta del modulo dentro del proyecto
    name = "bongusto.modules.musica"

    # Nombre interno del modulo (para identificarlo)
    label = "modules_musica"

    # Nombre que se ve en el admin de Django
    verbose_name = "Modulo Musica"

    def ready(self):
        from bongusto.modules.musica.runtime import iniciar_scheduler_musical

        iniciar_scheduler_musical()
