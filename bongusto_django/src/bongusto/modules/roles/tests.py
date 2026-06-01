from django.test import TestCase

from bongusto.domain.models import Rol
from bongusto.modules.roles.services import RolService


class RolServiceTest(TestCase):
    def setUp(self):
        self.service = RolService()

    def test_guardar_y_buscar_por_id_retorna_rol_persistido(self):
        rol = Rol(nombre_rol="Administrador")
        self.service.guardar(rol)

        encontrado = self.service.buscar_por_id(rol.id_rol)

        self.assertIsNotNone(encontrado)
        self.assertEqual(encontrado.nombre_rol, "Administrador")

    def test_eliminar_remueve_el_rol(self):
        rol = Rol.objects.create(nombre_rol="Mesero")

        self.service.eliminar(rol.id_rol)

        self.assertFalse(Rol.objects.filter(pk=rol.id_rol).exists())
