"""módulo auth.
Configuración base del módulo de autenticación dentro del proyecto.
"""

# Se importa AppConfig, que es la clase que Django usa para registrar una app
from django.apps import AppConfig

# Clase que representa la configuración del módulo auth
class AuthConfig(AppConfig):
    
    # Tipo de ID que Django usará automáticamente en los modelos (BigAutoField)
    default_auto_field = "django.db.models.BigAutoField"
    
    # Ruta completa donde está ubicado el módulo dentro del proyecto
    name = "bongusto.modules.auth"
    
    # Nombre corto interno para identificar esta app dentro de Django
    label = "modules_auth"
    
    # Nombre más legible que se puede mostrar en el panel o configuraciones
    verbose_name = "Modulo Auth"