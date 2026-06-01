import json

from django.test import Client, TestCase

from bongusto.domain.models import Menu, Musica, PedidoEncabezado, Producto, Rol, SolicitudPago, SolicitudMusica, Usuario
from bongusto.modules.mesas.models import Mesa
from bongusto.modules.shared.security import hash_contrasena


class BonGustoIntegrationTest(TestCase):
    def setUp(self):
        self.client = Client()

        self.rol_mesero = Rol.objects.create(nombre_rol="Mesero Principal")
        self.cliente_usuario = Usuario.objects.create(
            nombre="Cliente",
            apellido="Prueba",
            correo="cliente.integration@test.com",
            clave=hash_contrasena("ClaveSegura1!"),
            tipo_usuario="cliente",
            estado="Activo",
        )
        self.mesero_usuario = Usuario.objects.create(
            nombre="Mesero",
            apellido="Prueba",
            correo="mesero.integration@test.com",
            clave=hash_contrasena("ClaveSegura1!"),
            tipo_usuario="mesero",
            id_rol=self.rol_mesero,
            estado="Activo",
        )

        self.mesa = Mesa.objects.create(
            numero_mesa=7,
            nombre="Ventana",
            capacidad=4,
            estado=Mesa.ESTADO_LIBRE,
            activa=True,
        )
        self.menu = Menu.objects.create(
            nombre_menu="Principal",
            descripcion_menu="Menu base de integracion",
        )
        self.producto = Producto.objects.create(
            nombre_producto="Hamburguesa BonGusto",
            precio_producto=32000,
            descripcion_producto="Producto de prueba",
            id_menu=self.menu,
            estado="activo",
        )

    def _post_json(self, path, payload, *, token=None):
        extra = {}
        if token:
            extra["HTTP_AUTHORIZATION"] = f"Bearer {token}"
        return self.client.post(
            path,
            data=json.dumps(payload),
            content_type="application/json",
            **extra,
        )

    def _get_json(self, path, *, token=None):
        extra = {}
        if token:
            extra["HTTP_AUTHORIZATION"] = f"Bearer {token}"
        return self.client.get(path, **extra)

    def _login_cliente(self, correo=None, clave="ClaveSegura1!"):
        response = self._post_json(
            "/api/clientes/login",
            {
                "correo": correo or self.cliente_usuario.correo,
                "clave": clave,
            },
        )
        self.assertEqual(response.status_code, 200)
        return response.json()

    def _login_mesero(self):
        response = self._post_json(
            "/api/meseros/login",
            {
                "correo": self.mesero_usuario.correo,
                "clave": "ClaveSegura1!",
            },
        )
        self.assertEqual(response.status_code, 200)
        return response.json()

    def _asignar_mesa_cliente(self, token):
        response = self._post_json(
            "/api/mesas/seleccionar",
            {"mesa_id": self.mesa.id},
            token=token,
        )
        self.assertEqual(response.status_code, 201)
        return response.json()

    def _crear_pedido_cliente(self, token):
        response = self._post_json(
            "/api/pedidos",
            {
                "id_usuario": self.cliente_usuario.id_usuario,
                "mesa_id": self.mesa.id,
                "tipo_pedido": "restaurante",
                "items": [
                    {
                        "id_producto": self.producto.id_producto,
                        "cantidad": 2,
                    }
                ],
            },
            token=token,
        )
        self.assertEqual(response.status_code, 201)
        return response.json()

    def test_integracion_registro_login_y_refresh_cliente(self):
        response = self._post_json(
            "/api/clientes/register",
            {
                "nombre": "Ana Integracion",
                "correo": "ana.integration@test.com",
                "clave": "ClaveSegura1!",
                "telefono": "3001234567",
            },
        )

        self.assertEqual(response.status_code, 201)
        payload_registro = response.json()
        self.assertEqual(payload_registro["correo"], "ana.integration@test.com")
        self.assertTrue(payload_registro["api_token"])

        login = self._post_json(
            "/api/clientes/login",
            {
                "correo": "ana.integration@test.com",
                "clave": "ClaveSegura1!",
            },
        )
        self.assertEqual(login.status_code, 200)
        payload_login = login.json()
        self.assertEqual(payload_login["tipo_usuario"], "cliente")

        refresh = self._get_json(
            "/api/session/refresh",
            token=payload_login["api_token"],
        )
        self.assertEqual(refresh.status_code, 200)
        payload_refresh = refresh.json()
        self.assertEqual(payload_refresh["correo"], "ana.integration@test.com")
        self.assertTrue(payload_refresh["api_token"])

    def test_integracion_cliente_asigna_mesa_y_crea_pedido(self):
        login = self._login_cliente()
        token = login["api_token"]

        mesa_payload = self._asignar_mesa_cliente(token)
        self.assertEqual(mesa_payload["id"], self.mesa.id)
        self.assertEqual(mesa_payload["estado"], Mesa.ESTADO_OCUPADA)

        pedido_payload = self._crear_pedido_cliente(token)
        self.assertEqual(pedido_payload["id_usuario"], self.cliente_usuario.id_usuario)
        self.assertEqual(pedido_payload["mesa_id"], self.mesa.id)
        self.assertEqual(pedido_payload["estado"], "abierto")
        self.assertEqual(len(pedido_payload["items"]), 1)
        self.assertEqual(pedido_payload["items"][0]["cantidad"], 2)

        pedidos = self._get_json(
            f"/api/pedidos?id_usuario={self.cliente_usuario.id_usuario}",
            token=token,
        )
        self.assertEqual(pedidos.status_code, 200)
        pedidos_data = pedidos.json()
        self.assertEqual(len(pedidos_data), 1)
        self.assertEqual(pedidos_data[0]["id_pedido"], pedido_payload["id_pedido"])

        self.mesa.refresh_from_db()
        self.assertEqual(self.mesa.usuario_actual_id, self.cliente_usuario.id_usuario)
        self.assertEqual(self.mesa.pedido_actual_id, pedido_payload["id_pedido"])

    def test_integracion_cliente_solicita_musica_y_aparece_en_cola(self):
        login = self._login_cliente()
        token = login["api_token"]
        self._asignar_mesa_cliente(token)

        response = self._post_json(
            "/api/musica/solicitar",
            {
                "id_usuario": self.cliente_usuario.id_usuario,
                "mesa_id": self.mesa.id,
                "nombre_musica": "Viva BonGusto",
                "artista_musica": "Grupo QA",
            },
            token=token,
        )

        self.assertEqual(response.status_code, 201)
        payload = response.json()
        self.assertEqual(payload["cliente_id"], self.cliente_usuario.id_usuario)
        self.assertEqual(payload["mesa_id"], self.mesa.id)
        self.assertIn(payload["estado_solicitud"], {"pendiente", "reproduciendo"})

        cola = self._get_json("/api/musica/cola", token=token)
        self.assertEqual(cola.status_code, 200)
        cola_data = cola.json()
        self.assertTrue(any(item["id_solicitud"] == payload["id_solicitud"] for item in cola_data))

        self.assertTrue(
            Musica.objects.filter(
                nombre_musica="Viva BonGusto",
                artista_musica="Grupo QA",
            ).exists()
        )
        self.assertTrue(SolicitudMusica.objects.filter(pk=payload["id_solicitud"]).exists())

    def test_integracion_cliente_solicita_pago_y_mesero_lo_finaliza(self):
        login_cliente = self._login_cliente()
        token_cliente = login_cliente["api_token"]
        self._asignar_mesa_cliente(token_cliente)
        pedido_payload = self._crear_pedido_cliente(token_cliente)

        solicitud_pago = self._post_json(
            "/api/pagos/solicitudes",
            {
                "id_pedido": pedido_payload["id_pedido"],
                "mesa_id": self.mesa.id,
                "metodo_pago": "efectivo",
            },
            token=token_cliente,
        )
        self.assertEqual(solicitud_pago.status_code, 201)
        pago_payload = solicitud_pago.json()
        self.assertEqual(pago_payload["estado"], "pendiente")
        self.assertEqual(pago_payload["mesa_id"], self.mesa.id)

        login_mesero = self._login_mesero()
        token_mesero = login_mesero["api_token"]

        listado = self._get_json("/api/pagos/solicitudes", token=token_mesero)
        self.assertEqual(listado.status_code, 200)
        self.assertTrue(any(item["id_solicitud_pago"] == pago_payload["id_solicitud_pago"] for item in listado.json()))

        finalizar = self._post_json(
            f"/api/pagos/solicitudes/{pago_payload['id_solicitud_pago']}/estado",
            {"estado": "finalizada"},
            token=token_mesero,
        )
        self.assertEqual(finalizar.status_code, 200)
        finalizar_payload = finalizar.json()
        self.assertEqual(finalizar_payload["estado"], "finalizada")
        self.assertEqual(finalizar_payload["id_mesero_atendio"], self.mesero_usuario.id_usuario)

        self.mesa.refresh_from_db()
        pedido = PedidoEncabezado.objects.get(pk=pedido_payload["id_pedido"])
        solicitud = SolicitudPago.objects.get(pk=pago_payload["id_solicitud_pago"])

        self.assertEqual(self.mesa.estado, Mesa.ESTADO_PAGADA)
        self.assertEqual(pedido.estado_pedido, "finalizado")
        self.assertEqual(solicitud.estado, "finalizada")

    def test_integracion_mesero_consulta_snapshot_operativo(self):
        login_cliente = self._login_cliente()
        token_cliente = login_cliente["api_token"]
        self._asignar_mesa_cliente(token_cliente)
        self._crear_pedido_cliente(token_cliente)

        login_mesero = self._login_mesero()
        token_mesero = login_mesero["api_token"]

        response = self._get_json("/api/operacion/snapshot", token=token_mesero)

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("mesas", payload)
        self.assertIn("kpis", payload)
        self.assertTrue(any(mesa["id"] == self.mesa.id for mesa in payload["mesas"]))
