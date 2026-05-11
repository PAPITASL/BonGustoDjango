"""Configuracion del modulo `usuarios` en Django.

Este modulo se encarga de manejar todo lo relacionado con usuarios
del sistema, tanto internos (meseros, administradores) como clientes
que interactuan desde la API.
"""
# ===== Importaciones | Se importa AppConfig para registrar correctamente el modulo en Django. =====
from django.apps import AppConfig

# ===== Clase `UsuariosConfig` | Modulo `usuarios` | Define como Django reconoce y carga este modulo. =====
class UsuariosConfig(AppConfig):
    # Tipo de campo ID que se usara por defecto en los modelos (BigAutoField = numeros grandes automaticos)
    default_auto_field = "django.db.models.BigAutoField"

    # Ruta completa del modulo dentro del proyecto
    name = "bongusto.modules.usuarios"

    # Nombre interno que Django usa para identificar este modulo (evita conflictos con otros)
    label = "modules_usuarios"

    # Nombre visible en el panel de administracion de Django
    verbose_name = "Modulo Usuarios"