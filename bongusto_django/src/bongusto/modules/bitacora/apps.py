"""Configuración Django del módulo bitácora.
Aquí se registra la app que maneja el historial de acciones del sistema.
"""
# Importamos AppConfig, que sirve para configurar una app en Django
from django.apps import AppConfig

# Configuración del módulo bitácora
class BitacoraConfig(AppConfig):
    # Tipo de id automático por defecto (llave primaria en modelos)
    default_auto_field = "django.db.models.BigAutoField"
    # Ruta completa del módulo dentro del proyecto
    name = "bongusto.modules.bitacora"
    # Nombre interno corto (evita conflictos entre apps)
    label = "modules_bitacora"
    # Nombre más entendible para mostrar en paneles
    verbose_name = "Modulo Bitacora"