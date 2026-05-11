"""
tests/test_services.py
Pruebas unitarias enfocadas en la capa de aplicacion (services).
Estas pruebas ayudan a validar que la logica principal del sistema
responda correctamente en distintos escenarios.
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
    """Pruebas basicas para validar el comportamiento de UsuarioService."""

    def setUp(self):
        # Se crea una instancia del servicio antes de cada prueba.
        self.service = UsuarioService()

    def test_autenticar_correo_incorrecto(self):
        """Si las credenciales no existen o son incorrectas, debe devolver None."""
        resultado = self.service.autenticar("noexiste@test.com", "wrongpass")
        self.assertIsNone(resultado)

    def test_listar_filtrado_sin_filtros(self):
        """Cuando no se envian filtros, debe devolver el queryset general."""
        resultado = self.service.listar_filtrado()
        # Aqui solo comprobamos que la respuesta exista y pueda usarse.
        self.assertIsNotNone(resultado)

    def test_buscar_por_id_inexistente(self):
        """Si el ID no existe en base de datos, debe devolver None."""
        resultado = self.service.buscar_por_id(99999)
        self.assertIsNone(resultado)


class RolServiceTest(TestCase):
    """Pruebas basicas para el servicio de roles."""

    def setUp(self):
        # Se prepara el servicio antes de cada prueba.
        self.service = RolService()

    def test_listar_todos_no_prefetch_rol_permisos(self):
        # Se valida que el queryset no venga con prefetch extra innecesario.
        resultado = self.service.listar_todos()
        self.assertEqual(resultado._prefetch_related_lookups, ())


class MenuServiceTest(TestCase):
    """Pruebas relacionadas con el servicio de menus."""

    def setUp(self):
        # Instancia base del servicio de menus.
        self.service = MenuService()

    def test_listar_filtrado_vacio(self):
        """Debe responder aunque no se envien filtros."""
        resultado = self.service.listar_filtrado()
        self.assertIsNotNone(resultado)

    def test_listar_filtrado_por_nombre(self):
        """Si el nombre no coincide con nada, debe devolver una lista vacia."""
        resultado = self.service.listar_filtrado(nombre="xxxxxx_inexistente")
        self.assertEqual(list(resultado), [])

    def test_buscar_inexistente(self):
        """Buscar un menu que no existe debe devolver None."""
        self.assertIsNone(self.service.buscar_por_id(99999))

    def test_modelo_menu_permita_300_caracteres(self):
        """Valida que el modelo soporte nombres y descripciones amplias."""
        from bongusto.domain.models import Menu

        self.assertEqual(Menu._meta.get_field("nombre_menu").max_length, 300)
        self.assertEqual(Menu._meta.get_field("descripcion_menu").max_length, 300)


class ProductoServiceTest(TestCase):
    """Pruebas del servicio de productos."""

    def setUp(self):
        # Se inicializa el servicio para reutilizarlo en cada test.
        self.service = ProductoService()

    def test_listar_todos(self):
        """Debe devolver el listado general de productos sin fallar."""
        resultado = self.service.listar_todos()
        self.assertIsNotNone(resultado)

    def test_filtrado_por_nombre_inexistente(self):
        """Si no hay coincidencias por nombre, el resultado debe quedar vacio."""
        resultado = self.service.listar_filtrado(nombre="xxxxnoexiste")
        self.assertEqual(list(resultado), [])

    def test_buscar_inexistente(self):
        """Si el producto no existe, debe devolver None."""
        self.assertIsNone(self.service.buscar_por_id(99999))

    def test_modelo_producto_permita_300_caracteres(self):
        """Valida que el modelo de producto soporte textos largos."""
        from bongusto.domain.models import Producto

        self.assertEqual(Producto._meta.get_field("nombre_producto").max_length, 300)
        self.assertEqual(Producto._meta.get_field("descripcion_producto").max_length, 300)


class CategoriaServiceTest(TestCase):
    """Pruebas del servicio de categorias."""

    def setUp(self):
        # Servicio base para trabajar las pruebas de categorias.
        self.service = CategoriaService()

    def test_listar_todas(self):
        """Debe retornar el listado general de categorias."""
        resultado = self.service.listar_todas()
        self.assertIsNotNone(resultado)

    def test_buscar_inexistente(self):
        """Si la categoria no existe, debe devolver None."""
        self.assertIsNone(self.service.buscar_por_id(99999))

    def test_listar_todas_siembra_catalogo_base(self):
        """Si no hay categorias, el servicio debe sembrar el catalogo base."""
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
        """No debe duplicar categorias cuando ya existen nombres parecidos o equivalentes."""
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
    """Pruebas del servicio de musica."""

    def setUp(self):
        # Se crea la instancia del servicio antes de cada prueba.
        self.service = MusicaService()

    def test_listar_todas(self):
        """Debe devolver el listado general de musica."""
        resultado = self.service.listar_todas()
        self.assertIsNotNone(resultado)

    def test_buscar_inexistente(self):
        """Si la musica no existe, debe devolver None."""
        self.assertIsNone(self.service.buscar_por_id(99999))


class BitacoraServiceTest(TestCase):
    """Pruebas del servicio de bitacora."""

    def setUp(self):
        # Servicio base para las pruebas de bitacora.
        self.service = BitacoraService()

    def test_listar_filtrado_sin_filtros(self):
        """Sin filtros debe responder normalmente."""
        resultado = self.service.listar_filtrado()
        self.assertIsNotNone(resultado)

    def test_filtrado_por_accion_inexistente(self):
        """Si la accion no coincide con nada, el resultado debe estar vacio."""
        resultado = self.service.listar_filtrado(accion="xxxxnoexiste")
        self.assertEqual(list(resultado), [])


class ReservaServiceTest(TestCase):
    """Pruebas del servicio de reservas."""

    def setUp(self):
        # Se prepara el servicio de reservas.
        self.service = ReservaService()

    def test_listar_todas(self):
        """Debe devolver el listado general de reservas."""
        resultado = self.service.listar_todas()
        self.assertIsNotNone(resultado)

    def test_buscar_inexistente(self):
        """Buscar una reserva inexistente debe devolver None."""
        self.assertIsNone(self.service.buscar_por_id(99999))


class DashboardServiceTest(TestCase):
    """Pruebas del servicio del dashboard."""

    def setUp(self):
        # Se inicializa el servicio del dashboard.
        self.service = DashboardService()

    def test_estadisticas_retorna_dict_completo(self):
        """Las estadisticas principales deben venir con todas las claves esperadas."""
        stats = self.service.obtener_estadisticas()
        self.assertIn("total_usuarios", stats)
        self.assertIn("total_menus", stats)
        self.assertIn("total_productos", stats)
        self.assertIn("total_categorias", stats)
        self.assertIn("total_musica", stats)
        self.assertIn("total_reservas", stats)

    def test_estadisticas_valores_son_enteros(self):
        """Los valores numericos del resumen deben devolverse como enteros."""
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
        """El dashboard debe incluir estructuras listas para mostrar en pantalla."""
        stats = self.service.obtener_estadisticas()
        self.assertIsInstance(stats["metricas_resumen"], list)
        self.assertIsInstance(stats["actividad_modulos"], list)
        self.assertIsInstance(stats["usuarios_por_tipo"], list)
        self.assertIsInstance(stats["resumen_operativo"], list)
        self.assertIsInstance(stats["lineas_reserva"], dict)
        self.assertIsInstance(stats["calendario_dashboard"], dict)

    def test_ultimos_retorna_dict_completo(self):
        """La seccion de ultimos registros debe traer todas las claves necesarias."""
        ultimos = self.service.obtener_ultimos()
        self.assertIn("ultimos_menus", ultimos)
        self.assertIn("ultimos_productos", ultimos)
        self.assertIn("ultimas_musicas", ultimos)
        self.assertIn("ultimas_reservas", ultimos)


class ExcelImportTest(TestCase):
    """Pruebas de la utilidad compartida de importacion desde Excel."""

    def test_falla_con_mensaje_claro_si_openpyxl_no_esta_instalado(self):
        """Si falta openpyxl, el sistema debe lanzar un error claro y entendible."""
        archivo = MagicMock()
        archivo.name = "plantilla.xlsx"

        with patch("builtins.__import__") as import_mock:
            original_import = __import__

            def _import_controlado(name, *args, **kwargs):
                # Se simula el caso donde openpyxl no esta disponible.
                if name == "openpyxl":
                    raise ImportError("missing openpyxl")
                return original_import(name, *args, **kwargs)

            import_mock.side_effect = _import_controlado

            with self.assertRaises(RuntimeError) as error:
                leer_filas_excel(archivo)

        self.assertIn("Hace falta instalar openpyxl", str(error.exception))