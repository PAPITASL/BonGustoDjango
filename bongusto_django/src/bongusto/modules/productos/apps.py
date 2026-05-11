"""Configuracion del modulo `productos`, aqui se maneja todo lo de productos del restaurante."""

# Se importa AppConfig que es lo que usa para registrar el modulo
from django.apps import AppConfig


# Clase principal del modulo productos
class ProductosConfig(AppConfig):
    # Tipo de id automatico para los modelos
    default_auto_field = "django.db.models.BigAutoField"

    # Ruta del modulo dentro del proyecto
    name = "bongusto.modules.productos"

    # Nombre interno del modulo
    label = "modules_productos"

    # Nombre que se muestra en el admin o configuraciones
    verbose_name = "Modulo Productos"