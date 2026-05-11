"""
Modelos del módulo categorías.
Aquí no se crean modelos directamente,
solo se usan los que ya están en la capa de dominio.
"""
# Importamos el modelo Categoria desde domain
# Es el modelo real que ya tiene la estructura de la base de datos
from bongusto.domain.models import Categoria
# Esto define qué se puede usar cuando otro archivo importa este módulo
# En este caso solo estamos exponiendo Categoria
__all__ = ["Categoria"]