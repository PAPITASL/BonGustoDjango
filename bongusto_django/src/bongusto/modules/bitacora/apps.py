"""Configuración del módulo bitácora.
Aquí se define cómo Django reconoce esta app dentro del proyecto.
Este módulo es el que maneja todo el historial de acciones del sistema.
"""
# Se importa AppConfig, que es la base para registrar una app en Django
from django.apps import AppConfig

# Clase de configuración del módulo bitácora
class BitacoraConfig(AppConfig):
    
    # Tipo de id que se usará por defecto en los modelos (BigAutoField)
    default_auto_field = "django.db.models.BigAutoField"
    
    # Ruta completa del módulo dentro del proyecto
    # Django usa esto para ubicar correctamente la app
    name = "bongusto.modules.bitacora"
    
    # Nombre interno corto de la app
    # Sirve para identificarla sin chocar con otras apps
    label = "modules_bitacora"
    
    # Nombre más legible que se puede mostrar en el admin u otras partes
    verbose_name = "Modulo Bitacora"