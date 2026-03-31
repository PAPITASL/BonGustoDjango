"""
Configuración del módulo categorías.

Aquí se registra la app que maneja la clasificación de productos y menús.
"""

# Importamos AppConfig (sirve para registrar el módulo en Django)
from django.apps import AppConfig


# Configuración del módulo categorías
class CategoriasConfig(AppConfig):

    # Tipo de ID automático (llave primaria)
    default_auto_field = "django.db.models.BigAutoField"

    # Ruta del módulo dentro del proyecto
    name = "bongusto.modules.categorias"

    # Nombre interno (para evitar conflictos)
    label = "modules_categorias"

    # Nombre visible (más entendible)
    verbose_name = "Modulo Categorias"