from django.test import TestCase

from bongusto.domain.models import Rol, Usuario
from bongusto.modules.shared.security import hash_contrasena
from bongusto.modules.usuarios.services import UsuarioService


class UsuarioServiceTest(TestCase):
    def setUp(self):
        self.service = UsuarioService()
        self.rol_admin = Rol.objects.create(nombre_rol="Administrador")
        self.rol_mesero = Rol.objects.create(nombre_rol="Mesero")
        self.usuario_activo = Usuario.objects.create(
            nombre="Sebastian",
            apellido="Arteaga",
            correo="sebas@test.com",
            clave=hash_contrasena("ClaveSegura1!"),
            tipo_usuario="administrador",
            id_rol=self.rol_admin,
            estado="Activo",
        )
        self.usuario_inactivo = Usuario.objects.create(
            nombre="Carlos",
            apellido="Mesa",
            correo="carlos@test.com",
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
        usuario = self.service.autenticar("sebas@test.com", "ClaveSegura1!")

        self.assertIsNotNone(usuario)
        self.assertEqual(usuario.id_usuario, self.usuario_activo.id_usuario)

    def test_autenticar_rechaza_usuario_inactivo(self):
        usuario = self.service.autenticar("carlos@test.com", "ClaveSegura1!")

        self.assertIsNone(usuario)
