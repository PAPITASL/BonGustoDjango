// ===== Pantalla `pedido_detalle_screen.dart` | Muestra el detalle puntual de un pedido seleccionado desde el listado. =====
import 'package:flutter/material.dart';

// ===== Clase `PedidoDetalleScreen` | Organiza encabezado, metricas e items del pedido actual. =====
class PedidoDetalleScreen extends StatelessWidget {
  const PedidoDetalleScreen({super.key, required this.pedido});

  final Map<String, dynamic> pedido;

  static const _bg = Color(0xFFF2F1F4);
  static const _card = Color(0xFFFFFFFF);
  static const _ink = Color(0xFF181818);
  static const _muted = Color(0xFF73727A);
  static const _accent = Color(0xFFD90416);
  static const _line = Color(0xFFE8E6EB);

  @override
  Widget build(BuildContext context) {
    final pedidoData = PedidoDetailData.fromDynamic(pedido);

    return Scaffold(
      backgroundColor: _bg,
      appBar: AppBar(
        backgroundColor: _bg,
        foregroundColor: _ink,
        title: Text(
          'Pedido #${pedidoData.id}',
          style: const TextStyle(fontWeight: FontWeight.w900),
        ),
      ),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(20, 8, 20, 28),
        children: [
          Container(
            padding: const EdgeInsets.all(18),
            decoration: BoxDecoration(
              color: _card,
              borderRadius: BorderRadius.circular(24),
              border: Border.all(color: _line),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  pedidoData.clienteNombre,
                  style: const TextStyle(
                    color: _ink,
                    fontSize: 22,
                    fontWeight: FontWeight.w900,
                  ),
                ),
                const SizedBox(height: 6),
                Text(
                  pedidoData.clienteCorreo,
                  style: const TextStyle(color: _muted),
                ),
                if (pedidoData.mesaLabel.isNotEmpty) ...[
                  const SizedBox(height: 6),
                  Text(
                    pedidoData.mesaLabel,
                    style: const TextStyle(
                      color: _accent,
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                ],
                const SizedBox(height: 14),
                Row(
                  children: [
                    Expanded(
                      child: _metric(
                        'Estado',
                        pedidoData.estado,
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: _metric(
                        'Fecha',
                        pedidoData.fechaPedido.isEmpty
                            ? 'Sin fecha'
                            : pedidoData.fechaPedido,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                Row(
                  children: [
                    Expanded(child: _metric('Items', '${pedidoData.cantidadTotal}')),
                    const SizedBox(width: 12),
                    Expanded(
                      child: _metric(
                        'Total',
                        '\$${pedidoData.totalPedido.toStringAsFixed(0)}',
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
          const SizedBox(height: 18),
          const Text(
            'Items del pedido',
            style: TextStyle(
              color: _ink,
              fontSize: 20,
              fontWeight: FontWeight.w900,
            ),
          ),
          const SizedBox(height: 12),
          if (pedidoData.items.isEmpty)
            _emptyState()
          else
            ...pedidoData.items.map(_itemCard),
        ],
      ),
    );
  }

  Widget _metric(String label, String value) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 14),
      decoration: BoxDecoration(
        color: const Color(0xFFF8F8FA),
        borderRadius: BorderRadius.circular(18),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(label, style: const TextStyle(color: _muted, fontSize: 12)),
          const SizedBox(height: 6),
          Text(
            value,
            style: const TextStyle(
              color: _ink,
              fontWeight: FontWeight.w800,
            ),
          ),
        ],
      ),
    );
  }

  Widget _itemCard(PedidoItemDetailData item) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: _card,
        borderRadius: BorderRadius.circular(22),
        border: Border.all(color: _line),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(
                child: Text(
                  item.nombre,
                  style: const TextStyle(
                    color: _ink,
                    fontSize: 17,
                    fontWeight: FontWeight.w900,
                  ),
                ),
              ),
              const SizedBox(width: 12),
              Text(
                '\$${item.subtotal.toStringAsFixed(0)}',
                style: const TextStyle(
                  color: _accent,
                  fontWeight: FontWeight.w900,
                ),
              ),
            ],
          ),
          if (item.descripcion.trim().isNotEmpty) ...[
            const SizedBox(height: 8),
            Text(
              item.descripcion,
              style: const TextStyle(color: _muted, height: 1.4),
            ),
          ],
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(child: _metric('Cantidad', '${item.cantidad}')),
              const SizedBox(width: 10),
              Expanded(
                child: _metric('Unitario', '\$${item.precio.toStringAsFixed(0)}'),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _emptyState() {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: _card,
        borderRadius: BorderRadius.circular(22),
        border: Border.all(color: _line),
      ),
      child: const Text(
        'Este pedido no tiene items disponibles para mostrar.',
        style: TextStyle(color: _muted),
      ),
    );
  }
}

class PedidoDetailData {
  final int id;
  final String clienteNombre;
  final String clienteCorreo;
  final String mesaLabel;
  final String fechaPedido;
  final String estado;
  final double totalPedido;
  final List<PedidoItemDetailData> items;

  const PedidoDetailData({
    required this.id,
    required this.clienteNombre,
    required this.clienteCorreo,
    required this.mesaLabel,
    required this.fechaPedido,
    required this.estado,
    required this.totalPedido,
    required this.items,
  });

  int get cantidadTotal => items.fold(0, (sum, item) => sum + item.cantidad);

  factory PedidoDetailData.fromDynamic(dynamic value) {
    final json = Map<String, dynamic>.from(value as Map);
    final rawItems = (json['items'] as List<dynamic>? ?? const []);
    return PedidoDetailData(
      id: PedidoItemDetailData.asInt(json['id_pedido']),
      clienteNombre: (json['cliente_nombre'] ?? 'Cliente sin nombre').toString(),
      clienteCorreo: (json['cliente_correo'] ?? '').toString(),
      mesaLabel: (json['mesa_label'] ?? '').toString(),
      fechaPedido: (json['fecha_pedido'] ?? '').toString(),
      estado: (json['estado'] ?? 'Registrado').toString(),
      totalPedido: PedidoItemDetailData.asDouble(json['total_pedido']),
      items: rawItems
          .map(
            (item) => PedidoItemDetailData.fromMap(
              Map<String, dynamic>.from(item as Map),
            ),
          )
          .toList(),
    );
  }
}

class PedidoItemDetailData {
  final String nombre;
  final String descripcion;
  final int cantidad;
  final double precio;
  final double subtotal;

  const PedidoItemDetailData({
    required this.nombre,
    required this.descripcion,
    required this.cantidad,
    required this.precio,
    required this.subtotal,
  });

  factory PedidoItemDetailData.fromMap(Map<String, dynamic> json) {
    return PedidoItemDetailData(
      nombre: (json['nombre_producto'] ?? 'Producto').toString(),
      descripcion: (json['descripcion_producto'] ?? '').toString(),
      cantidad: asInt(json['cantidad']),
      precio: asDouble(json['precio']),
      subtotal: asDouble(json['subtotal']),
    );
  }

  static int asInt(dynamic value) {
    if (value is int) {
      return value;
    }
    return int.tryParse('$value') ?? 0;
  }

  static double asDouble(dynamic value) {
    if (value is num) {
      return value.toDouble();
    }
    return double.tryParse('$value') ?? 0;
  }
}
