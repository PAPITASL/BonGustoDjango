"""
Servicios del módulo categorías.
Aquí es donde se maneja toda la lógica para organizar y clasificar productos y menús.
"""

# Se usa para trabajar texto y normalizarlo mejor (por ejemplo quitar tildes)
import unicodedata

# Modelos que necesita este servicio
from bongusto.domain.models import Categoria, Producto


class CategoriaService:

    # Categorías principales del sistema
    # Este es el orden base que se quiere mantener siempre
    CATEGORIAS_BASE = [
        "Desayunos",
        "Brunch",
        "Entradas",
        "Platos Principales",
        "Receta de Autor",
        "Postres",
        "Bebidas (Sin Alcohol)",
        "Bebidas Calientes",
        "Bebidas Frias",
        "Bebidas con Alcohol",
        "Cócteles",
        "Opciones Saludables",
        "Vegetarianos y Veganos",
    ]

    # Sirve para limpiar el texto y compararlo mejor
    # Lo deja en minúsculas, sin tildes y sin espacios raros
    def _normalizar_nombre(self, valor):

        # Limpia espacios al inicio y final, y pasa todo a minúscula
        texto = (valor or "").strip().lower()

        # Convierte caracteres especiales para poder tratarlos más fácil
        texto = unicodedata.normalize("NFKD", texto)

        # Elimina las tildes
        return "".join(
            ch for ch in texto
            if not unicodedata.combining(ch)
        )

    # Crea un diccionario para ubicar rápido las categorías base
    # Ejemplo: "desayunos" apunta a "Desayunos"
    def _categoria_base_por_clave(self):
        return {
            self._normalizar_nombre(nombre): nombre
            for nombre in self.CATEGORIAS_BASE
        }

    # Intenta decidir a qué categoría debería pertenecer un nombre
    # Se basa en palabras clave encontradas en el texto
    def _inferir_categoria_destino(self, nombre):

        clave = self._normalizar_nombre(nombre)

        # Reglas de palabras clave para clasificar
        reglas = [
            (("desayuno", "huevos", "omelette", "parfait", "bowl"), "Desayunos"),
            (("brunch", "waffle", "pancake", "tostada", "french toast", "infantil"), "Brunch"),
            (("entrada", "tapa", "compartir", "charcuteria", "queso", "sopa", "crema"), "Entradas"),
            (
                (
                    "pasta", "arroz", "risotto", "sushi", "asian",
                    "marisco", "pescado", "carne", "parrilla",
                    "fuego", "fuerte", "chef", "hamburguesa",
                    "pizza", "flatbread", "sandwich", "panini",
                ),
                "Platos Principales",
            ),
            (("autor", "chef", "especial"), "Receta de Autor"),
            (("postre", "helado", "sorbete", "dulce"), "Postres"),
            (("cafe", "te", "infusion", "caliente"), "Bebidas Calientes"),
            (("jugo", "smoothie", "gaseosa", "refresco", "fria", "frio"), "Bebidas Frias"),
            (("mocktail", "sin alcohol"), "Bebidas (Sin Alcohol)"),
            (("vino", "espumoso", "cerveza", "licor", "destilado", "alcohol"), "Bebidas con Alcohol"),
            (("coctel", "cocktail", "gin tonic", "shot", "bomb", "happy hour"), "Cócteles"),
            (("ensalada", "healthy", "fit", "saludable", "sin gluten"), "Opciones Saludables"),
            (("vegetar", "vegano"), "Vegetarianos y Veganos"),
        ]

        # Revisa si alguna palabra clave coincide
        for patrones, destino in reglas:
            if any(patron in clave for patron in patrones):
                return destino

        # Si no encuentra algo claro, lo manda a platos principales
        return "Platos Principales"

    # Organiza todo el catálogo de categorías
    # Corrige nombres, crea faltantes y elimina las que sobran
    def sincronizar_catalogo_base(self):

        base_por_clave = self._categoria_base_por_clave()
        categorias = list(Categoria.objects.all())
        canonicas = {}

        # Revisa las categorías que ya existen
        for categoria in categorias:

            clave = self._normalizar_nombre(categoria.nombre_cate)

            if clave in base_por_clave and clave not in canonicas:

                nombre_canonico = base_por_clave[clave]

                # Si el nombre no coincide con el oficial, lo corrige
                if categoria.nombre_cate != nombre_canonico:
                    categoria.nombre_cate = nombre_canonico
                    categoria.save(update_fields=["nombre_cate"])

                canonicas[clave] = categoria

        # Crea las categorías base que hagan falta
        for clave, nombre_canonico in base_por_clave.items():
            if clave not in canonicas:
                canonicas[clave] = Categoria.objects.create(
                    nombre_cate=nombre_canonico
                )

        # Reacomoda categorías que no pertenecen a la base oficial
        for categoria in Categoria.objects.exclude(
            pk__in=[c.pk for c in canonicas.values()]
        ):

            destino_nombre = self._inferir_categoria_destino(
                categoria.nombre_cate
            )

            destino = canonicas[
                self._normalizar_nombre(destino_nombre)
            ]

            # Mueve los productos a la categoría correcta
            Producto.objects.filter(id_cate=categoria).update(id_cate=destino)

            # Después elimina la categoría vieja
            categoria.delete()

    # Se asegura de que el catálogo base esté bien organizado
    def asegurar_catalogo_base(self):
        self.sincronizar_catalogo_base()

    # Lista todas las categorías respetando el orden base
    def listar_todas(self):

        self.asegurar_catalogo_base()

        categorias = {
            categoria.nombre_cate: categoria
            for categoria in Categoria.objects.all()
        }

        # Devuelve las categorías en el orden definido arriba
        return [
            categorias[nombre]
            for nombre in self.CATEGORIAS_BASE
            if nombre in categorias
        ]

    # Busca una categoría por su id
    def buscar_por_id(self, pk):
        return Categoria.objects.filter(pk=pk).first()

    # Guarda una categoría
    def guardar(self, categoria):

        # Limpia espacios antes de guardar
        categoria.nombre_cate = (categoria.nombre_cate or "").strip()

        categoria.save()
        return categoria

    # Elimina una categoría por id
    def eliminar(self, pk):
        Categoria.objects.filter(pk=pk).delete()


# Define lo que se puede importar desde este archivo
__all__ = ["CategoriaService", "Categoria", "Producto"]