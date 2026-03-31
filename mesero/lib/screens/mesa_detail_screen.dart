// ===== Pantalla `mesa_detail_screen.dart` | Permite revisar el cliente actual y cambiar el estado operativo de la mesa. =====
import 'package:flutter/material.dart';

import '../services/bongusto_api.dart';
import 'mesa_model.dart';

// ===== Clase `MesaDetailScreen` | Recibe una mesa puntual y permite marcarla como pagada o disponible. =====
class MesaDetailScreen extends StatefulWidget {
  const MesaDetailScreen({super.key, required this.mesa});

  final Mesa mesa;

  @override
  State<MesaDetailScreen> createState() => _MesaDetailScreenState();
}

// ===== Estado `_MesaDetailScreenState` | Presenta el cliente actual, el pedido actual y las acciones de la mesa. =====
class _MesaDetailScreenState extends State<MesaDetailScreen> {
  static const kBrandRed = Color(0xFFD90416);
  static const kBg = Color(0xFFF2F1F4);
  static const kCard = Color(0xFFFFFFFF);
  static const kInk = Color(0xFF181818);
  static const kMuted = Color(0xFF73727A);
  static const kLine = Color(0xFFE8E6EB);

  bool _updating = false;

  Mesa get mesa => widget.mesa;

  double _asDouble(dynamic value) {
    if (value is num) return value.toDouble();
    return double.tryParse('$value') ?? 0;
  }

  int _asInt(dynamic value) {
    if (value is int) return value;
    return int.tryParse('$value') ?? 0;
  }

  String _statusLabel() {
    switch (mesa.status) {
      case TableStatus.disponible:
        return 'Disponible';
      case TableStatus.noPagado:
        return 'Ocupada';
      case TableStatus.pagado:
        return 'Pagada';
    }
  }

  Future<void> _actualizarEstado(String estado) async {
    setState(() => _updating = true);
    try {
      await BongustoApi.actualizarEstadoMesa(mesaId: mesa.id, estado: estado);
      if (!mounted) return;
      Navigator.pop(context, true);
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('No se pudo actualizar la mesa: $e')),
      );
    } finally {
      if (mounted) {
        setState(() => _updating = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final pedidoActual = mesa.pedidos.isEmpty ? null : mesa.pedidos.first;
    final items = (pedidoActual?['items'] as List<dynamic>? ?? const <dynamic>[]);

    return Scaffold(
      backgroundColor: kBg,
      appBar: AppBar(
        backgroundColor: kBg,
        foregroundColor: kInk,
        title: Text(
          'Mesa ${mesa.id}',
          style: const TextStyle(fontWeight: FontWeight.w800),
        ),
      ),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(20, 8, 20, 28),
        children: [
          Container(
            padding: const EdgeInsets.all(22),
            decoration: BoxDecoration(
              color: kCard,
              borderRadius: BorderRadius.circular(30),
              border: Border.all(color: kLine),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'DETALLE DE MESA',
                  style: TextStyle(
                    color: kBrandRed,
                    fontSize: 12,
                    letterSpacing: 3,
                    fontWeight: FontWeight.w800,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  mesa.clientes.isEmpty
                      ? 'La mesa ${mesa.id} esta disponible'
                      : 'Cliente actual de la mesa ${mesa.id}',
                  style: const TextStyle(
                    color: kInk,
                    fontSize: 26,
                    height: 1.08,
                    fontWeight: FontWeight.w900,
                  ),
                ),
                const SizedBox(height: 10),
                Text(
                  mesa.clientes.isEmpty
                      ? 'No hay cliente asignado en este momento.'
                      : mesa.clientes.first,
                  style: const TextStyle(
                    color: kMuted,
                    fontSize: 16,
                    fontWeight: FontWeight.w700,
                  ),
                ),
                const SizedBox(height: 16),
                Row(
                  children: [
                    Expanded(child: _metric('Estado', _statusLabel())),
                    const SizedBox(width: 10),
                    Expanded(child: _metric('Productos', '${mesa.totalItems}')),
                  ],
                ),
              ],
            ),
          ),
          const SizedBox(height: 18),
          if (pedidoActual != null) ...[
            const Text(
              'Pedido actual',
              style: TextStyle(
                color: kInk,
                fontSize: 18,
                fontWeight: FontWeight.w900,
              ),
            ),
            const SizedBox(height: 10),
            Container(
              padding: const EdgeInsets.all(18),
              decoration: BoxDecoration(
                color: kCard,
                borderRadius: BorderRadius.circular(24),
                border: Border.all(color: kLine),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Pedido #${pedidoActual['id_pedido']}',
                    style: const TextStyle(
                      color: kInk,
                      fontSize: 18,
                      fontWeight: FontWeight.w900,
                    ),
                  ),
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      Expanded(
                        child: _metric(
                          'Fecha',
                          (pedidoActual['fecha_pedido'] ?? 'Sin fecha').toString(),
                        ),
                      ),
                      const SizedBox(width: 10),
                      Expanded(
                        child: _metric(
                          'Total',
                          '\$${_asDouble(pedidoActual['total_pedido']).toStringAsFixed(0)}',
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 14),
                  const Text(
                    'Productos del pedido',
                    style: TextStyle(
                      color: kInk,
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                  const SizedBox(height: 10),
                  ...items.map(
                    (rawItem) => _itemTile(Map<String, dynamic>.from(rawItem as Map)),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 18),
          ],
          const Text(
            'Acciones de la mesa',
            style: TextStyle(
              color: kInk,
              fontSize: 18,
              fontWeight: FontWeight.w900,
            ),
          ),
          const SizedBox(height: 10),
          Row(
            children: [
              Expanded(
                child: SizedBox(
                  height: 48,
                  child: ElevatedButton(
                    onPressed: _updating || mesa.clientes.isEmpty || mesa.status == TableStatus.pagado
                        ? null
                        : () => _actualizarEstado('pagada'),
                    style: ElevatedButton.styleFrom(
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(16),
                      ),
                    ),
                    child: Text(_updating ? 'Actualizando' : 'Pagada'),
                  ),
                ),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: SizedBox(
                  height: 48,
                  child: OutlinedButton(
                    onPressed: _updating || mesa.status == TableStatus.disponible
                        ? null
                        : () => _actualizarEstado('disponible'),
                    style: OutlinedButton.styleFrom(
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(16),
                      ),
                    ),
                    child: const Text('Liberar'),
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _metric(String label, String value) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 12),
      decoration: BoxDecoration(
        color: const Color(0xFFF8F8FA),
        borderRadius: BorderRadius.circular(18),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(label, style: const TextStyle(color: kMuted, fontSize: 12)),
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

  Widget _itemTile(Map<String, dynamic> item) {
    final nombre = (item['nombre_producto'] ?? 'Producto').toString();
    final cantidad = _asInt(item['cantidad']);
    final subtotal = _asDouble(item['subtotal']);

    return Container(
      margin: const EdgeInsets.only(bottom: 10),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: const Color(0xFFF8F8FA),
        borderRadius: BorderRadius.circular(18),
      ),
      child: Row(
        children: [
          Container(
            width: 40,
            height: 40,
            alignment: Alignment.center,
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(14),
            ),
            child: Text(
              '$cantidad',
              style: const TextStyle(
                color: kBrandRed,
                fontWeight: FontWeight.w900,
              ),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              nombre,
              style: const TextStyle(
                color: kInk,
                fontWeight: FontWeight.w800,
              ),
            ),
          ),
          const SizedBox(width: 12),
          Text(
            '\$${subtotal.toStringAsFixed(0)}',
            style: const TextStyle(
              color: kInk,
              fontWeight: FontWeight.w800,
            ),
          ),
        ],
      ),
    );
  }
}
