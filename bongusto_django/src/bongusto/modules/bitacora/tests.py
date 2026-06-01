from django.test import TestCase
from django.utils import timezone

from bongusto.domain.models import Usuario
from bongusto.modules.bitacora.services import BitacoraService


class BitacoraServiceTest(TestCase):
    def setUp(self):
        self.service = BitacoraService()
        self.usuario = Usuario.objects.create(
            nombre="Ana",
            apellido="Auditora",
            correo="ana@test.com",
            clave="hash",
            tipo_usuario="administrador",
            estado="Activo",
        )

    def test_registrar_guarda_accion_con_fecha_timezone_aware(self):
        registro = self.service.registrar(self.usuario, "Creo un usuario")

        self.assertIsNotNone(registro.id_log)
        self.assertTrue(timezone.is_aware(registro.fecha_accion))

    def test_listar_filtrado_aplica_filtros_de_usuario_y_accion(self):
        self.service.registrar(self.usuario, "Creo un usuario")
        self.service.registrar(self.usuario, "Elimino un producto")

        resultados = self.service.listar_filtrado(usuario="Ana", accion="producto")

        self.assertEqual(len(resultados), 1)
        self.assertIn("producto", resultados[0].accion.lower())
