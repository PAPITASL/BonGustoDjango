from django.test import TestCase

from bongusto.domain.models import Permiso
from bongusto.modules.permisos.services import PermisoService


class PermisoServiceTest(TestCase):
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
