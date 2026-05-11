"""Configuracion del modulo `pedidos`, aqui se maneja todo lo relacionado con pedidos del sistema."""


# Se importa AppConfig que es lo que usa para registrar el modulo
from django.apps import AppConfig



# Clase principal del modulo pedidos
class PedidosConfig(AppConfig):
    # Tipo de id automatico para los modelos
    default_auto_field = "django.db.models.BigAutoField"

    # Ruta del modulo dentro del proyecto
    name = "bongusto.modules.pedidos"

    # Nombre interno del modulo
    label = "modules_pedidos"

    # Nombre que aparece visible 
    verbose_name = "Modulo Pedidos"