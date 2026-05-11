"""Pruebas del modulo musica en tiempo real e historial."""

from datetime import timedelta
from unittest.mock import patch

from django.test import TransactionTestCase
from django.utils import timezone

from bongusto.domain.models import Musica, SolicitudMusica, Usuario
from bongusto.modules.mesas.models import Mesa
from bongusto.modules.musica.services import MusicaService


class MusicaModuleTest(TransactionTestCase):
    def setUp(self):
        self.service = MusicaService()
        self.admin = Usuario.objects.create(
            nombre="Admin",
            apellido="Music",
            correo="admin@bongusto.test",
            clave="hash",
            tipo_usuario="administrador",
            estado="Activo",
        )
        self.mesero = Usuario.objects.create(
            nombre="Mesero",
            apellido="Music",
            correo="mesero@bongusto.test",
            clave="hash",
            tipo_usuario="mesero",
            estado="Activo",
        )
        self.cliente = Usuario.objects.create(
            nombre="Cliente",
            apellido="Music",
            correo="cliente@bongusto.test",
            clave="hash",
            tipo_usuario="cliente",
            estado="Activo",
        )
        self.mesa = Mesa.objects.create(numero_mesa=1, nombre="Salon", capacidad=4, activa=True)
        self.musica = Musica.objects.create(
            nombre_musica="Hound Dog",
            artista_musica="Elvis Presley",
            duracion_musica="180",
        )

    def _login_session(self, usuario):
        session = self.client.session
        session["usuario_id"] = usuario.id_usuario
        session["usuario_tipo"] = usuario.tipo_usuario
        session.save()

    def test_agregar_cancion_a_cola(self):
        solicitud = self.service.solicitar(
            usuario=self.cliente,
            musica=self.musica,
            mesa=self.mesa,
        )
        solicitud.refresh_from_db()
        self.assertIn(solicitud.estado_solicitud, {"pendiente", "reproduciendo"})
        self.assertEqual(solicitud.mesa_id, self.mesa.id)
        self.assertEqual(solicitud.cancion, "Hound Dog")

    @patch("bongusto.modules.musica.services.emitir_evento_operacion")
    @patch("bongusto.modules.musica.realtime.emitir_evento_musica")
    def test_reproduccion_automatica_y_cambio_a_reproducida(self, mock_ws, mock_operacion):
        solicitud = self.service.solicitar(
            usuario=self.cliente,
            musica=self.musica,
            mesa=self.mesa,
            duracion_segundos=1,
        )
        self.service.sincronizar_reproduccion()
        solicitud.refresh_from_db()
        self.assertEqual(solicitud.estado_solicitud, "reproduciendo")

        solicitud.fecha_inicio_reproduccion = timezone.now() - timedelta(seconds=5)
        solicitud.save(update_fields=["fecha_inicio_reproduccion"])
        self.service.sincronizar_reproduccion()
        solicitud.refresh_from_db()

        self.assertEqual(solicitud.estado_solicitud, "reproducida")
        self.assertIsNotNone(solicitud.fecha_finalizacion)
        eventos = [call.args[0] for call in mock_ws.call_args_list]
        self.assertIn("cancion_reproducida", eventos)

    def test_historial_conserva_cancion_eliminada_logicamante(self):
        solicitud = self.service.solicitar(
            usuario=self.cliente,
            musica=self.musica,
            mesa=self.mesa,
        )
        self.service.eliminar_solicitud(
            solicitud.id_solicitud,
            admin=self.admin,
            motivo="No aplica",
        )
        solicitud.refresh_from_db()
        self.assertEqual(solicitud.estado_solicitud, "eliminada")
        historial = self.service.historial(estado="eliminada")
        self.assertTrue(any(item["id_solicitud"] == solicitud.id_solicitud for item in historial))

    def test_api_bloquea_eliminacion_para_cliente_y_mesero(self):
        solicitud = self.service.solicitar(
            usuario=self.cliente,
            musica=self.musica,
            mesa=self.mesa,
        )

        self._login_session(self.cliente)
        response = self.client.post(f"/api/musica/{solicitud.id_solicitud}/eliminar")
        self.assertEqual(response.status_code, 403)

        self._login_session(self.mesero)
        response = self.client.post(f"/api/musica/{solicitud.id_solicitud}/eliminar")
        self.assertEqual(response.status_code, 403)

    def test_api_admin_puede_reordenar_cola(self):
        primera = self.service.solicitar(
            usuario=self.cliente,
            cancion="Primera",
            artista="A",
            mesa=self.mesa,
        )
        segunda = self.service.solicitar(
            usuario=self.cliente,
            cancion="Segunda",
            artista="B",
            mesa=self.mesa,
        )
        self._login_session(self.admin)

        response = self.client.post(f"/api/musica/{segunda.id_solicitud}/subir")
        self.assertEqual(response.status_code, 200)
        snapshot = response.json()
        cola = snapshot["cola"]
        pendientes = [item for item in cola if item["estado_solicitud"] == "pendiente"]
        self.assertEqual(pendientes[0]["id_solicitud"], segunda.id_solicitud)
        self.assertNotEqual(primera.id_solicitud, pendientes[0]["id_solicitud"])

    def test_api_cola_y_snapshot(self):
        self.service.solicitar(
            usuario=self.cliente,
            musica=self.musica,
            mesa=self.mesa,
        )
        self._login_session(self.cliente)

        cola_response = self.client.get("/api/musica/cola")
        self.assertEqual(cola_response.status_code, 200)
        self.assertEqual(len(cola_response.json()), 1)

        snapshot_response = self.client.get("/api/musica/snapshot")
        self.assertEqual(snapshot_response.status_code, 200)
        self.assertIn("cola", snapshot_response.json())

    def test_pdf_historial(self):
        self.service.solicitar(
            usuario=self.cliente,
            musica=self.musica,
            mesa=self.mesa,
        )
        self._login_session(self.admin)

        response = self.client.get("/musicas/reporte")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")
