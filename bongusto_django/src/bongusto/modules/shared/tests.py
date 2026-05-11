"""Pruebas del modulo shared."""

# ===== Importaciones | Aqui se traen las herramientas necesarias para simular objetos,
# ===== hacer pruebas de peticiones y validar que las funciones del modulo compartido funcionen bien. =====
from unittest.mock import MagicMock, patch

from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from bongusto.modules.shared.api_auth import participante_permitido
from bongusto.modules.shared.audit import usuario_actual
from bongusto.modules.shared.excel_import import leer_filas_excel, normalizar_encabezado, texto_limpio
from bongusto.modules.shared.middleware import AuthMiddleware
from bongusto.modules.shared.security import es_hash_django, validar_contrasena_segura


# ===== Clase `SharedHelpersTest` | Modulo `shared` | Reune pruebas sencillas pero importantes
# ===== para comprobar que varias utilidades compartidas del sistema funcionen como se espera. =====
class SharedHelpersTest(TestCase):
    """Contiene pruebas basicas para validar helpers del modulo shared."""

    # ===== Funcion `setUp` | Se ejecuta antes de cada prueba para preparar objetos reutilizables. =====
    def setUp(self):
        # RequestFactory permite simular peticiones HTTP sin necesidad de levantar el servidor.
        self.factory = RequestFactory()

    # ===== Funcion `test_normalizar_encabezado_limpia_texto` | Revisa que un encabezado del Excel
    # ===== se limpie correctamente y quede en un formato estandar. =====
    def test_normalizar_encabezado_limpia_texto(self):
        self.assertEqual(normalizar_encabezado(" Nombre / Producto "), "nombre_producto")

    # ===== Funcion `test_texto_limpio_convierte_none_a_vacio` | Valida que si llega un valor None,
    # ===== la funcion devuelva texto vacio y no cause errores. =====
    def test_texto_limpio_convierte_none_a_vacio(self):
        self.assertEqual(texto_limpio(None), "")

    # ===== Funcion `test_leer_filas_excel_rechaza_archivo_sin_extension_xlsx` | Comprueba que
    # ===== la importacion solo acepte archivos Excel reales con extension .xlsx. =====
    def test_leer_filas_excel_rechaza_archivo_sin_extension_xlsx(self):
        # Se crea un archivo simulado con una extension no permitida.
        archivo = MagicMock()
        archivo.name = "productos.csv"

        # Se espera que la funcion lance un ValueError.
        with self.assertRaises(ValueError) as error:
            leer_filas_excel(archivo)

        # Se valida que el mensaje mencione claramente la extension .xlsx.
        self.assertIn(".xlsx", str(error.exception))

    # ===== Funcion `test_usuario_actual_retorna_none_si_no_hay_sesion` | Valida que si no existe
    # ===== un usuario guardado en sesion, la funcion devuelva None. =====
    def test_usuario_actual_retorna_none_si_no_hay_sesion(self):
        # Se simula una peticion a una ruta cualquiera.
        request = self.factory.get("/productos")
        request.session = {}

        self.assertIsNone(usuario_actual(request))

    # ===== Funcion `test_middleware_redirige_si_no_hay_sesion_en_ruta_privada` | Verifica que
    # ===== el middleware bloquee rutas privadas cuando no hay login activo. =====
    def test_middleware_redirige_si_no_hay_sesion_en_ruta_privada(self):
        # Se crea el middleware con una respuesta simple.
        middleware = AuthMiddleware(lambda request: HttpResponse("ok"))
        request = self.factory.get("/productos")
        request.session = {}

        # Se ejecuta el middleware como si la peticion entrara al sistema.
        response = middleware(request)

        # Debe redirigir al login.
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login")

    # ===== Funcion `test_middleware_permite_ruta_publica` | Revisa que una ruta publica
    # ===== si pueda pasar aunque no exista sesion iniciada. =====
    def test_middleware_permite_ruta_publica(self):
        middleware = AuthMiddleware(lambda request: HttpResponse("ok"))
        request = self.factory.get("/login")
        request.session = {}

        response = middleware(request)

        # Como /login es publica, la respuesta debe continuar normal.
        self.assertEqual(response.status_code, 200)

    # ===== Funcion `test_validar_contrasena_segura_detecta_clave_valida` | Comprueba que una clave
    # ===== bien construida pase correctamente la validacion de seguridad. =====
    def test_validar_contrasena_segura_detecta_clave_valida(self):
        valida, mensaje = validar_contrasena_segura("ClaveSegura1!")

        self.assertTrue(valida)
        self.assertEqual(mensaje, "")

    # ===== Funcion `test_es_hash_django_detecta_valor_invalido` | Verifica que un texto plano comun
    # ===== no sea confundido con un hash valido de Django. =====
    def test_es_hash_django_detecta_valor_invalido(self):
        self.assertFalse(es_hash_django("texto_plano"))

    # ===== Funcion `test_participante_permitido_valida_cliente` | Comprueba que la validacion del
    # ===== participante del chat funcione correctamente para un usuario tipo cliente. =====
    def test_participante_permitido_valida_cliente(self):
        # Se simula un usuario cliente con ID 7.
        usuario = MagicMock(id_usuario=7, tipo_usuario="cliente")

        # Debe permitir su propio identificador y rechazar otro diferente.
        self.assertTrue(participante_permitido(usuario, "cliente_7"))
        self.assertFalse(participante_permitido(usuario, "cliente_8"))

    # ===== Funcion `test_leer_filas_excel_falla_con_mensaje_claro_si_falta_openpyxl` | Valida que
    # ===== el sistema muestre un error entendible cuando no esta instalada la libreria necesaria. =====
    def test_leer_filas_excel_falla_con_mensaje_claro_si_falta_openpyxl(self):
        archivo = MagicMock()
        archivo.name = "plantilla.xlsx"

        # Se simula la ausencia de openpyxl para probar la respuesta del sistema.
        with patch("bongusto.modules.shared.excel_import.load_workbook", None):
            with self.assertRaises(RuntimeError) as error:
                leer_filas_excel(archivo)

        # Se valida que el mensaje explique claramente que falta instalar openpyxl.
        self.assertIn("Hace falta instalar openpyxl", str(error.exception))