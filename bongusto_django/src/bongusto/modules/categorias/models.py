"""
Modelos del módulo categorías.

Aquí no se crean modelos, solo se traen desde domain
para usarlos dentro de este módulo.
"""

# Importamos el modelo real de Categoria
from bongusto.domain.models import Categoria


# __all__ define qué se puede usar desde este archivo
# O sea, qué se exporta cuando otro archivo importa este módulo
__all__ = ["Categoria"]