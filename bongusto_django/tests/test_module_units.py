import json
from datetime import timedelta
from unittest.mock import patch

from django.test import RequestFactory, TestCase, override_settings
from django.utils import timezone

from bongusto.domain.models import Categoria, Menu, Permiso, Rol, Usuario
from bongusto.modules.auth.views import _helper, api_password_request_code, api_password_reset
from bongusto.modules.categorias.services import CategoriaService
from bongusto.modules.permisos.services import PermisoService
from bongusto.modules.roles.services import RolService
from bongusto.modules.shared.security import hash_contrasena, verificar_contrasena_usuario
from bongusto.modules.usuarios.services import UsuarioService


class AuthModuleUnitTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.usuario = Usuario.objects.create(
            nombre="Sebas",
            apellido="Prueba",
            correo="sebas@test.com",
            clave=hash_contrasena("ClaveSegura1!"),
            tipo_usuario="cliente",
            estado="Activo",
        )

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_request_code_envia_correo_y_guarda_codigo(self):
        request = self.factory.post(
            "/api/password/request-code",
            data=json.dumps({"correo": self.usuario.correo}),
            content_type="application/json",
        )
        with patch.object(_helper, "enviar_correo_recuperacion") as send_mock:
            response = api_password_request_code(request)

        self.assertEqual(response.status_code, 200)
        send_mock.assert_called_once()
        self.assertIsNotNone(_helper.leer_codigo_api(self.usuario.correo))

    def test_validar_sesion_recuperacion_falla_si_codigo_vence(self):
        reset_data = {
            "email": self.usuario.correo,
            "code": "123456",
            "expires_at": (timezone.now() - timedelta(minutes=1)).isoformat(),
        }

        valido, mensaje = _helper.validar_sesion_recuperacion(
            reset_data,
            self.usuario.correo,
            "123456",
        )

        self.assertFalse(valido)
        self.assertIn("vencio", mensaje.lower())

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_reset_password_actualiza_clave(self):
        _helper.guardar_codigo_api(self.usuario.correo, "123456")

        request = self.factory.post(
            "/api/password/reset",
            data=json.dumps(
                {
                    "correo": self.usuario.correo,
                    "codigo": "123456",
                    "password": "NuevaClave1!",
                    "password_confirm": "NuevaClave1!",
                }
            ),
            content_type="application/json",
        )
        response = api_password_reset(request)

        self.assertEqual(response.status_code, 200)
        self.usuario.refresh_from_db()
        self.assertTrue(verificar_contrasena_usuario(self.usuario, "NuevaClave1!"))


class UsuariosModuleUnitTest(TestCase):
    def setUp(self):
        self.service = UsuarioService()
        self.rol_admin = Rol.objects.create(nombre_rol="Administrador")
        self.rol_mesero = Rol.objects.create(nombre_rol="Mesero")
        self.usuario_activo = Usuario.objects.create(
            nombre="Sebastian",
            apellido="Arteaga",
            correo="sebas.usuarios@test.com",
            clave=hash_contrasena("ClaveSegura1!"),
            tipo_usuario="administrador",
            id_rol=self.rol_admin,
            estado="Activo",
        )
        self.usuario_inactivo = Usuario.objects.create(
            nombre="Carlos",
            apellido="Mesa",
            correo="carlos.usuarios@test.com",
            clave=hash_contrasena("ClaveSegura1!"),
            tipo_usuario="mesero",
            id_rol=self.rol_mesero,
            estado="Inactivo",
        )

    def test_listar_filtrado_permite_combinar_nombre_rol_y_estado(self):
        resultados = self.service.listar_filtrado(
            nombre="Seba",
            rol="Admin",
            estado="activo",
        )
        self.assertEqual(list(resultados), [self.usuario_activo])

    def test_autenticar_retorna_usuario_activo_con_clave_valida(self):
        usuario = self.service.autenticar(
            "sebas.usuarios@test.com",
            "ClaveSegura1!",
        )
        self.assertIsNotNone(usuario)
        self.assertEqual(usuario.id_usuario, self.usuario_activo.id_usuario)

    def test_autenticar_rechaza_usuario_inactivo(self):
        usuario = self.service.autenticar(
            "carlos.usuarios@test.com",
            "ClaveSegura1!",
        )
        self.assertIsNone(usuario)


class RolesModuleUnitTest(TestCase):
    def setUp(self):
        self.service = RolService()

    def test_guardar_y_buscar_por_id(self):
        rol = Rol(nombre_rol="Administrador")
        self.service.guardar(rol)

        encontrado = self.service.buscar_por_id(rol.id_rol)

        self.assertIsNotNone(encontrado)
        self.assertEqual(encontrado.nombre_rol, "Administrador")

    def test_eliminar_remueve_el_rol(self):
        rol = Rol.objects.create(nombre_rol="Mesero")

        self.service.eliminar(rol.id_rol)

        self.assertFalse(Rol.objects.filter(pk=rol.id_rol).exists())


class PermisosModuleUnitTest(TestCase):
    def setUp(self):
        self.service = PermisoService()
        self.crear = Permiso.objects.create(nombre_permiso="Crear pedidos")
        self.editar = Permiso.objects.create(nombre_permiso="Editar menu")

    def test_listar_todos_retorna_permisos_creados(self):
        permisos = list(self.service.listar_todos().order_by("id_permiso"))
        self.assertEqual(permisos, [self.crear, self.editar])

    def test_buscar_por_id_retorna_permiso_correcto(self):
        permiso = self.service.buscar_por_id(self.editar.id_permiso)
        self.assertIsNotNone(permiso)
        self.assertEqual(permiso.nombre_permiso, "Editar menu")


class CategoriasModuleUnitTest(TestCase):
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
        menu = Menu.objects.create(
            nombre_menu="Principal",
            descripcion_menu="Menu base",
        )
        categoria_custom = Categoria.objects.create(nombre_cate="Pescados premium")
        from bongusto.domain.models import Producto
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
