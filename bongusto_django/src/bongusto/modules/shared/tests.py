"""Tests del modulo shared."""

# ===== Importaciones | Dependencias necesarias para mocks, respuestas y pruebas del modulo compartido. =====
from unittest.mock import MagicMock, patch

from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from bongusto.modules.shared.api_auth import participante_permitido
from bongusto.modules.shared.audit import usuario_actual
from bongusto.modules.shared.excel_import import leer_filas_excel, normalizar_encabezado, texto_limpio
from bongusto.modules.shared.middleware import AuthMiddleware
from bongusto.modules.shared.security import es_hash_django, validar_contrasena_segura


# ===== Clase `SharedHelpersTest` | Modulo `shared` | Reune pruebas basicas para utilidades compartidas del sistema. =====
class SharedHelpersTest(TestCase):
    """Cobertura basica para helpers compartidos."""

    # ===== Funcion `setUp` | Prepara objetos reutilizables antes de cada prueba. =====
    def setUp(self):
        self.factory = RequestFactory()

    # ===== Funcion `test_normalizar_encabezado_limpia_texto` | Verifica limpieza de encabezados del Excel. =====
    def test_normalizar_encabezado_limpia_texto(self):
        self.assertEqual(normalizar_encabezado(" Nombre / Producto "), "nombre_producto")

    # ===== Funcion `test_texto_limpio_convierte_none_a_vacio` | Verifica que None se convierta en texto vacio. =====
    def test_texto_limpio_convierte_none_a_vacio(self):
        self.assertEqual(texto_limpio(None), "")

    # ===== Funcion `test_leer_filas_excel_rechaza_archivo_sin_extension_xlsx` | Valida que solo se acepten archivos .xlsx. =====
    def test_leer_filas_excel_rechaza_archivo_sin_extension_xlsx(self):
        archivo = MagicMock()
        archivo.name = "productos.csv"

        with self.assertRaises(ValueError) as error:
            leer_filas_excel(archivo)

        self.assertIn(".xlsx", str(error.exception))

    # ===== Funcion `test_usuario_actual_retorna_none_si_no_hay_sesion` | Verifica que no se obtenga usuario sin sesion. =====
    def test_usuario_actual_retorna_none_si_no_hay_sesion(self):
        request = self.factory.get("/productos")
        request.session = {}

        self.assertIsNone(usuario_actual(request))

    # ===== Funcion `test_middleware_redirige_si_no_hay_sesion_en_ruta_privada` | Valida proteccion de rutas privadas. =====
    def test_middleware_redirige_si_no_hay_sesion_en_ruta_privada(self):
        middleware = AuthMiddleware(lambda request: HttpResponse("ok"))
        request = self.factory.get("/productos")
        request.session = {}

        response = middleware(request)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login")

    # ===== Funcion `test_middleware_permite_ruta_publica` | Verifica acceso normal a rutas publicas. =====
    def test_middleware_permite_ruta_publica(self):
        middleware = AuthMiddleware(lambda request: HttpResponse("ok"))
        request = self.factory.get("/login")
        request.session = {}

        response = middleware(request)

        self.assertEqual(response.status_code, 200)

    # ===== Funcion `test_validar_contrasena_segura_detecta_clave_valida` | Verifica una contrasena que cumple la politica. =====
    def test_validar_contrasena_segura_detecta_clave_valida(self):
        valida, mensaje = validar_contrasena_segura("ClaveSegura1!")

        self.assertTrue(valida)
        self.assertEqual(mensaje, "")

    # ===== Funcion `test_es_hash_django_detecta_valor_invalido` | Verifica que texto plano no se detecte como hash valido. =====
    def test_es_hash_django_detecta_valor_invalido(self):
        self.assertFalse(es_hash_django("texto_plano"))

    # ===== Funcion `test_participante_permitido_valida_cliente` | Comprueba acceso correcto segun el participante del chat. =====
    def test_participante_permitido_valida_cliente(self):
        usuario = MagicMock(id_usuario=7, tipo_usuario="cliente")

        self.assertTrue(participante_permitido(usuario, "cliente_7"))
        self.assertFalse(participante_permitido(usuario, "cliente_8"))

    # ===== Funcion `test_leer_filas_excel_falla_con_mensaje_claro_si_falta_openpyxl` | Valida mensaje de error si falta la libreria. =====
    def test_leer_filas_excel_falla_con_mensaje_claro_si_falta_openpyxl(self):
        archivo = MagicMock()
        archivo.name = "plantilla.xlsx"

        with patch("bongusto.modules.shared.excel_import.load_workbook", None):
            with self.assertRaises(RuntimeError) as error:
                leer_filas_excel(archivo)

        self.assertIn("Hace falta instalar openpyxl", str(error.exception))