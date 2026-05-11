// Pantalla de acciones posteriores al carrito: pago, musica y mesero.
import 'dart:async';

import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:web_socket_channel/io.dart';

import '../app_theme.dart';
import '../api_config.dart';
import '../services/bongusto_api.dart';
import '../services/session_service.dart';
import 'app_settings_controls.dart';
import 'carrito_global.dart';
import 'conocenos_screen.dart';
import 'mesero_screen.dart';
import 'metodos_screen.dart';
import 'musica_screen.dart';

// Widget que reune accesos rapidos relacionados con la experiencia del pedido.
class OpcionesPedidoScreen extends StatefulWidget {
  const OpcionesPedidoScreen({super.key});

  @override
  State<OpcionesPedidoScreen> createState() => _OpcionesPedidoScreenState();
}

class _OpcionesPedidoScreenState extends State<OpcionesPedidoScreen> {
  IOWebSocketChannel? _operationChannel;
  Timer? _reconnectTimer;
  String _mesaEstado = '';
  String _mesaLabelActual = '';

  static Color get _pageBg => AppThemeColors.bg;
  static Color get _card => AppThemeColors.surface;
  static Color get _ink => AppThemeColors.text;
  static Color get _muted => AppThemeColors.muted;
  static const _accent = Color(0xFFD90416);
  static Color get _line => AppThemeColors.line;

  Future<void> _abrirReservaWhatsapp() async {
    const numero = '573001112233';
    const mensaje =
        'Hola, quiero reservar en Santa Juana. Me gustaria conocer disponibilidad.';
    final url = Uri.parse(
      'https://wa.me/$numero?text=${Uri.encodeComponent(mensaje)}',
    );
    await launchUrl(url, mode: LaunchMode.externalApplication);
  }

  @override
  void initState() {
    super.initState();
    _mesaLabelActual = _mesaLabelDesdeSesion();
    _refrescarOperacion();
    _conectarOperacionLive();
  }

  @override
  void dispose() {
    _reconnectTimer?.cancel();
    _operationChannel?.sink.close();
    super.dispose();
  }

  String _mesaLabelDesdeSesion() {
    return SessionService.mesaLabel.trim().isEmpty
        ? (SessionService.mesaId != null
              ? 'Mesa ${SessionService.mesaNumero ?? SessionService.mesaId}'
              : 'Mesa no asignada')
        : SessionService.mesaLabel;
  }

  Future<void> _refrescarOperacion() async {
    if (!SessionService.estaAutenticado) return;
    try {
      final snapshot = await BongustoApi.obtenerSnapshotOperacion();
      final mesas = (snapshot['mesas'] as List<dynamic>? ?? const <dynamic>[]);
      final mesa = mesas.isEmpty ? null : Map<String, dynamic>.from(mesas.first as Map);
      if (mesa != null && mesa['id'] != null) {
        await SessionService.guardarMesa(mesa);
      }
      if (!mounted) return;
      setState(() {
        _mesaLabelActual = _mesaLabelDesdeSesion();
        _mesaEstado = (mesa?['estado'] ?? '').toString().trim();
      });
    } catch (_) {}
  }

  void _conectarOperacionLive() {
    _reconnectTimer?.cancel();
    _operationChannel?.sink.close();
    if (!SessionService.estaAutenticado || SessionService.apiToken.isEmpty) {
      return;
    }

    try {
      final wsScheme = ApiConfig.baseUrl.startsWith('https') ? 'wss' : 'ws';
      final wsPort = int.tryParse(ApiConfig.port);
      if (wsPort == null) {
        throw Exception('Puerto WS invalido');
      }
      final uri = Uri(
        scheme: wsScheme,
        host: ApiConfig.host,
        port: wsPort,
        path: '/ws/operacion/mesas/',
        queryParameters: <String, String>{'token': SessionService.apiToken},
      );
      final channel = IOWebSocketChannel.connect(uri);
      _operationChannel = channel;
      channel.stream.listen(
        (_) => _refrescarOperacion(),
        onDone: _programarReconexion,
        onError: (_) => _programarReconexion(),
      );
    } catch (_) {
      _programarReconexion();
    }
  }

  void _programarReconexion() {
    if (!mounted) return;
    _reconnectTimer?.cancel();
    _reconnectTimer = Timer(const Duration(seconds: 2), _conectarOperacionLive);
  }

  String _estadoMesaLabel() {
    final estado = _mesaEstado.toLowerCase().trim();
    if (estado == 'ocupada') return 'Ocupada';
    if (estado == 'esperando_pago') return 'Esperando pago';
    if (estado == 'pagada') return 'Pagada';
    if (estado == 'en_limpieza') return 'En limpieza';
    if (estado == 'libre') return 'Libre';
    if (estado == 'bloqueada') return 'No disponible';
    return '';
  }

  @override
  Widget build(BuildContext context) {
    final total = CarritoGlobal.calcularTotal();
    final totalItems = CarritoGlobal.totalItems();
    final mesaLabel = _mesaLabelActual.isEmpty ? _mesaLabelDesdeSesion() : _mesaLabelActual;
    final estadoMesa = _estadoMesaLabel();

    return Scaffold(
      backgroundColor: _pageBg,
      appBar: AppBar(
        backgroundColor: _pageBg,
        foregroundColor: _ink,
        title: Text('Tu pedido', style: TextStyle(fontWeight: FontWeight.w800)),
        actions: [
          Padding(
            padding: const EdgeInsets.only(right: 12),
            child: AppSettingsControls(),
          ),
        ],
      ),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.fromLTRB(20, 8, 20, 28),
          children: [
            Container(
              padding: const EdgeInsets.all(22),
              decoration: BoxDecoration(
                color: _card,
                borderRadius: BorderRadius.circular(28),
                border: Border.all(color: _line),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'SIGUIENTE PASO',
                    style: TextStyle(
                      color: _accent,
                      fontSize: 12,
                      letterSpacing: 3,
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Elige lo que necesitas ahora',
                    style: TextStyle(
                      color: _ink,
                      fontSize: 30,
                      height: 1.08,
                      fontWeight: FontWeight.w900,
                    ),
                  ),
                  const SizedBox(height: 10),
                  Text(
                    'Ya tienes productos en el carrito. Desde aqui puedes pedir musica, llamar al mesero, reservar, conocer mas del restaurante o terminar en pagar.',
                    style: TextStyle(color: _muted, fontSize: 14, height: 1.5),
                  ),
                  const SizedBox(height: 18),
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 16,
                      vertical: 14,
                    ),
                    decoration: BoxDecoration(
                      color: const Color(0xFFF8F8FA),
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: Row(
                      children: [
                        _pill(
                          icon: Icons.shopping_bag_outlined,
                          label: '$totalItems items',
                        ),
                        const SizedBox(width: 10),
                        Expanded(
                          child: Text(
                            'Total: \$${total.toStringAsFixed(0)}',
                            textAlign: TextAlign.right,
                            style: TextStyle(
                              color: _ink,
                              fontSize: 18,
                              fontWeight: FontWeight.w800,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 12),
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.symmetric(
                      horizontal: 16,
                      vertical: 14,
                    ),
                    decoration: BoxDecoration(
                      color: const Color(0xFFFFECEE),
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(color: const Color(0xFFFFD7DC)),
                    ),
                    child: Row(
                      children: [
                        Container(
                          width: 44,
                          height: 44,
                          decoration: BoxDecoration(
                            color: Colors.white,
                            borderRadius: BorderRadius.circular(14),
                          ),
                          child: Icon(
                            Icons.table_restaurant_rounded,
                            color: _accent,
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                'Tu mesa actual',
                                style: TextStyle(
                                  color: _muted,
                                  fontSize: 12,
                                  fontWeight: FontWeight.w700,
                                ),
                              ),
                              SizedBox(height: 4),
                              Text(
                                'Esta referencia se usa para pedidos y llamados.',
                                style: TextStyle(
                                  color: _muted,
                                  fontSize: 12,
                                  height: 1.3,
                                ),
                              ),
                            ],
                          ),
                        ),
                        const SizedBox(width: 12),
                        Text(
                          mesaLabel,
                          style: TextStyle(
                            color: _ink,
                            fontSize: 20,
                            fontWeight: FontWeight.w900,
                          ),
                        ),
                      ],
                    ),
                  ),
                  if (estadoMesa.isNotEmpty) ...[
                    const SizedBox(height: 10),
                    Text(
                      'Estado en vivo: $estadoMesa',
                      style: TextStyle(
                        color: _accent,
                        fontSize: 13,
                        fontWeight: FontWeight.w800,
                      ),
                    ),
                  ],
                ],
              ),
            ),
            const SizedBox(height: 18),
            GridView.count(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              crossAxisCount: 2,
              crossAxisSpacing: 14,
              mainAxisSpacing: 14,
              childAspectRatio: 0.66,
              children: [
                _optionCard(
                  context,
                  title: 'Pedir musica',
                  subtitle: 'Solicita una cancion.',
                  icon: Icons.music_note_rounded,
                  tint: const Color(0xFFFFF0F1),
                  onTap: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(builder: (_) => const MusicaScreen()),
                    );
                  },
                ),
                _optionCard(
                  context,
                  title: 'Mesero',
                  subtitle: 'Llama al equipo para apoyo inmediato en tu mesa.',
                  icon: Icons.room_service_rounded,
                  tint: const Color(0xFFFFF6EC),
                  onTap: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(builder: (_) => const MeseroScreen()),
                    );
                  },
                ),
                _optionCard(
                  context,
                  title: 'Reservar',
                  subtitle:
                      'Abre WhatsApp para reservar directo con Santa Juana.',
                  icon: Icons.event_available_rounded,
                  tint: const Color(0xFFFFF2E8),
                  onTap: () async {
                    await _abrirReservaWhatsapp();
                  },
                ),
                _optionCard(
                  context,
                  title: 'Conocenos',
                  subtitle:
                      'Explora la historia, estilo y experiencia Santa Juana.',
                  icon: Icons.auto_awesome_outlined,
                  tint: const Color(0xFFF5F2FF),
                  onTap: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(builder: (_) => const ConocenosPage()),
                    );
                  },
                ),
                _optionCard(
                  context,
                  title: 'Pagar',
                  subtitle:
                      'Continua al pago cuando ya hayas finalizado tu experiencia.',
                  icon: Icons.credit_card_rounded,
                  tint: const Color(0xFFFFECEE),
                  prominent: true,
                  onTap: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(builder: (_) => const MetodoPagoPage()),
                    );
                  },
                ),
              ],
            ),
            const SizedBox(height: 18),
            OutlinedButton.icon(
              onPressed: () => Navigator.pop(context),
              style: OutlinedButton.styleFrom(
                foregroundColor: _ink,
                side: BorderSide(color: _line),
                padding: const EdgeInsets.symmetric(vertical: 16),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(16),
                ),
              ),
              icon: Icon(Icons.arrow_back_rounded),
              label: Text('Volver al carrito'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _pill({required IconData icon, required String label}) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(999),
        border: Border.all(color: _line),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 18, color: _accent),
          const SizedBox(width: 8),
          Text(
            label,
            style: TextStyle(color: _ink, fontWeight: FontWeight.w700),
          ),
        ],
      ),
    );
  }

  Widget _optionCard(
    BuildContext context, {
    required String title,
    required String subtitle,
    required IconData icon,
    required Color tint,
    required VoidCallback onTap,
    bool prominent = false,
  }) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(28),
      child: Container(
        padding: const EdgeInsets.all(18),
        decoration: BoxDecoration(
          color: _card,
          borderRadius: BorderRadius.circular(28),
          border: Border.all(color: prominent ? _accent : _line),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.04),
              blurRadius: 14,
              offset: const Offset(0, 8),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              width: 62,
              height: 62,
              decoration: BoxDecoration(
                color: tint,
                borderRadius: BorderRadius.circular(20),
              ),
              child: Icon(icon, color: _accent, size: 30),
            ),
            const Spacer(),
            Text(
              title,
              style: TextStyle(
                color: _ink,
                fontSize: 22,
                height: 1.05,
                fontWeight: FontWeight.w900,
              ),
            ),
            const SizedBox(height: 10),
            Text(
              subtitle,
              maxLines: 5,
              overflow: TextOverflow.fade,
              style: TextStyle(color: _muted, fontSize: 13, height: 1.45),
            ),
            const SizedBox(height: 14),
            const Spacer(),
            Row(
              children: [
                Text(
                  prominent ? 'Ir a pagar' : 'Abrir',
                  style: TextStyle(
                    color: _ink,
                    fontSize: 15,
                    fontWeight: FontWeight.w800,
                  ),
                ),
                const SizedBox(width: 6),
                Icon(Icons.arrow_forward_rounded, size: 18, color: _ink),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
