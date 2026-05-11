"""
tests/test_views.py
Pruebas de integracion enfocadas en las respuestas HTTP de las vistas.
Aqui se valida que las rutas principales del sistema respondan bien,
redirijan cuando toca y generen archivos como PDF o JSON cuando corresponde.
Ejecutar con: python manage.py test tests
"""
from django.test import TestCase, Client, RequestFactory

from bongusto.interfaces.views import dashboard as dashboard_view


class AuthViewsTest(TestCase):
    """Pruebas relacionadas con autenticacion y proteccion de rutas."""

    def setUp(self):
        # Se crea un cliente de pruebas para simular peticiones HTTP.
        self.client = Client()

    def test_root_redirige_a_login(self):
        """La ruta raiz debe enviar al usuario hacia login."""
        response = self.client.get("/")
        self.assertRedirects(response, "/login", fetch_redirect_response=False)

    def test_login_get_retorna_200(self):
        """La vista de login debe cargar correctamente con GET."""
        response = self.client.get("/login")
        self.assertEqual(response.status_code, 200)

    def test_login_post_credenciales_invalidas(self):
        """Si las credenciales son invalidas, la vista debe seguir cargando y mostrar error."""
        response = self.client.post("/login", {
            "username": "noexiste@test.com",
            "password": "wrongpass",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "incorrectos")

    def test_rutas_protegidas_redirigen_sin_sesion(self):
        """Las rutas privadas deben redirigir cuando no existe una sesion activa."""
        rutas = ["/dashboard", "/usuarios", "/productos", "/menus",
                 "/categorias", "/musicas", "/eventos", "/bitacora",
                 "/roles", "/permisos", "/chat", "/perfil"]

        # Se recorre cada ruta para confirmar que ninguna deje pasar sin login.
        for ruta in rutas:
            r = self.client.get(ruta)
            self.assertIn(r.status_code, [301, 302],
                          msg=f"{ruta} deberia redirigir sin sesion")


class DashboardViewTest(TestCase):
    """Pruebas del dashboard simulando una sesion iniciada."""

    def setUp(self):
        # Se prepara cliente y factory para probar tanto vistas completas como llamadas directas.
        self.client = Client()
        self.factory = RequestFactory()

        # Se crea una sesion simulada de administrador.
        session = self.client.session
        session["usuario_id"] = 200
        session["usuario_nombre"] = "sebastian"
        session["usuario_tipo"] = "administrador"
        session.save()

    def test_dashboard_con_sesion_retorna_200(self):
        """Con sesion valida, el dashboard debe responder correctamente."""
        request = self.factory.get("/dashboard")
        request.session = {
            "usuario_id": 200,
            "usuario_nombre": "sebastian",
            "usuario_tipo": "administrador",
        }

        # Aqui se llama directamente la vista para validar su respuesta.
        response = dashboard_view.index(request)
        self.assertEqual(response.status_code, 200)

    def test_dashboard_sin_sesion_redirige(self):
        """Sin sesion, el dashboard debe enviar al login."""
        self.client.session.flush()
        response = self.client.get("/dashboard")
        self.assertRedirects(response, "/login", fetch_redirect_response=False)

    def test_dashboard_reporte_retorna_pdf(self):
        """La ruta del reporte del dashboard debe devolver un archivo PDF."""
        r = self.client.get("/dashboard/reporte")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r["Content-Type"], "application/pdf")


class UsuarioViewTest(TestCase):
    """Pruebas principales del modulo de usuarios."""

    def setUp(self):
        # Se simula una sesion de administrador para acceder al modulo.
        self.client = Client()
        session = self.client.session
        session["usuario_id"] = 200
        session["usuario_nombre"] = "Admin"
        session["usuario_tipo"] = "administrador"
        session.save()

    def test_lista_usuarios_retorna_200(self):
        """El listado general de usuarios debe cargar correctamente."""
        r = self.client.get("/usuarios")
        self.assertEqual(r.status_code, 200)

    def test_form_crear_usuario_retorna_200(self):
        """El formulario para crear usuarios debe abrir sin errores."""
        r = self.client.get("/usuarios/create")
        self.assertEqual(r.status_code, 200)

    def test_filtro_por_nombre(self):
        """La vista debe responder bien cuando se filtra por nombre."""
        r = self.client.get("/usuarios?nombre=juan")
        self.assertEqual(r.status_code, 200)

    def test_filtro_por_estado(self):
        """La vista debe responder bien cuando se filtra por estado."""
        r = self.client.get("/usuarios?estado=Activo")
        self.assertEqual(r.status_code, 200)

    def test_reporte_usuarios_retorna_pdf(self):
        """El reporte del modulo usuarios debe generarse en PDF."""
        r = self.client.get("/usuarios/reporte")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r["Content-Type"], "application/pdf")


class ProductoViewTest(TestCase):
    """Pruebas principales del modulo de productos."""

    def setUp(self):
        # Se prepara una sesion valida para acceder a las rutas protegidas.
        self.client = Client()
        s = self.client.session
        s["usuario_id"] = 200
        s["usuario_nombre"] = "Admin"
        s["usuario_tipo"] = "administrador"
        s.save()

    def test_lista_retorna_200(self):
        """El listado de productos debe cargar correctamente."""
        r = self.client.get("/productos")
        self.assertEqual(r.status_code, 200)

    def test_form_nuevo_retorna_200(self):
        """El formulario para crear un producto debe abrir sin errores."""
        r = self.client.get("/productos/create")
        self.assertEqual(r.status_code, 200)

    def test_reporte_productos_retorna_pdf(self):
        """El reporte de productos debe devolverse como PDF."""
        r = self.client.get("/productos/reporte")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r["Content-Type"], "application/pdf")


class MenuViewTest(TestCase):
    """Pruebas basicas del modulo de menus."""

    def setUp(self):
        # Se crea una sesion simple para acceder a las vistas del modulo.
        self.client = Client()
        s = self.client.session
        s["usuario_id"] = 200
        s.save()

    def test_lista_retorna_200(self):
        """La vista principal de menus debe responder correctamente."""
        r = self.client.get("/menus")
        self.assertEqual(r.status_code, 200)

    def test_form_nuevo_retorna_200(self):
        """El formulario para crear menus debe abrir sin errores."""
        r = self.client.get("/menus/create")
        self.assertEqual(r.status_code, 200)

    def test_reporte_menus_retorna_pdf(self):
        """La exportacion de menus debe devolverse como PDF."""
        r = self.client.get("/menus/pdf")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r["Content-Type"], "application/pdf")


class MusicaViewTest(TestCase):
    """Pruebas basicas del modulo de musica."""

    def setUp(self):
        # Se simula una sesion para acceder al modulo.
        self.client = Client()
        s = self.client.session
        s["usuario_id"] = 200
        s.save()

    def test_lista_retorna_200(self):
        """El listado de musica debe cargar sin problemas."""
        r = self.client.get("/musicas")
        self.assertEqual(r.status_code, 200)

    def test_form_nueva_retorna_200(self):
        """El formulario para registrar musica debe responder bien."""
        r = self.client.get("/musicas/nueva")
        self.assertEqual(r.status_code, 200)

    def test_reporte_musica_retorna_pdf(self):
        """El reporte del modulo musica debe salir en PDF."""
        r = self.client.get("/musicas/reporte")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r["Content-Type"], "application/pdf")


class ReservaViewTest(TestCase):
    """Pruebas basicas del modulo de reservas o eventos."""

    def setUp(self):
        # Se crea sesion de prueba para acceder a la vista.
        self.client = Client()
        s = self.client.session
        s["usuario_id"] = 200
        s.save()

    def test_lista_retorna_200(self):
        """La lista de reservas/eventos debe cargar correctamente."""
        r = self.client.get("/eventos")
        self.assertEqual(r.status_code, 200)

    def test_filtro_estado(self):
        """El filtro por estado en reservas debe responder bien."""
        r = self.client.get("/eventos?estado=activa")
        self.assertEqual(r.status_code, 200)

    def test_reporte_eventos_retorna_pdf(self):
        """El reporte de eventos debe devolverse en formato PDF."""
        r = self.client.get("/eventos/pdf")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r["Content-Type"], "application/pdf")


class BitacoraViewTest(TestCase):
    """Pruebas del modulo de bitacora."""

    def setUp(self):
        # Se prepara sesion valida para ingresar al modulo.
        self.client = Client()
        s = self.client.session
        s["usuario_id"] = 200
        s.save()

    def test_lista_bitacora_retorna_200(self):
        """La vista principal de bitacora debe responder correctamente."""
        r = self.client.get("/bitacora")
        self.assertEqual(r.status_code, 200)

    def test_reporte_bitacora_retorna_pdf(self):
        """La exportacion de bitacora debe entregarse como PDF."""
        r = self.client.get("/bitacora/reporte")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r["Content-Type"], "application/pdf")

class PedidoApiTest(TestCase):
    """Pruebas basicas para la API REST de pedidos."""
    def setUp(self):
        # Se crea una sesion base para probar endpoints protegidos.
        self.client = Client()
        s = self.client.session
        s["usuario_id"] = 200
        s.save()
    def test_get_pedidos_retorna_json(self):
        """La API de pedidos debe responder con contenido JSON."""
        r = self.client.get("/api/pedidos")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r["Content-Type"], "application/json")

    def test_get_pedido_inexistente_retorna_404(self):
        """Si el pedido no existe, la API debe responder con 404."""
        r = self.client.get("/api/pedidos/99999")
        self.assertEqual(r.status_code, 404)