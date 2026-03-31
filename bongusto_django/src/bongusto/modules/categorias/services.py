"""
Servicios del módulo categorías.

Aquí se maneja toda la lógica de clasificación de productos y menús.
"""

# Para normalizar texto (quitar tildes, etc)
import unicodedata

# Modelos
from bongusto.domain.models import Categoria, Producto


class CategoriaService:

    # Lista base de categorías del sistema (orden oficial)
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


    # Normaliza el texto (minúsculas + sin tildes)
    def _normalizar_nombre(self, valor):

        # Limpia espacios y pasa a minúscula
        texto = (valor or "").strip().lower()

        # Convierte caracteres especiales (ej: á -> a)
        texto = unicodedata.normalize("NFKD", texto)

        # Quita los acentos
        return "".join(
            ch for ch in texto
            if not unicodedata.combining(ch)
        )


    # Crea un diccionario tipo:
    # "desayunos" -> "Desayunos"
    def _categoria_base_por_clave(self):
        return {
            self._normalizar_nombre(nombre): nombre
            for nombre in self.CATEGORIAS_BASE
        }


    # Decide a qué categoría debe ir algo según su nombre
    def _inferir_categoria_destino(self, nombre):

        clave = self._normalizar_nombre(nombre)

        # Reglas de clasificación
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

        # Busca coincidencias
        for patrones, destino in reglas:
            if any(patron in clave for patron in patrones):
                return destino

        # Si no encuentra nada, lo manda a principales
        return "Platos Principales"


    # Sincroniza la base de datos con las categorías oficiales
    def sincronizar_catalogo_base(self):

        base_por_clave = self._categoria_base_por_clave()
        categorias = list(Categoria.objects.all())
        canonicas = {}

        # Normaliza categorías existentes
        for categoria in categorias:

            clave = self._normalizar_nombre(categoria.nombre_cate)

            if clave in base_por_clave and clave not in canonicas:

                nombre_canonico = base_por_clave[clave]

                # Si el nombre está mal, lo corrige
                if categoria.nombre_cate != nombre_canonico:
                    categoria.nombre_cate = nombre_canonico
                    categoria.save(update_fields=["nombre_cate"])

                canonicas[clave] = categoria

        # Crea categorías que no existen
        for clave, nombre_canonico in base_por_clave.items():
            if clave not in canonicas:
                canonicas[clave] = Categoria.objects.create(
                    nombre_cate=nombre_canonico
                )

        # Reorganiza categorías sobrantes
        for categoria in Categoria.objects.exclude(
            pk__in=[c.pk for c in canonicas.values()]
        ):

            destino_nombre = self._inferir_categoria_destino(
                categoria.nombre_cate
            )

            destino = canonicas[
                self._normalizar_nombre(destino_nombre)
            ]

            # Mueve productos a la nueva categoría
            Producto.objects.filter(id_cate=categoria).update(id_cate=destino)

            # Elimina la categoría vieja
            categoria.delete()


    # Asegura que todo esté sincronizado
    def asegurar_catalogo_base(self):
        self.sincronizar_catalogo_base()


    # Lista todas las categorías en orden base
    def listar_todas(self):

        self.asegurar_catalogo_base()

        categorias = {
            categoria.nombre_cate: categoria
            for categoria in Categoria.objects.all()
        }

        # Devuelve en orden correcto
        return [
            categorias[nombre]
            for nombre in self.CATEGORIAS_BASE
            if nombre in categorias
        ]


    # Buscar por ID
    def buscar_por_id(self, pk):
        return Categoria.objects.filter(pk=pk).first()


    # Guardar categoría
    def guardar(self, categoria):

        # Limpia el nombre
        categoria.nombre_cate = (categoria.nombre_cate or "").strip()

        categoria.save()
        return categoria


    # Eliminar categoría
    def eliminar(self, pk):
        Categoria.objects.filter(pk=pk).delete()


# Exportaciones
__all__ = ["CategoriaService", "Categoria", "Producto"]
