"""Pruebas basicas del modulo mesas."""

from django.core.exceptions import ValidationError
from django.test import TransactionTestCase

from bongusto.domain.models import PedidoEncabezado, SolicitudPago, Usuario
from bongusto.modules.mesas.models import Mesa
from bongusto.modules.pedidos.payment_services import SolicitudPagoService
from bongusto.modules.shared.table_state import MesaStateService


class MesaModuleTest(TransactionTestCase):
    """Valida reglas criticas del modelo, servicio y API de mesas."""

    reset_sequences = True

    def setUp(self):
        self.service = MesaStateService()
        self.admin = Usuario.objects.create(
            nombre="Admin",
            apellido="Mesa",
            correo="admin@bongusto.test",
            clave="hash",
            tipo_usuario="administrador",
            estado="Activo",
        )
        self.cliente = Usuario.objects.create(
            nombre="Cliente",
            apellido="Mesa",
            correo="cliente@bongusto.test",
            clave="hash",
            tipo_usuario="cliente",
            estado="Activo",
        )
        self.mesero = Usuario.objects.create(
            nombre="Mesero",
            apellido="Mesa",
            correo="mesero@bongusto.test",
            clave="hash",
            tipo_usuario="mesero",
            estado="Activo",
        )

    def _login_session(self, usuario):
        session = self.client.session
        session["usuario_id"] = usuario.id_usuario
        session["usuario_tipo"] = usuario.tipo_usuario
        session.save()

    def test_creacion_correcta_de_mesa(self):
        mesa = Mesa(numero_mesa=1, nombre="Ventana", capacidad=4, activa=True)
        mesa.full_clean()
        mesa.save()

        self.assertEqual(mesa.numero_mesa, 1)
        self.assertEqual(mesa.estado, Mesa.ESTADO_LIBRE)

    def test_error_al_crear_mesa_con_numero_cero(self):
        mesa = Mesa(numero_mesa=0, nombre="Invalida", capacidad=4, activa=True)

        with self.assertRaises(ValidationError):
            mesa.full_clean()

    def test_error_al_duplicar_numero_mesa(self):
        Mesa.objects.create(numero_mesa=5, nombre="Principal", capacidad=4, activa=True)
        duplicada = Mesa(numero_mesa=5, nombre="Duplicada", capacidad=2, activa=True)

        with self.assertRaises(ValidationError):
            duplicada.full_clean()

    def test_historial_desactiva_en_lugar_de_borrar(self):
        mesa = Mesa.objects.create(numero_mesa=8, nombre="Patio", capacidad=4, activa=True)
        PedidoEncabezado.objects.create(
            id_usuario=self.cliente,
            id_restaurante=1,
            total_pedido=25000,
            mesa=mesa,
        )

        ok, mensaje = self.service.eliminar_o_desactivar(mesa)
        mesa.refresh_from_db()

        self.assertTrue(ok)
        self.assertEqual(mensaje, "Mesa desactivada para conservar historial.")
        self.assertFalse(mesa.activa)
        self.assertEqual(mesa.estado, Mesa.ESTADO_BLOQUEADA)

    def test_ocupar_solicitar_pago_confirmar_y_liberar_mesa(self):
        mesa = Mesa.objects.create(numero_mesa=3, nombre="Salon", capacidad=4, activa=True)
        self.service.seleccionar_para_cliente(self.cliente, mesa_id=mesa.id)
        pedido = PedidoEncabezado.objects.create(
            id_usuario=self.cliente,
            id_restaurante=1,
            total_pedido=42000,
            mesa=mesa,
        )
        self.service.ocupar_con_pedido(mesa, pedido, cliente=self.cliente)
        mesa.refresh_from_db()

        self.assertEqual(mesa.estado, Mesa.ESTADO_OCUPADA)
        self.assertEqual(mesa.pedido_actual_id, pedido.id_pedido)

        solicitud = SolicitudPagoService().crear_solicitud(
            self.cliente,
            metodo_pago="efectivo",
            pedido_id=pedido.id_pedido,
            mesa_id=mesa.id,
        )
        mesa.refresh_from_db()
        self.assertEqual(mesa.estado, Mesa.ESTADO_ESPERANDO_PAGO)

        SolicitudPagoService().actualizar_estado(
            solicitud.id_solicitud_pago,
            "finalizada",
            mesero=self.mesero,
        )
        mesa.refresh_from_db()
        self.assertEqual(mesa.estado, Mesa.ESTADO_PAGADA)

        self.service.liberar(mesa, mesero=self.mesero)
        mesa.refresh_from_db()
        self.assertEqual(mesa.estado, Mesa.ESTADO_LIBRE)
        self.assertIsNone(mesa.pedido_actual_id)
        self.assertIsNone(mesa.usuario_actual_id)

    def test_no_permita_liberar_con_pago_pendiente(self):
        mesa = Mesa.objects.create(numero_mesa=4, nombre="Caja", capacidad=4, activa=True)
        self.service.seleccionar_para_cliente(self.cliente, mesa_id=mesa.id)
        pedido = PedidoEncabezado.objects.create(
            id_usuario=self.cliente,
            id_restaurante=1,
            total_pedido=21000,
            mesa=mesa,
        )
        self.service.ocupar_con_pedido(mesa, pedido, cliente=self.cliente)
        SolicitudPago.objects.create(
            id_pedido=pedido,
            id_usuario=self.cliente,
            mesa=mesa,
            metodo_pago="Efectivo",
            estado="pendiente",
        )

        with self.assertRaisesMessage(ValueError, "No se puede liberar una mesa con pago pendiente."):
            self.service.liberar(mesa)

    def test_liberacion_forzada_cierra_pago_activo_y_libera(self):
        mesa = Mesa.objects.create(numero_mesa=5, nombre="Forzada", capacidad=4, activa=True)
        self.service.seleccionar_para_cliente(self.cliente, mesa_id=mesa.id)
        pedido = PedidoEncabezado.objects.create(
            id_usuario=self.cliente,
            id_restaurante=1,
            total_pedido=18000,
            mesa=mesa,
        )
        self.service.ocupar_con_pedido(mesa, pedido, cliente=self.cliente)
        solicitud = SolicitudPago.objects.create(
            id_pedido=pedido,
            id_usuario=self.cliente,
            mesa=mesa,
            metodo_pago="Tarjeta / datafono",
            estado="pendiente",
        )

        self.service.liberar(mesa, forzada=True, mesero=self.admin)
        mesa.refresh_from_db()
        solicitud.refresh_from_db()

        self.assertEqual(mesa.estado, Mesa.ESTADO_LIBRE)
        self.assertEqual(solicitud.estado, "finalizada")
        self.assertIsNotNone(solicitud.finalizado_en)

    def test_api_liberar_mesa_despues_de_pago_confirmado(self):
        mesa = Mesa.objects.create(numero_mesa=6, nombre="Terraza", capacidad=4, activa=True)
        self.service.seleccionar_para_cliente(self.cliente, mesa_id=mesa.id)
        pedido = PedidoEncabezado.objects.create(
            id_usuario=self.cliente,
            id_restaurante=1,
            total_pedido=30000,
            mesa=mesa,
        )
        self.service.ocupar_con_pedido(mesa, pedido, cliente=self.cliente)
        SolicitudPago.objects.create(
            id_pedido=pedido,
            id_usuario=self.cliente,
            mesa=mesa,
            metodo_pago="Tarjeta / datafono",
            estado="pendiente",
        )
        SolicitudPagoService().actualizar_estado(
            SolicitudPago.objects.get(mesa=mesa).id_solicitud_pago,
            "finalizada",
            mesero=self.admin,
        )
        self._login_session(self.admin)
        mesa.refresh_from_db()
        self.assertEqual(mesa.estado, Mesa.ESTADO_PAGADA)

        liberar = self.client.post(
            f"/api/mesas/{mesa.id}/liberar",
            data="{}",
            content_type="application/json",
        )
        self.assertEqual(liberar.status_code, 200)
        mesa.refresh_from_db()
        self.assertEqual(mesa.estado, Mesa.ESTADO_LIBRE)

    def test_api_admin_puede_liberar_mesa_en_esperando_pago(self):
        mesa = Mesa.objects.create(numero_mesa=9, nombre="Admin", capacidad=4, activa=True)
        self.service.seleccionar_para_cliente(self.cliente, mesa_id=mesa.id)
        pedido = PedidoEncabezado.objects.create(
            id_usuario=self.cliente,
            id_restaurante=1,
            total_pedido=33000,
            mesa=mesa,
        )
        self.service.ocupar_con_pedido(mesa, pedido, cliente=self.cliente)
        SolicitudPago.objects.create(
            id_pedido=pedido,
            id_usuario=self.cliente,
            mesa=mesa,
            metodo_pago="Efectivo",
            estado="pendiente",
        )
        self._login_session(self.admin)

        liberar = self.client.post(
            f"/api/mesas/{mesa.id}/liberar",
            data="{}",
            content_type="application/json",
        )

        self.assertEqual(liberar.status_code, 200)
        mesa.refresh_from_db()
        self.assertEqual(mesa.estado, Mesa.ESTADO_LIBRE)
        self.assertFalse(SolicitudPago.objects.filter(mesa=mesa).exclude(estado="finalizada").exists())

    def test_api_limpiar_cache_mesas_retorna_snapshot(self):
        Mesa.objects.create(numero_mesa=10, nombre="Cache", capacidad=4, activa=True)
        self._login_session(self.admin)

        response = self.client.post(
            "/api/mesas/limpiar-cache",
            data="{}",
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["ok"])
        self.assertIn("snapshot", data)

    def test_api_listar_oculta_mesas_inactivas_a_cliente(self):
        activa = Mesa.objects.create(numero_mesa=1, nombre="A", capacidad=4, activa=True)
        inactiva = Mesa.objects.create(
            numero_mesa=2,
            nombre="B",
            capacidad=4,
            activa=False,
            estado=Mesa.ESTADO_BLOQUEADA,
        )
        self._login_session(self.cliente)

        response = self.client.get("/api/mesas")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        ids = {item["id"] for item in data}
        self.assertIn(activa.id, ids)
        self.assertNotIn(inactiva.id, ids)

    def test_api_no_permite_seleccionar_mesa_bloqueada(self):
        mesa = Mesa.objects.create(
            numero_mesa=7,
            nombre="Fuera de servicio",
            capacidad=4,
            activa=False,
            estado=Mesa.ESTADO_BLOQUEADA,
        )
        self._login_session(self.cliente)

        response = self.client.post(
            "/api/mesas/seleccionar",
            data=f'{{"mesa_id": {mesa.id}}}',
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
