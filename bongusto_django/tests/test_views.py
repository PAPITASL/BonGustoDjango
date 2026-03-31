"""
tests/test_views.py
Pruebas de integracion: respuestas HTTP de las vistas.
Ejecutar con: python manage.py test tests
"""

from django.test import TestCase, Client, RequestFactory

from bongusto.interfaces.views import dashboard as dashboard_view


class AuthViewsTest(TestCase):
    """Tests de autenticacion."""

    def setUp(self):
        self.client = Client()

    def test_root_redirige_a_login(self):
        response = self.client.get("/")
        self.assertRedirects(response, "/login", fetch_redirect_response=False)

    def test_login_get_retorna_200(self):
        response = self.client.get("/login")
        self.assertEqual(response.status_code, 200)

    def test_login_post_credenciales_invalidas(self):
        response = self.client.post("/login", {
            "username": "noexiste@test.com",
            "password": "wrongpass",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "incorrectos")

    def test_rutas_protegidas_redirigen_sin_sesion(self):
        rutas = ["/dashboard", "/usuarios", "/productos", "/menus",
                 "/categorias", "/musicas", "/eventos", "/bitacora",
                 "/roles", "/permisos", "/chat", "/perfil"]
        for ruta in rutas:
            r = self.client.get(ruta)
            self.assertIn(r.status_code, [301, 302],
                          msg=f"{ruta} deberia redirigir sin sesion")


class DashboardViewTest(TestCase):
    """Tests del dashboard con sesion simulada."""

    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
        session = self.client.session
        session["usuario_id"] = 200
        session["usuario_nombre"] = "sebastian"
        session["usuario_tipo"] = "administrador"
        session.save()

    def test_dashboard_con_sesion_retorna_200(self):
        request = self.factory.get("/dashboard")
        request.session = {
            "usuario_id": 200,
            "usuario_nombre": "sebastian",
            "usuario_tipo": "administrador",
        }
        response = dashboard_view.index(request)
        self.assertEqual(response.status_code, 200)

    def test_dashboard_sin_sesion_redirige(self):
        self.client.session.flush()
        response = self.client.get("/dashboard")
        self.assertRedirects(response, "/login", fetch_redirect_response=False)

    def test_dashboard_reporte_retorna_pdf(self):
        r = self.client.get("/dashboard/reporte")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r["Content-Type"], "application/pdf")


class UsuarioViewTest(TestCase):
    """Tests CRUD de usuarios."""

    def setUp(self):
        self.client = Client()
        session = self.client.session
        session["usuario_id"] = 200
        session["usuario_nombre"] = "Admin"
        session["usuario_tipo"] = "administrador"
        session.save()

    def test_lista_usuarios_retorna_200(self):
        r = self.client.get("/usuarios")
        self.assertEqual(r.status_code, 200)

    def test_form_crear_usuario_retorna_200(self):
        r = self.client.get("/usuarios/create")
        self.assertEqual(r.status_code, 200)

    def test_filtro_por_nombre(self):
        r = self.client.get("/usuarios?nombre=juan")
        self.assertEqual(r.status_code, 200)

    def test_filtro_por_estado(self):
        r = self.client.get("/usuarios?estado=Activo")
        self.assertEqual(r.status_code, 200)

    def test_reporte_usuarios_retorna_pdf(self):
        r = self.client.get("/usuarios/reporte")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r["Content-Type"], "application/pdf")


class ProductoViewTest(TestCase):
    """Tests CRUD de productos."""

    def setUp(self):
        self.client = Client()
        s = self.client.session
        s["usuario_id"] = 200
        s["usuario_nombre"] = "Admin"
        s["usuario_tipo"] = "administrador"
        s.save()

    def test_lista_retorna_200(self):
        r = self.client.get("/productos")
        self.assertEqual(r.status_code, 200)

    def test_form_nuevo_retorna_200(self):
        r = self.client.get("/productos/create")
        self.assertEqual(r.status_code, 200)

    def test_reporte_productos_retorna_pdf(self):
        r = self.client.get("/productos/reporte")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r["Content-Type"], "application/pdf")


class MenuViewTest(TestCase):
    """Tests de menus."""

    def setUp(self):
        self.client = Client()
        s = self.client.session
        s["usuario_id"] = 200
        s.save()

    def test_lista_retorna_200(self):
        r = self.client.get("/menus")
        self.assertEqual(r.status_code, 200)

    def test_form_nuevo_retorna_200(self):
        r = self.client.get("/menus/create")
        self.assertEqual(r.status_code, 200)

    def test_reporte_menus_retorna_pdf(self):
        r = self.client.get("/menus/pdf")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r["Content-Type"], "application/pdf")


class MusicaViewTest(TestCase):
    """Tests de musica."""

    def setUp(self):
        self.client = Client()
        s = self.client.session
        s["usuario_id"] = 200
        s.save()

    def test_lista_retorna_200(self):
        r = self.client.get("/musicas")
        self.assertEqual(r.status_code, 200)

    def test_form_nueva_retorna_200(self):
        r = self.client.get("/musicas/nueva")
        self.assertEqual(r.status_code, 200)

    def test_reporte_musica_retorna_pdf(self):
        r = self.client.get("/musicas/reporte")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r["Content-Type"], "application/pdf")


class ReservaViewTest(TestCase):
    """Tests de reservas."""

    def setUp(self):
        self.client = Client()
        s = self.client.session
        s["usuario_id"] = 200
        s.save()

    def test_lista_retorna_200(self):
        r = self.client.get("/eventos")
        self.assertEqual(r.status_code, 200)

    def test_filtro_estado(self):
        r = self.client.get("/eventos?estado=activa")
        self.assertEqual(r.status_code, 200)

    def test_reporte_eventos_retorna_pdf(self):
        r = self.client.get("/eventos/pdf")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r["Content-Type"], "application/pdf")


class BitacoraViewTest(TestCase):
    """Tests de bitácora."""

    def setUp(self):
        self.client = Client()
        s = self.client.session
        s["usuario_id"] = 200
        s.save()

    def test_lista_bitacora_retorna_200(self):
        r = self.client.get("/bitacora")
        self.assertEqual(r.status_code, 200)

    def test_reporte_bitacora_retorna_pdf(self):
        r = self.client.get("/bitacora/reporte")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r["Content-Type"], "application/pdf")


class PedidoApiTest(TestCase):
    """Tests de la API REST de pedidos."""

    def setUp(self):
        self.client = Client()
        s = self.client.session
        s["usuario_id"] = 200
        s.save()

    def test_get_pedidos_retorna_json(self):
        r = self.client.get("/api/pedidos")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r["Content-Type"], "application/json")

    def test_get_pedido_inexistente_retorna_404(self):
        r = self.client.get("/api/pedidos/99999")
        self.assertEqual(r.status_code, 404)
