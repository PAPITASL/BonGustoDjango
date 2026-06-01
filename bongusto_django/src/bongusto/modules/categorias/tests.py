from django.test import TestCase

from bongusto.domain.models import Categoria, Menu, Producto
from bongusto.modules.categorias.services import CategoriaService


class CategoriaServiceTest(TestCase):
    def setUp(self):
        self.service = CategoriaService()

    def test_asegurar_catalogo_base_crea_categorias_canonicas(self):
        self.service.asegurar_catalogo_base()

        categorias = Categoria.objects.all()

        self.assertEqual(categorias.count(), len(self.service.CATEGORIAS_BASE))
        self.assertTrue(
            Categoria.objects.filter(nombre_cate="Platos Principales").exists()
        )

    def test_sincronizar_catalogo_reubica_categoria_fuera_de_base(self):
        menu = Menu.objects.create(nombre_menu="Principal", descripcion_menu="Menu base")
        categoria_custom = Categoria.objects.create(nombre_cate="Pescados premium")
        producto = Producto.objects.create(
            nombre_producto="Salmon de la casa",
            precio_producto=35000,
            descripcion_producto="Especialidad",
            id_menu=menu,
            id_cate=categoria_custom,
            estado="activo",
        )

        self.service.sincronizar_catalogo_base()

        producto.refresh_from_db()
        self.assertEqual(producto.id_cate.nombre_cate, "Platos Principales")
        self.assertFalse(Categoria.objects.filter(pk=categoria_custom.pk).exists())
