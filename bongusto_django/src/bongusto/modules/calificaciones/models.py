"""
Modelos del módulo calificaciones.

Aquí no se crean modelos, solo se traen desde domain
para usarlos dentro de este módulo.
"""

# Importamos los modelos reales del sistema
from bongusto.domain.models import CalificacionCliente, PedidoEncabezado, Usuario


# __all__ define qué modelos se pueden usar desde este archivo
# O sea, qué se exporta cuando otro archivo importa este módulo
__all__ = ["CalificacionCliente", "PedidoEncabezado", "Usuario"]