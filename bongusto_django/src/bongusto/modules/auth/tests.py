import json
from unittest.mock import patch

from django.test import RequestFactory, TestCase, override_settings

from bongusto.domain.models import Usuario
from bongusto.modules.auth.views import _helper, api_password_request_code, api_password_reset
from bongusto.modules.shared.security import hash_contrasena, verificar_contrasena_usuario


class PasswordRecoveryApiTests(TestCase):
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

    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend",
        EMAIL_HOST_USER="",
        EMAIL_HOST_PASSWORD="",
    )
    def test_request_code_retorna_503_si_smtp_no_esta_configurado(self):
        request = self.factory.post(
            "/api/password/request-code",
            data=json.dumps({"correo": self.usuario.correo}),
            content_type="application/json",
        )
        response = api_password_request_code(request)

        self.assertEqual(response.status_code, 503)
        payload = json.loads(response.content.decode())
        self.assertIn("no esta configurado", payload["error"].lower())

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_reset_password_actualiza_clave_con_codigo_valido(self):
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
        self.assertIsNone(_helper.leer_codigo_api(self.usuario.correo))
