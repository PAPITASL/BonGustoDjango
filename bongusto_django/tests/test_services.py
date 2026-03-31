"""
tests/test_services.py
Pruebas unitarias de la capa de aplicación (services).
Ejecutar con: python manage.py test tests
"""

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bongusto.infrastructure.settings")

from django.test import TestCase
from unittest.mock import patch, MagicMock
from bongusto.application.services import (
    UsuarioService,
    RolService,
    MenuService,
    ProductoService,
    CategoriaService,
    MusicaService,
    BitacoraService,
    ReservaService,
    DashboardService,
)
from bongusto.domain.models import Categoria
from bongusto.modules.shared.excel_import import leer_filas_excel


class UsuarioServiceTest(TestCase):
    """Tests de UsuarioService."""

    def setUp(self):
        self.service = UsuarioService()

    def test_autenticar_correo_incorrecto(self):
        """Credenciales inválidas deben retornar None."""
        resultado = self.service.autenticar("noexiste@test.com", "wrongpass")
        self.assertIsNone(resultado)

    def test_listar_filtrado_sin_filtros(self):
        """Sin filtros debe retornar queryset completo (puede estar vacío en test DB)."""
        resultado = self.service.listar_filtrado()
        # Solo verificamos que es iterable
        self.assertIsNotNone(resultado)

    def test_buscar_por_id_inexistente(self):
        """ID que no existe debe retornar None."""
        resultado = self.service.buscar_por_id(99999)
        self.assertIsNone(resultado)


class RolServiceTest(TestCase):
    """Tests de RolService."""

    def setUp(self):
        self.service = RolService()

    def test_listar_todos_no_prefetch_rol_permisos(self):
        resultado = self.service.listar_todos()
        self.assertEqual(resultado._prefetch_related_lookups, ())


class MenuServiceTest(TestCase):
    """Tests de MenuService."""

    def setUp(self):
        self.service = MenuService()

    def test_listar_filtrado_vacio(self):
        resultado = self.service.listar_filtrado()
        self.assertIsNotNone(resultado)

    def test_listar_filtrado_por_nombre(self):
        resultado = self.service.listar_filtrado(nombre="xxxxxx_inexistente")
        self.assertEqual(list(resultado), [])

    def test_buscar_inexistente(self):
        self.assertIsNone(self.service.buscar_por_id(99999))

    def test_modelo_menu_permita_300_caracteres(self):
        from bongusto.domain.models import Menu

        self.assertEqual(Menu._meta.get_field("nombre_menu").max_length, 300)
        self.assertEqual(Menu._meta.get_field("descripcion_menu").max_length, 300)


class ProductoServiceTest(TestCase):
    """Tests de ProductoService."""

    def setUp(self):
        self.service = ProductoService()

    def test_listar_todos(self):
        resultado = self.service.listar_todos()
        self.assertIsNotNone(resultado)

    def test_filtrado_por_nombre_inexistente(self):
        resultado = self.service.listar_filtrado(nombre="xxxxnoexiste")
        self.assertEqual(list(resultado), [])

    def test_buscar_inexistente(self):
        self.assertIsNone(self.service.buscar_por_id(99999))

    def test_modelo_producto_permita_300_caracteres(self):
        from bongusto.domain.models import Producto

        self.assertEqual(Producto._meta.get_field("nombre_producto").max_length, 300)
        self.assertEqual(Producto._meta.get_field("descripcion_producto").max_length, 300)


class CategoriaServiceTest(TestCase):
    """Tests de CategoriaService."""

    def setUp(self):
        self.service = CategoriaService()

    def test_listar_todas(self):
        resultado = self.service.listar_todas()
        self.assertIsNotNone(resultado)

    def test_buscar_inexistente(self):
        self.assertIsNone(self.service.buscar_por_id(99999))

    def test_listar_todas_siembra_catalogo_base(self):
        Categoria.objects.all().delete()

        resultado = list(self.service.listar_todas())

        self.assertEqual(len(resultado), 13)
        nombres = {c.nombre_cate for c in resultado}
        self.assertIn("Desayunos", nombres)
        self.assertIn("Entradas", nombres)
        self.assertIn("Cócteles", nombres)
        self.assertIn("Vegetarianos y Veganos", nombres)
        self.assertIn("Receta de Autor", nombres)

    def test_catalogo_base_no_duplica_nombres_equivalentes(self):
        Categoria.objects.create(nombre_cate="cocteles de autor")
        Categoria.objects.create(nombre_cate="Entradas Frias")

        self.service.asegurar_catalogo_base()

        nombres = list(Categoria.objects.values_list("nombre_cate", flat=True))

        self.assertEqual(Categoria.objects.count(), 13)
        self.assertIn("Cócteles", nombres)
        self.assertIn("Entradas", nombres)
        self.assertNotIn("cocteles de autor", nombres)
        self.assertNotIn("Entradas Frias", nombres)


class MusicaServiceTest(TestCase):
    """Tests de MusicaService."""

    def setUp(self):
        self.service = MusicaService()

    def test_listar_todas(self):
        resultado = self.service.listar_todas()
        self.assertIsNotNone(resultado)

    def test_buscar_inexistente(self):
        self.assertIsNone(self.service.buscar_por_id(99999))


class BitacoraServiceTest(TestCase):
    """Tests de BitacoraService."""

    def setUp(self):
        self.service = BitacoraService()

    def test_listar_filtrado_sin_filtros(self):
        resultado = self.service.listar_filtrado()
        self.assertIsNotNone(resultado)

    def test_filtrado_por_accion_inexistente(self):
        resultado = self.service.listar_filtrado(accion="xxxxnoexiste")
        self.assertEqual(list(resultado), [])


class ReservaServiceTest(TestCase):
    """Tests de ReservaService."""

    def setUp(self):
        self.service = ReservaService()

    def test_listar_todas(self):
        resultado = self.service.listar_todas()
        self.assertIsNotNone(resultado)

    def test_buscar_inexistente(self):
        self.assertIsNone(self.service.buscar_por_id(99999))


class DashboardServiceTest(TestCase):
    """Tests de DashboardService."""

    def setUp(self):
        self.service = DashboardService()

    def test_estadisticas_retorna_dict_completo(self):
        stats = self.service.obtener_estadisticas()
        self.assertIn("total_usuarios", stats)
        self.assertIn("total_menus", stats)
        self.assertIn("total_productos", stats)
        self.assertIn("total_categorias", stats)
        self.assertIn("total_musica", stats)
        self.assertIn("total_reservas", stats)

    def test_estadisticas_valores_son_enteros(self):
        stats = self.service.obtener_estadisticas()
        for key in [
            "total_usuarios",
            "total_menus",
            "total_productos",
            "total_categorias",
            "total_musica",
            "total_reservas",
            "resumen_general_total",
            "resumen_general_porcentaje",
        ]:
            self.assertIsInstance(stats[key], int, f"{key} debe ser int, got {type(stats[key])}")

    def test_estadisticas_incluye_bloques_visuales(self):
        stats = self.service.obtener_estadisticas()
        self.assertIsInstance(stats["metricas_resumen"], list)
        self.assertIsInstance(stats["actividad_modulos"], list)
        self.assertIsInstance(stats["usuarios_por_tipo"], list)
        self.assertIsInstance(stats["resumen_operativo"], list)
        self.assertIsInstance(stats["lineas_reserva"], dict)
        self.assertIsInstance(stats["calendario_dashboard"], dict)

    def test_ultimos_retorna_dict_completo(self):
        ultimos = self.service.obtener_ultimos()
        self.assertIn("ultimos_menus", ultimos)
        self.assertIn("ultimos_productos", ultimos)
        self.assertIn("ultimas_musicas", ultimos)
        self.assertIn("ultimas_reservas", ultimos)


class ExcelImportTest(TestCase):
    """Tests de la utilidad compartida de importacion Excel."""

    def test_falla_con_mensaje_claro_si_openpyxl_no_esta_instalado(self):
        archivo = MagicMock()
        archivo.name = "plantilla.xlsx"

        with patch("builtins.__import__") as import_mock:
            original_import = __import__

            def _import_controlado(name, *args, **kwargs):
                if name == "openpyxl":
                    raise ImportError("missing openpyxl")
                return original_import(name, *args, **kwargs)

            import_mock.side_effect = _import_controlado

            with self.assertRaises(RuntimeError) as error:
                leer_filas_excel(archivo)

        self.assertIn("Hace falta instalar openpyxl", str(error.exception))
