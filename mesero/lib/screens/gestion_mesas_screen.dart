// ===== Pantalla `gestion_mesas_screen.dart` | Presenta las mesas reales y su estado operativo en tiempo real. =====
import 'dart:async';

import 'package:flutter/material.dart';
import 'package:web_socket_channel/io.dart';

import '../api_config.dart';
import '../services/bongusto_api.dart';
import '../services/session_service.dart';
import 'mesa_detail_screen.dart';
import 'mesa_model.dart';

// ===== Clase `GestionMesasScreen` | Define la vista principal del modulo de mesas. =====
class GestionMesasScreen extends StatefulWidget {
  const GestionMesasScreen({super.key});

  @override
  State<GestionMesasScreen> createState() => _GestionMesasScreenState();
}

// ===== Estado `_GestionMesasScreenState` | Consulta las mesas reales, su pedido y pago asociado, y abre su detalle. =====
class _GestionMesasScreenState extends State<GestionMesasScreen> {
  static const kBrandRed = Color(0xFFD90416);
  static const kGreen = Color(0xFFDDF4D7);
  static const kGray = Color(0xFFECEAF0);
  static const kPageBgLight = Color(0xFFF2F1F4);
  static const kPageBgDark = Color(0xFF101218);
  static const kCard = Color(0xFFFFFFFF);
  static const kInk = Color(0xFF181818);
  static const kMuted = Color(0xFF73727A);
  static const kLine = Color(0xFFE8E6EB);

  bool _loading = true;
  String _error = '';
  List<Mesa> _mesas = <Mesa>[];
  List<Map<String, dynamic>> _pedidos = <Map<String, dynamic>>[];
  List<Map<String, dynamic>> _pedidosParaLlevar = <Map<String, dynamic>>[];
  Timer? _refreshTimer;
  Timer? _reconnectTimer;
  bool _requestInFlight = false;
  IOWebSocketChannel? _operationChannel;
  bool _socketConectado = false;
  late final _MesasLifecycleObserver _lifecycleObserver;
  bool get _isDark => Theme.of(context).brightness == Brightness.dark;
  Color get _bg => _isDark ? kPageBgDark : kPageBgLight;

  @override
  void initState() {
    super.initState();
    _lifecycleObserver = _MesasLifecycleObserver(onResume: _onResume);
    WidgetsBinding.instance.addObserver(_lifecycleObserver);
    _cargarMesas();
    _conectarOperacionLive();
    _refreshTimer = Timer.periodic(const Duration(seconds: 8), (_) {
      _cargarMesas(silent: true);
    });
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(_lifecycleObserver);
    _refreshTimer?.cancel();
    _reconnectTimer?.cancel();
    _operationChannel?.sink.close();
    super.dispose();
  }

  void _onResume() {
    if (!_socketConectado) {
      _conectarOperacionLive();
    }
    _cargarMesas(silent: true);
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
      _socketConectado = true;

      channel.stream.listen(
        (dynamic event) {
          if (!mounted) return;
          final payload = event.toString();
          if (payload.contains('"type":"snapshot"') ||
              payload.contains('"type": "snapshot"') ||
              payload.contains('"type":"event"') ||
              payload.contains('"type": "event"')) {
            _cargarMesas(silent: true);
          }
        },
        onDone: _programarReconexion,
        onError: (_) => _programarReconexion(),
      );
    } catch (_) {
      _programarReconexion();
    }
  }

  void _programarReconexion() {
    _socketConectado = false;
    if (!mounted) return;
    _reconnectTimer?.cancel();
    _reconnectTimer = Timer(const Duration(seconds: 2), _conectarOperacionLive);
  }

  Future<void> _cargarMesas({bool silent = false}) async {
    if (_requestInFlight) return;
    _requestInFlight = true;
    if (!silent) {
      setState(() {
        _loading = true;
        _error = '';
      });
    }

    try {
      final resultados = await Future.wait([
        BongustoApi.obtenerMesas(),
        BongustoApi.obtenerPedidos(),
        BongustoApi.obtenerSolicitudesPago(),
      ]);
      Map<String, dynamic> snapshotOperacion = <String, dynamic>{};
      try {
        snapshotOperacion = await BongustoApi.obtenerSnapshotOperacion();
      } catch (_) {}
      final mesasApi = resultados[0];
      final pedidos = resultados[1];
      final pagos = resultados[2];
      if (!mounted) return;

      setState(() {
        _mesas = _mapearMesasYPedidos(mesasApi, pedidos, pagos);
        _pedidos = pedidos;
        _pedidosParaLlevar = (snapshotOperacion['pedidos_para_llevar'] as List<dynamic>? ?? const <dynamic>[])
            .whereType<Map>()
            .map((pedido) => Map<String, dynamic>.from(pedido))
            .toList(growable: false);
        _loading = false;
        _error = '';
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _mesas = <Mesa>[];
        _error = '$e';
        _loading = false;
      });
    } finally {
      _requestInFlight = false;
    }
  }

  List<Mesa> _mapearMesasYPedidos(
    List<Map<String, dynamic>> mesasApi,
    List<Map<String, dynamic>> pedidos,
    List<Map<String, dynamic>> pagos,
  ) {
    final mesas = <int, Mesa>{};
    final pedidoActualPorMesa = <int, int>{};

    for (final rawMesa in mesasApi) {
      final mesaMap = Map<String, dynamic>.from(rawMesa);
      final mesaId = _asInt(mesaMap['id']);
      if (mesaId <= 0) continue;
      final mesa = Mesa(
        id: mesaId,
        numeroMesa: _asInt(mesaMap['numero_mesa']) > 0 ? _asInt(mesaMap['numero_mesa']) : mesaId,
        etiqueta: (mesaMap['etiqueta'] ?? '').toString().trim().isNotEmpty
            ? (mesaMap['etiqueta'] ?? '').toString()
            : 'Mesa ${_asInt(mesaMap['numero_mesa']) > 0 ? _asInt(mesaMap['numero_mesa']) : mesaId}',
        capacidad: _asInt(mesaMap['capacidad']),
        activa: mesaMap['activa'] != false,
      );
      mesas[mesaId] = mesa;
      final pedidoActualId = _asInt(
        mesaMap['pedido_actual_id'] ?? mesaMap['pedido_actual'],
      );
      if (pedidoActualId > 0) {
        pedidoActualPorMesa[mesaId] = pedidoActualId;
      }
      mesa.idUsuario = _asInt(mesaMap['id_usuario']);
      mesa.asignadoEn = (mesaMap['asignado_en'] ?? '').toString();
      mesa.reserva = mesaMap['reserva'] is Map ? Map<String, dynamic>.from(mesaMap['reserva'] as Map) : null;
      final cliente = (mesaMap['cliente_nombre'] ?? '').toString().trim();
      final estado = (mesaMap['estado'] ?? 'libre').toString().trim().toLowerCase();
      if (estado == 'esperando_pago') {
        mesa.status = TableStatus.esperandoPago;
      } else if (estado == 'ocupada') {
        mesa.status = TableStatus.ocupada;
      } else if (estado == 'pagada') {
        mesa.status = TableStatus.pagada;
      } else if (estado == 'en_limpieza') {
        mesa.status = TableStatus.enLimpieza;
      } else if (estado == 'bloqueada') {
        mesa.status = TableStatus.bloqueada;
      } else {
        mesa.status = TableStatus.libre;
      }

      if (cliente.isNotEmpty) {
        mesa.clientes.add(cliente);
      }
      if (mesaMap['pago'] is Map) {
        mesa.pago = Map<String, dynamic>.from(mesaMap['pago'] as Map);
      }
    }

    final pedidosPorMesa = <int, List<Map<String, dynamic>>>{};
    for (final pedido in pedidos) {
      final mesaId = _resolverMesaId(pedido);
      if (mesaId <= 0 || !mesas.containsKey(mesaId)) continue;
      pedidosPorMesa.putIfAbsent(mesaId, () => <Map<String, dynamic>>[]);
      pedidosPorMesa[mesaId]!.add(Map<String, dynamic>.from(pedido));
    }

    for (final mesa in mesas.values) {
      final pedidosMesa = pedidosPorMesa[mesa.id] ?? const <Map<String, dynamic>>[];
      final mesaBloqueadaOLibre =
          mesa.status == TableStatus.libre || mesa.status == TableStatus.bloqueada;
      final pedidoActualId = pedidoActualPorMesa[mesa.id] ?? 0;
      if (!mesaBloqueadaOLibre && pedidosMesa.isNotEmpty) {
        Map<String, dynamic>? pedidoActual;
        if (pedidoActualId > 0) {
          for (final pedido in pedidosMesa) {
            if (_asInt(pedido['id_pedido']) == pedidoActualId) {
              pedidoActual = pedido;
              break;
            }
          }
        }
        pedidoActual ??= pedidosMesa.reduce((actual, siguiente) {
          final actualId = _asInt(actual['id_pedido']);
          final siguienteId = _asInt(siguiente['id_pedido']);
          return siguienteId > actualId ? siguiente : actual;
        });
        mesa.pedidos = <Map<String, dynamic>>[Map<String, dynamic>.from(pedidoActual)];
        final cliente = (pedidoActual['cliente_nombre'] ?? '').toString().trim();
        mesa.clientes = cliente.isEmpty ? <String>[] : <String>[cliente];

        final items = (pedidoActual['items'] as List<dynamic>? ?? const <dynamic>[]);
        mesa.pendientes.clear();
        for (final rawItem in items) {
          final item = Map<String, dynamic>.from(rawItem as Map);
          final nombre = (item['nombre_producto'] ?? 'Producto').toString();
          final cantidad = _asInt(item['cantidad']);
          mesa.pendientes[nombre] = cantidad;
        }
      } else {
        mesa.pedidos.clear();
        mesa.pendientes.clear();
        if (mesa.status == TableStatus.libre || mesa.status == TableStatus.bloqueada) {
          mesa.clientes.clear();
        }
      }
    }

    for (final pago in pagos) {
      final pagoMap = Map<String, dynamic>.from(pago);
      if ((pagoMap['estado'] ?? '').toString().toLowerCase() == 'finalizada') {
        continue;
      }
      final mesaId = _asInt(pagoMap['mesa_id']);
      final mesa = mesas[mesaId];
      if (mesa == null) continue;
      mesa.pago = pagoMap;
      mesa.status = TableStatus.esperandoPago;
      final cliente = (pagoMap['cliente_nombre'] ?? '').toString().trim();
      if (cliente.isNotEmpty && mesa.clientes.isEmpty) {
        mesa.clientes = <String>[cliente];
      }
    }

    final lista = mesas.values.toList()
      ..sort((a, b) => a.numeroMesa.compareTo(b.numeroMesa));
    return lista;
  }

  int _resolverMesaId(Map<String, dynamic> pedido) {
    final mesaExplicita = _asInt(
      pedido['id_mesa'] ?? pedido['mesa_id'] ?? pedido['numero_mesa'],
    );
    if (mesaExplicita > 0) {
      return mesaExplicita;
    }
    return 0;
  }

  int _asInt(dynamic value) {
    if (value is int) return value;
    return int.tryParse('$value') ?? 0;
  }

  double _asDouble(dynamic value) {
    if (value is num) return value.toDouble();
    return double.tryParse('$value') ?? 0.0;
  }

  Color _color(Mesa mesa) {
    switch (mesa.status) {
      case TableStatus.libre:
        return kGray;
      case TableStatus.ocupada:
        return const Color(0xFFFFD6DB);
      case TableStatus.esperandoPago:
        return const Color(0xFFFFF0B8);
      case TableStatus.pagada:
        return const Color(0xFFE5EBFF);
      case TableStatus.enLimpieza:
        return const Color(0xFFE5F4FF);
      case TableStatus.bloqueada:
        return const Color(0xFFE9E7EC);
    }
  }

  String _statusLabel(Mesa mesa) {
    switch (mesa.status) {
      case TableStatus.libre:
        return 'Disponible';
      case TableStatus.ocupada:
        return 'Ocupada';
      case TableStatus.esperandoPago:
        return 'Pago solicitado';
      case TableStatus.pagada:
        return 'Pagada';
      case TableStatus.enLimpieza:
        return 'En limpieza';
      case TableStatus.bloqueada:
        return 'Bloqueada';
    }
  }

  Color _takeoutChipColor(String estado) {
    switch (estado) {
      case 'en_preparacion':
        return const Color(0xFFFFF0B8);
      case 'listo_para_recoger':
        return const Color(0xFFE5EBFF);
      case 'entregado':
      case 'finalizado':
        return const Color(0xFFE8F5EA);
      case 'pagado':
        return const Color(0xFFEDF9F1);
      default:
        return const Color(0xFFF3F1F7);
    }
  }

  Color _takeoutChipTextColor(String estado) {
    switch (estado) {
      case 'en_preparacion':
        return const Color(0xFF9B6500);
      case 'listo_para_recoger':
        return const Color(0xFF405AA8);
      case 'entregado':
      case 'finalizado':
      case 'pagado':
        return const Color(0xFF2F7A4F);
      default:
        return kInk;
    }
  }

  Widget _hero() {
    return Container(
      padding: const EdgeInsets.all(22),
      decoration: BoxDecoration(
        color: kCard,
        borderRadius: BorderRadius.circular(30),
        border: Border.all(color: kLine),
      ),
      child: const Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'MESAS',
            style: TextStyle(
              color: kBrandRed,
              fontSize: 12,
              letterSpacing: 3,
              fontWeight: FontWeight.w800,
            ),
          ),
          SizedBox(height: 8),
          Text(
            'mesas conectadas al flujo del cliente',
            style: TextStyle(
              color: kInk,
              fontSize: 28,
              height: 1.08,
              fontWeight: FontWeight.w900,
            ),
          ),
          SizedBox(height: 10),
          Text(
            'Cada pedido se asigna a una de las mesas para que el mesero vea a que cliente y productos al que pertenece.',
            style: TextStyle(
              color: kMuted,
              fontSize: 14,
              height: 1.5,
            ),
          ),
        ],
      ),
    );
  }

  Widget _stateCard({required IconData icon, required String text}) {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: kCard,
        borderRadius: BorderRadius.circular(28),
        border: Border.all(color: kLine),
      ),
      child: Column(
        children: [
          Icon(icon, size: 48, color: kBrandRed),
          const SizedBox(height: 12),
          Text(
            text,
            textAlign: TextAlign.center,
            style: const TextStyle(color: kInk),
          ),
          if (_error.isNotEmpty) ...[
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: _cargarMesas,
              child: const Text('Reintentar'),
            ),
          ],
        ],
      ),
    );
  }

  Widget _takeoutPanel() {
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: kCard,
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: kLine),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.05),
            blurRadius: 14,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'PEDIDOS PARA LLEVAR',
            style: TextStyle(
              color: kBrandRed,
              fontSize: 12,
              letterSpacing: 3,
              fontWeight: FontWeight.w800,
            ),
          ),
          const SizedBox(height: 12),
          const Text(
            'Pedidos sin mesa que se gestionan desde la misma operacion del restaurante.',
            style: TextStyle(
              color: kInk,
              fontSize: 18,
              height: 1.15,
              fontWeight: FontWeight.w900,
            ),
          ),
          const SizedBox(height: 8),
          const Text(
            'Mantienen el mismo estilo visual de BonGusto y se actualizan en tiempo real.',
            style: TextStyle(
              color: kMuted,
              fontSize: 13,
              height: 1.45,
            ),
          ),
          const SizedBox(height: 14),
          if (_pedidosParaLlevar.isEmpty)
            const Text(
              'No hay pedidos para llevar activos.',
              style: TextStyle(color: kMuted),
            )
          else
            Wrap(
              spacing: 12,
              runSpacing: 12,
              children: _pedidosParaLlevar.map((pedido) => _takeoutCard(pedido)).toList(),
            ),
        ],
      ),
    );
  }

  Widget _takeoutCard(Map<String, dynamic> pedido) {
    final estado = (pedido['estado'] ?? 'abierto').toString();
    final pago = pedido['pago'] is Map ? Map<String, dynamic>.from(pedido['pago'] as Map) : null;
    final pagoMetodo = (pago == null ? 'Sin solicitud' : (pago['metodo_pago'] ?? 'Sin solicitud')).toString();
    final pagoEstado = (pago == null || pago['estado'] == null) ? '' : ' - ${pago['estado']}';
    return ConstrainedBox(
      constraints: const BoxConstraints(minWidth: 280, maxWidth: 380),
      child: Container(
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: const Color(0xFFFFFFFF),
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: kLine),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.04),
              blurRadius: 10,
              offset: const Offset(0, 6),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Text(
                    '#${pedido['id_pedido'] ?? '-'} - ${pedido['cliente_nombre'] ?? 'Cliente'}',
                    style: const TextStyle(
                      color: kInk,
                      fontSize: 16,
                      fontWeight: FontWeight.w900,
                    ),
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                  decoration: BoxDecoration(
                    color: _takeoutChipColor(estado),
                    borderRadius: BorderRadius.circular(999),
                  ),
                  child: Text(
                    estado.replaceAll('_', ' '),
                    style: TextStyle(
                      fontSize: 11,
                      fontWeight: FontWeight.w800,
                      color: _takeoutChipTextColor(estado),
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text('Total: \$${(_asDouble(pedido['total_pedido']) ).toStringAsFixed(0)}', style: const TextStyle(fontWeight: FontWeight.w800)),
            Text('Fecha: ${pedido['fecha_pedido'] ?? '-'}', style: const TextStyle(color: kMuted)),
            Text(
              'Pago: $pagoMetodo$pagoEstado',
              style: const TextStyle(color: kMuted),
            ),
            const SizedBox(height: 10),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                OutlinedButton(
                  onPressed: () => _verPedidoParaLlevar(pedido),
                  style: OutlinedButton.styleFrom(
                    foregroundColor: kInk,
                    side: const BorderSide(color: kLine),
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 12),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                  ),
                  child: const Text('Ver detalle'),
                ),
                OutlinedButton(
                  onPressed: () => _actualizarPedidoParaLlevar(pedido, 'en_preparacion'),
                  style: OutlinedButton.styleFrom(
                    foregroundColor: kInk,
                    side: const BorderSide(color: kLine),
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 12),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                  ),
                  child: const Text('En preparacion'),
                ),
                OutlinedButton(
                  onPressed: () => _actualizarPedidoParaLlevar(pedido, 'listo_para_recoger'),
                  style: OutlinedButton.styleFrom(
                    foregroundColor: kInk,
                    side: const BorderSide(color: kLine),
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 12),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                  ),
                  child: const Text('Listo para recoger'),
                ),
                OutlinedButton(
                  onPressed: () => _actualizarPedidoParaLlevar(pedido, 'entregado'),
                  style: OutlinedButton.styleFrom(
                    foregroundColor: kInk,
                    side: const BorderSide(color: kLine),
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 12),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                  ),
                  child: const Text('Entregado'),
                ),
                ElevatedButton(
                  onPressed: () => _confirmarPagoParaLlevar(pedido),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: kBrandRed,
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                  ),
                  child: const Text('Confirmar pago'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _verPedidoParaLlevar(Map<String, dynamic> pedido) async {
    final pedidoId = _asInt(pedido['id_pedido']);
    final detalle = _pedidos.where((item) => _asInt(item['id_pedido']) == pedidoId).toList();
    if (!mounted) return;
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.white,
      showDragHandle: true,
      builder: (_) {
        final pedidoData = detalle.isNotEmpty ? detalle.first : pedido;
        final items = (pedidoData['items'] as List<dynamic>? ?? const <dynamic>[]);
        return Padding(
          padding: const EdgeInsets.all(18),
          child: ListView(
            shrinkWrap: true,
            children: [
              Text('#${pedidoData['id_pedido'] ?? '-'}', style: const TextStyle(fontSize: 22, fontWeight: FontWeight.w900)),
              const SizedBox(height: 8),
              Text(pedidoData['cliente_nombre']?.toString() ?? 'Cliente'),
              const SizedBox(height: 8),
              Text('Estado: ${(pedidoData['estado'] ?? 'abierto').toString().replaceAll('_', ' ')}'),
              Text('Total: \$${_asDouble(pedidoData['total_pedido']).toStringAsFixed(0)}'),
              const SizedBox(height: 12),
              const Text('Productos', style: TextStyle(fontWeight: FontWeight.w900)),
              const SizedBox(height: 8),
              if (items.isEmpty)
                const Text('Sin detalle disponible')
              else
                ...items.map((raw) {
                  final item = Map<String, dynamic>.from(raw as Map);
                  return Padding(
                    padding: const EdgeInsets.symmetric(vertical: 4),
                    child: Text(
                      '${item['cantidad'] ?? 0} x ${item['nombre_producto'] ?? 'Producto'}',
                    ),
                  );
                }),
            ],
          ),
        );
      },
    );
  }

  Future<void> _actualizarPedidoParaLlevar(Map<String, dynamic> pedido, String estado) async {
    final live = ScaffoldMessenger.of(context);
    try {
      await BongustoApi.actualizarEstadoPedido(
        pedidoId: _asInt(pedido['id_pedido']),
        estado: estado,
      );
      await _cargarMesas(silent: true);
      live.showSnackBar(
        SnackBar(content: Text('Pedido para llevar actualizado a ${estado.replaceAll('_', ' ')}.')),
      );
    } catch (e) {
      live.showSnackBar(
        SnackBar(content: Text('No se pudo actualizar el pedido: $e')),
      );
    }
  }

  Future<void> _confirmarPagoParaLlevar(Map<String, dynamic> pedido) async {
    final pago = pedido['pago'] is Map ? Map<String, dynamic>.from(pedido['pago'] as Map) : null;
    if (pago == null || pago['id_solicitud_pago'] == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('El pedido no tiene una solicitud de pago activa.')),
      );
      return;
    }
    try {
      await BongustoApi.actualizarSolicitudPago(
        idSolicitudPago: _asInt(pago['id_solicitud_pago']),
        estado: 'finalizada',
      );
      await _cargarMesas(silent: true);
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Pago confirmado para pedido para llevar.')),
      );
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('No se pudo confirmar el pago: $e')),
      );
    }
  }

  Widget _mesaBox(Mesa mesa) {
    final productosPreview = mesa.pendientes.entries.take(2).map((entry) {
      final cantidad = entry.value;
      return cantidad > 0 ? '${entry.key} x$cantidad' : entry.key;
    }).join(' | ');
    final pago = mesa.pago;

    return GestureDetector(
      onTap: () {
        Navigator.push<bool>(
          context,
          MaterialPageRoute(builder: (_) => MesaDetailScreen(mesa: mesa)),
        ).then((actualizada) {
          if (actualizada == true) {
            _cargarMesas();
          }
        });
      },
      child: Container(
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: _color(mesa),
          borderRadius: BorderRadius.circular(24),
          border: Border.all(color: kLine),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.05),
              blurRadius: 14,
              offset: const Offset(0, 8),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Wrap(
              spacing: 8,
              runSpacing: 8,
              crossAxisAlignment: WrapCrossAlignment.center,
              children: [
                Text(
                  mesa.etiqueta,
                  style: const TextStyle(
                    color: kInk,
                    fontSize: 20,
                    fontWeight: FontWeight.w900,
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 10,
                    vertical: 6,
                  ),
                  decoration: BoxDecoration(
                    color: Colors.white.withValues(alpha: 0.75),
                    borderRadius: BorderRadius.circular(999),
                  ),
                  child: Text(
                    _statusLabel(mesa),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(
                      color: kInk,
                      fontSize: 11,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 10),
            Text(
              mesa.clientesLabel,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: const TextStyle(
                color: kMuted,
                fontWeight: FontWeight.w700,
              ),
            ),
            const SizedBox(height: 10),
            Row(
              children: [
                Expanded(child: _metric('Pedidos', '${mesa.totalPedidos}')),
                const SizedBox(width: 10),
                Expanded(child: _metric('Total', '\$${mesa.totalPendiente.toStringAsFixed(0)}')),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              productosPreview.isEmpty
                  ? 'Sin productos asignados'
                  : productosPreview,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: const TextStyle(color: kMuted, height: 1.2),
            ),
            if (pago != null) ...[
              const SizedBox(height: 8),
              Container(
                width: double.infinity,
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
                decoration: BoxDecoration(
                  color: Colors.white.withValues(alpha: 0.78),
                  borderRadius: BorderRadius.circular(18),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Pago solicitado',
                      style: TextStyle(
                        color: kBrandRed,
                        fontWeight: FontWeight.w900,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      '${pago['metodo_pago'] ?? '-'} | ${pago['estado'] ?? 'pendiente'}',
                      style: const TextStyle(
                        color: kInk,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _metric(String label, String value) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 10),
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.74),
        borderRadius: BorderRadius.circular(18),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            label,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
            style: const TextStyle(color: kMuted, fontSize: 11),
          ),
          const SizedBox(height: 4),
          Text(
            value,
            style: const TextStyle(
              color: kInk,
              fontWeight: FontWeight.w900,
            ),
          ),
        ],
      ),
    );
  }

  Widget _legend(Color color, String label) {
    return Row(
      children: [
        Container(
          width: 16,
          height: 16,
          decoration: BoxDecoration(color: color, shape: BoxShape.circle),
        ),
        const SizedBox(width: 8),
        Text(
          label,
          style: const TextStyle(
            color: kInk,
            fontWeight: FontWeight.w700,
          ),
        ),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    final screenWidth = MediaQuery.of(context).size.width;
    final isPhone = screenWidth < 700;

    return Scaffold(
      backgroundColor: _bg,
      appBar: AppBar(
        backgroundColor: _bg,
        foregroundColor: _isDark ? Colors.white : kInk,
        title: const Text(
          'Mesas',
          style: TextStyle(fontWeight: FontWeight.w800),
        ),
      ),
      body: RefreshIndicator(
        color: kBrandRed,
        onRefresh: _cargarMesas,
        child: ListView(
          padding: const EdgeInsets.fromLTRB(20, 8, 20, 28),
          children: [
            _hero(),
            const SizedBox(height: 18),
            if (_loading)
              const Padding(
                padding: EdgeInsets.all(32),
                child: Center(child: CircularProgressIndicator()),
              )
            else if (_error.isNotEmpty)
              _stateCard(
                icon: Icons.error_outline,
                text: 'No se pudieron cargar las mesas.\n$_error',
              )
            else if (_mesas.isEmpty)
              _stateCard(
                icon: Icons.table_restaurant_outlined,
                text: 'No hay mesas activas registradas en el backend.',
              )
            else ...[
              GridView.builder(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                itemCount: _mesas.length,
                gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                  crossAxisCount: isPhone ? 1 : 2,
                  crossAxisSpacing: 14,
                  mainAxisSpacing: 14,
                  mainAxisExtent: isPhone ? 255 : 285,
                ),
                itemBuilder: (_, index) => _mesaBox(_mesas[index]),
              ),
              const SizedBox(height: 22),
              Wrap(
                spacing: 18,
                runSpacing: 12,
                children: [
                  _legend(kGray, 'Disponible'),
                  _legend(const Color(0xFFFFD6DB), 'Ocupada'),
                  _legend(const Color(0xFFFFF0B8), 'Esperando pago'),
                  _legend(const Color(0xFFE5EBFF), 'Pagada'),
                  _legend(const Color(0xFFE5F4FF), 'En limpieza'),
                  _legend(const Color(0xFFE9E7EC), 'Bloqueada'),
                ],
              ),
            ],
            if (!_loading && _error.isEmpty) ...[
              const SizedBox(height: 22),
              _takeoutPanel(),
            ],
          ],
        ),
      ),
    );
  }
}

class _MesasLifecycleObserver with WidgetsBindingObserver {
  _MesasLifecycleObserver({required this.onResume});

  final VoidCallback onResume;

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    if (state == AppLifecycleState.resumed) {
      onResume();
    }
  }
}
