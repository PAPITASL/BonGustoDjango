from django.test import TransactionTestCase

from bongusto.domain.models import Categoria, Menu, Producto, Usuario
from bongusto.modules.mesas.models import Mesa
from bongusto.modules.pedidos.services import PedidoService
from bongusto.modules.shared.table_state import MesaStateService


class PedidoModuleTest(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.service = PedidoService()
        self.mesa_service = MesaStateService()
        self.menu = Menu.objects.create(nombre_menu="Principal", descripcion_menu="Test")
        self.categoria = Categoria.objects.create(nombre_cate="Hamburguesas")
        self.cliente = Usuario.objects.create(
            nombre="Cliente",
            apellido="Pedido",
            correo="cliente@pedido.test",
            clave="hash",
            tipo_usuario="cliente",
            estado="Activo",
        )
        self.mesa = Mesa.objects.create(numero_mesa=20, nombre="Pedidos", capacidad=4, activa=True)
        self.producto = Producto.objects.create(
            nombre_producto="Hamburguesa",
            precio_producto=12000,
            descripcion_producto="Prueba",
            id_menu=self.menu,
            id_cate=self.categoria,
            id_res=1,
            estado="activo",
        )
        self.mesa_service.seleccionar_para_cliente(self.cliente, mesa_id=self.mesa.id)

    def test_total_del_pedido_sale_de_los_items(self):
        pedido = self.service.crear_pedido_con_detalles(
            {
                "id_usuario": self.cliente.id_usuario,
                "mesa_id": self.mesa.id,
                "id_restaurante": 1,
                "total_pedido": 999999,
                "items": [
                    {
                        "id_producto": self.producto.id_producto,
                        "cantidad": 2,
                        "precio": 12000,
                    }
                ],
            }
        )

        self.assertEqual(float(pedido.total_pedido or 0), 24000.0)
