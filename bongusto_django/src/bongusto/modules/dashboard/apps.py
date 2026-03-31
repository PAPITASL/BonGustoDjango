"""Configuracion Django del modulo `dashboard`: resumen general y metricas del panel."""

# Importacion basica para poder crear la configuracion de la app
from django.apps import AppConfig


# Esta clase define como Django reconoce y maneja el modulo dashboard
class DashboardConfig(AppConfig):

    # Tipo de ID automatico que usara el sistema (BigAutoField es lo recomendado hoy)
    default_auto_field = "django.db.models.BigAutoField"

    # Ruta donde esta ubicado el modulo dentro del proyecto
    # IMPORTANTE: esto debe coincidir exactamente con tus carpetas
    name = "bongusto.modules.dashboard"

    # Nombre interno unico de la app (Django lo usa por debajo)
    label = "modules_dashboard"

    # Nombre bonito que se ve en el admin o en configuraciones
    verbose_name = "Modulo Dashboard"
