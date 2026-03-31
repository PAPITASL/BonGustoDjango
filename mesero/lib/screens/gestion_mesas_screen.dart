// ===== Pantalla `gestion_mesas_screen.dart` | Presenta cinco mesas y vincula los pedidos de clientes a cada una. =====
import 'dart:async';

import 'package:flutter/material.dart';

import '../services/bongusto_api.dart';
import 'mesa_detail_screen.dart';
import 'mesa_model.dart';

// ===== Clase `GestionMesasScreen` | Define la vista principal del modulo de mesas. =====
class GestionMesasScreen extends StatefulWidget {
  const GestionMesasScreen({super.key});

  @override
  State<GestionMesasScreen> createState() => _GestionMesasScreenState();
}

// ===== Estado `_GestionMesasScreenState` | Consulta pedidos, arma las cinco mesas y abre su detalle. =====
class _GestionMesasScreenState extends State<GestionMesasScreen> {
  static const kBrandRed = Color(0xFFD90416);
  static const kGreen = Color(0xFFDDF4D7);
  static const kGray = Color(0xFFECEAF0);
  static const kPageBg = Color(0xFFF2F1F4);
  static const kCard = Color(0xFFFFFFFF);
  static const kInk = Color(0xFF181818);
  static const kMuted = Color(0xFF73727A);
  static const kLine = Color(0xFFE8E6EB);

  bool _loading = true;
  String _error = '';
  List<Mesa> _mesas = _crearMesasBase();
  Timer? _refreshTimer;

  static List<Mesa> _crearMesasBase() => List<Mesa>.generate(
    5,
    (index) => Mesa(id: index + 1),
  );

  @override
  void initState() {
    super.initState();
    _cargarMesas();
    _refreshTimer = Timer.periodic(const Duration(seconds: 4), (_) {
      _cargarMesas(silent: true);
    });
  }

  @override
  void dispose() {
    _refreshTimer?.cancel();
    super.dispose();
  }

  Future<void> _cargarMesas({bool silent = false}) async {
    if (!silent) {
      setState(() {
        _loading = true;
        _error = '';
      });
    }

    try {
      final mesasApi = await BongustoApi.obtenerMesas();
      final pedidos = await BongustoApi.obtenerPedidos();
      if (!mounted) return;

      setState(() {
        _mesas = _mapearMesasYPedidos(mesasApi, pedidos);
        _loading = false;
        _error = '';
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _mesas = _crearMesasBase();
        _error = '$e';
        _loading = false;
      });
    }
  }

  List<Mesa> _mapearMesasYPedidos(
    List<Map<String, dynamic>> mesasApi,
    List<Map<String, dynamic>> pedidos,
  ) {
    final mesas = _crearMesasBase();

    for (final rawMesa in mesasApi) {
      final mesaMap = Map<String, dynamic>.from(rawMesa);
      final mesaId = _asInt(mesaMap['id']);
      if (mesaId < 1 || mesaId > mesas.length) continue;
      final mesa = mesas[mesaId - 1];
      mesa.idUsuario = _asInt(mesaMap['id_usuario']);
      mesa.asignadoEn = (mesaMap['asignado_en'] ?? '').toString();
      final cliente = (mesaMap['cliente_nombre'] ?? '').toString().trim();
      final estado = (mesaMap['estado'] ?? 'disponible').toString().trim().toLowerCase();
      if (estado == 'con_pedidos') {
        mesa.status = TableStatus.noPagado;
      } else if (estado == 'pagada') {
        mesa.status = TableStatus.pagado;
      } else {
        mesa.status = TableStatus.disponible;
      }

      if (cliente.isNotEmpty) {
        mesa.clientes.add(cliente);
      }
    }

    final pedidosPorMesa = <int, List<Map<String, dynamic>>>{};
    for (final pedido in pedidos) {
      final pedidoUsuarioId = _asInt(pedido['id_usuario']);
      final mesa = mesas.firstWhere(
        (item) => item.idUsuario != null && item.idUsuario == pedidoUsuarioId,
        orElse: () => mesas[_resolverMesaId(pedido) - 1],
      );
      final asignadoEn = (mesa.asignadoEn ?? '').split('T').first;
      final fechaPedido = (pedido['fecha_pedido'] ?? '').toString().split('T').first;
      if (mesa.idUsuario != null && pedidoUsuarioId != mesa.idUsuario) {
        continue;
      }
      if (asignadoEn.isNotEmpty && fechaPedido.isNotEmpty && fechaPedido != asignadoEn) {
        continue;
      }

      final mesaId = mesa.id;
      pedidosPorMesa.putIfAbsent(mesaId, () => <Map<String, dynamic>>[]);
      pedidosPorMesa[mesaId]!.add(Map<String, dynamic>.from(pedido));
    }

    for (final mesa in mesas) {
      final pedidosMesa = pedidosPorMesa[mesa.id] ?? const <Map<String, dynamic>>[];
      if (pedidosMesa.isNotEmpty) {
        final pedidoActual = pedidosMesa.reduce((actual, siguiente) {
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
      }
    }

    return mesas;
  }

  int _resolverMesaId(Map<String, dynamic> pedido) {
    final mesaExplicita = _asInt(
      pedido['id_mesa'] ?? pedido['mesa_id'] ?? pedido['numero_mesa'],
    );
    if (mesaExplicita >= 1 && mesaExplicita <= 5) {
      return mesaExplicita;
    }

    final idUsuario = _asInt(pedido['id_usuario']);
    if (idUsuario > 0) {
      return ((idUsuario - 1) % 5) + 1;
    }

    final idPedido = _asInt(pedido['id_pedido']);
    return ((idPedido - 1) % 5) + 1;
  }

  int _asInt(dynamic value) {
    if (value is int) return value;
    return int.tryParse('$value') ?? 0;
  }

  Color _color(Mesa mesa) {
    switch (mesa.status) {
      case TableStatus.disponible:
        return kGray;
      case TableStatus.noPagado:
        return const Color(0xFFFFD6DB);
      case TableStatus.pagado:
        return kGreen;
    }
  }

  String _statusLabel(Mesa mesa) {
    switch (mesa.status) {
      case TableStatus.disponible:
        return 'Disponible';
      case TableStatus.noPagado:
        return 'Ocupada';
      case TableStatus.pagado:
        return 'Pagada';
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
          Text(text, textAlign: TextAlign.center),
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

  Widget _mesaBox(Mesa mesa) {
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
        padding: const EdgeInsets.all(16),
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
                  'Mesa ${mesa.id}',
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
            const SizedBox(height: 12),
            Text(
              mesa.clientesLabel,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: const TextStyle(
                color: kMuted,
                fontWeight: FontWeight.w700,
              ),
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(child: _metric('Pedidos', '${mesa.totalPedidos}')),
                const SizedBox(width: 10),
                Expanded(child: _metric('Productos', '${mesa.totalItems}')),
              ],
            ),
            const SizedBox(height: 12),
            Text(
              mesa.pendientes.keys.take(1).join(' | ').isEmpty
                  ? 'Sin productos asignados'
                  : mesa.pendientes.keys.take(1).join(' | '),
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: const TextStyle(color: kMuted, height: 1.35),
            ),
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
      backgroundColor: kPageBg,
      appBar: AppBar(
        backgroundColor: kPageBg,
        foregroundColor: kInk,
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
            else ...[
              GridView.builder(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                itemCount: _mesas.length,
                gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                  crossAxisCount: isPhone ? 1 : 2,
                  crossAxisSpacing: 14,
                  mainAxisSpacing: 14,
                  mainAxisExtent: isPhone ? 220 : 250,
                ),
                itemBuilder: (_, index) {
                  if (!isPhone && index == 4) {
                    return Center(
                      child: SizedBox(
                        width: 185,
                        child: _mesaBox(_mesas[index]),
                      ),
                    );
                  }
                  return _mesaBox(_mesas[index]);
                },
              ),
              const SizedBox(height: 22),
              Wrap(
                spacing: 18,
                runSpacing: 12,
                children: [
                  _legend(kGray, 'Disponible'),
                  _legend(const Color(0xFFFFD6DB), 'Ocupada'),
                  _legend(kGreen, 'Pagada'),
                ],
              ),
            ],
          ],
        ),
      ),
    );
  }
}
