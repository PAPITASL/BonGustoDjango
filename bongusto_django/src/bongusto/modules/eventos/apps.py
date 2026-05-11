"""Configuracion del modulo eventos en Django, aqui se manejan las reservas y eventos del sistema."""

# ===== Importacion base | AppConfig es lo que usa Django para reconocer que este archivo es una app. =====
from django.apps import AppConfig


# ===== Clase principal del modulo eventos | Aqui basicamente le estamos diciendo a Django: "este es mi modulo eventos". =====
class EventosConfig(AppConfig):

    # Tipo de ID automatico para los modelos
    # Esto define como se crean las llaves primarias (IDs) en la base de datos
    # BigAutoField es el recomendado porque soporta muchisimos mas registros
    default_auto_field = "django.db.models.BigAutoField"

    # Ruta donde esta ubicado el modulo dentro del proyecto
    # Esto es clave porque Django usa esto para encontrar la app
    name = "bongusto.modules.eventos"

    # Nombre interno del modulo
    # No es visible para el usuario, pero Django lo usa por debajo
    # Sirve para evitar problemas si hay nombres repetidos en otros modulos
    label = "modules_eventos"

    # Nombre mas entendible o mas bonito
    # Este es el que se ve en el panel de admin o configuraciones
    verbose_name = "Modulo Eventos"