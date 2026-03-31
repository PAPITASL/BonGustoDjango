// ===== Pantalla `pedidos_screen.dart` | Lista los pedidos operativos que llegan desde Django para el mesero. =====
import 'dart:async';

import 'package:flutter/material.dart';

import '../services/bongusto_api.dart';
import 'pedido_detalle_screen.dart';

// ===== Clase `PedidosScreen` | Define la vista principal del modulo de pedidos. =====
class PedidosScreen extends StatefulWidget {
  const PedidosScreen({super.key});

  @override
  State<PedidosScreen> createState() => _PedidosScreenState();
}

// ===== Estado `_PedidosScreenState` | Administra la consulta de pedidos y la interfaz del listado. =====
class _PedidosScreenState extends State<PedidosScreen> {
  static const _bg = Color(0xFFF2F1F4);
  static const _card = Color(0xFFFFFFFF);
  static const _ink = Color(0xFF181818);
  static const _muted = Color(0xFF73727A);
  static const _accent = Color(0xFFD90416);
  static const _line = Color(0xFFE8E6EB);

  bool _loading = true;
  String _error = '';
  List<PedidoData> _pedidos = [];
  Timer? _refreshTimer;

  @override
  void initState() {
    super.initState();
    _cargarPedidos();
    _refreshTimer = Timer.periodic(const Duration(seconds: 4), (_) {
      _cargarPedidos(silent: true);
    });
  }

  @override
  void dispose() {
    _refreshTimer?.cancel();
    super.dispose();
  }

  Future<void> _cargarPedidos({bool silent = false}) async {
    if (!silent) {
      setState(() {
        _loading = true;
        _error = '';
      });
    }
    try {
      final pedidos = await BongustoApi.obtenerPedidos();
      if (!mounted) return;
      setState(() {
        _pedidos = pedidos.map(PedidoData.fromMap).toList();
        _loading = false;
        _error = '';
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _error = '$e';
        _loading = false;
      });
    }
  }

  Widget _hero() {
    return Container(
      padding: const EdgeInsets.all(22),
      decoration: BoxDecoration(
        color: _card,
        borderRadius: BorderRadius.circular(30),
        border: Border.all(color: _line),
      ),
      child: const Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'PEDIDOS',
            style: TextStyle(
              color: _accent,
              fontSize: 12,
              letterSpacing: 3,
              fontWeight: FontWeight.w800,
            ),
          ),
          SizedBox(height: 8),
          Text(
            'Lectura rapida del servicio',
            style: TextStyle(
              color: _ink,
              fontSize: 30,
              height: 1.06,
              fontWeight: FontWeight.w900,
            ),
          ),
          SizedBox(height: 10),
          Text(
            'Consulta pedidos creados por clientes con cliente, fecha, items y total.',
            style: TextStyle(
              color: _muted,
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
        color: _card,
        borderRadius: BorderRadius.circular(28),
        border: Border.all(color: _line),
      ),
      child: Column(
        children: [
          Icon(icon, size: 48, color: _accent),
          const SizedBox(height: 12),
          Text(text, textAlign: TextAlign.center),
          if (_error.isNotEmpty) ...[
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: _cargarPedidos,
              child: const Text('Reintentar'),
            ),
          ],
        ],
      ),
    );
  }

  Widget _pedidoCard(PedidoData p) {
    final preview = p.items.take(3).map((item) => item.nombre).join(' | ');
    return GestureDetector(
      onTap: () {
        Navigator.push(
          context,
          MaterialPageRoute(builder: (_) => PedidoDetalleScreen(pedido: p.toMap())),
        );
      },
      child: Container(
        padding: const EdgeInsets.all(18),
        decoration: BoxDecoration(
          color: _card,
          borderRadius: BorderRadius.circular(24),
          border: Border.all(color: _line),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  width: 46,
                  height: 46,
                  decoration: BoxDecoration(
                    color: const Color(0xFFFFECEE),
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: const Icon(Icons.receipt_long_outlined, color: _accent),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Pedido #${p.id}',
                        style: const TextStyle(
                          color: _ink,
                          fontWeight: FontWeight.w900,
                          fontSize: 18,
                        ),
                      ),
                      Text(
                        p.clienteNombre,
                        style: const TextStyle(color: _muted),
                      ),
                      if (p.mesaLabel.isNotEmpty)
                        Text(
                          p.mesaLabel,
                          style: const TextStyle(
                            color: _accent,
                            fontWeight: FontWeight.w700,
                          ),
                        ),
                    ],
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                  decoration: BoxDecoration(
                    color: const Color(0xFFFFECEE),
                    borderRadius: BorderRadius.circular(999),
                  ),
                  child: Text(
                    p.estado,
                    style: const TextStyle(
                      color: _accent,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: _metric(
                    'Fecha',
                    p.fechaPedido.isEmpty ? 'Sin fecha' : p.fechaPedido,
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(child: _metric('Items', '${p.cantidadTotal}')),
                const SizedBox(width: 10),
                Expanded(
                  child: _metric('Total', '\$${p.totalPedido.toStringAsFixed(0)}'),
                ),
              ],
            ),
            if (preview.isNotEmpty) ...[
              const SizedBox(height: 12),
              Text(
                preview,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
                style: const TextStyle(color: _muted, height: 1.4),
              ),
            ],
            const SizedBox(height: 10),
            const Row(
              children: [
                Text(
                  'Toca para ver detalles',
                  style: TextStyle(
                    color: _accent,
                    fontWeight: FontWeight.w800,
                  ),
                ),
                SizedBox(width: 6),
                Icon(Icons.arrow_forward_rounded, color: _accent, size: 18),
              ],
            ),
          ],
        ),
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
          Text(label, style: const TextStyle(color: _muted, fontSize: 12)),
          const SizedBox(height: 4),
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

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: _bg,
      appBar: AppBar(
        backgroundColor: _bg,
        foregroundColor: _ink,
        title: const Text(
          'Pedidos',
          style: TextStyle(fontWeight: FontWeight.w800),
        ),
      ),
      body: RefreshIndicator(
        color: _accent,
        onRefresh: _cargarPedidos,
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
                text: 'No se pudieron cargar los pedidos.\n$_error',
              )
            else if (_pedidos.isEmpty)
              _stateCard(
                icon: Icons.inbox_outlined,
                text: 'No hay pedidos registrados por clientes.',
              )
            else
              ..._pedidos.map(_pedidoCard),
          ],
        ),
      ),
    );
  }
}

class PedidoData {
  final int id;
  final String clienteNombre;
  final String clienteCorreo;
  final String mesaLabel;
  final String fechaPedido;
  final String estado;
  final double totalPedido;
  final List<PedidoItemData> items;

  const PedidoData({
    required this.id,
    required this.clienteNombre,
    required this.clienteCorreo,
    required this.mesaLabel,
    required this.fechaPedido,
    required this.estado,
    required this.totalPedido,
    required this.items,
  });

  int get cantidadTotal =>
      items.fold(0, (sum, item) => sum + item.cantidad);

  factory PedidoData.fromMap(Map<String, dynamic> json) {
    final rawItems = (json['items'] as List<dynamic>? ?? const []);
    return PedidoData(
      id: PedidoItemData.asInt(json['id_pedido']),
      clienteNombre: (json['cliente_nombre'] ?? 'Cliente sin nombre').toString(),
      clienteCorreo: (json['cliente_correo'] ?? '').toString(),
      mesaLabel: (json['mesa_label'] ?? '').toString(),
      fechaPedido: (json['fecha_pedido'] ?? '').toString(),
      estado: (json['estado'] ?? 'Registrado').toString(),
      totalPedido: PedidoItemData.asDouble(json['total_pedido']),
      items: rawItems
          .map((item) => PedidoItemData.fromMap(Map<String, dynamic>.from(item as Map)))
          .toList(),
    );
  }

  Map<String, dynamic> toMap() {
    return {
      'id_pedido': id,
      'cliente_nombre': clienteNombre,
      'cliente_correo': clienteCorreo,
      'mesa_label': mesaLabel,
      'fecha_pedido': fechaPedido,
      'estado': estado,
      'total_pedido': totalPedido,
      'items': items.map((item) => item.toMap()).toList(),
    };
  }
}

class PedidoItemData {
  final String nombre;
  final String descripcion;
  final int cantidad;
  final double precio;
  final double subtotal;

  const PedidoItemData({
    required this.nombre,
    required this.descripcion,
    required this.cantidad,
    required this.precio,
    required this.subtotal,
  });

  factory PedidoItemData.fromMap(Map<String, dynamic> json) {
    return PedidoItemData(
      nombre: (json['nombre_producto'] ?? 'Producto').toString(),
      descripcion: (json['descripcion_producto'] ?? '').toString(),
      cantidad: asInt(json['cantidad']),
      precio: asDouble(json['precio']),
      subtotal: asDouble(json['subtotal']),
    );
  }

  Map<String, dynamic> toMap() {
    return {
      'nombre_producto': nombre,
      'descripcion_producto': descripcion,
      'cantidad': cantidad,
      'precio': precio,
      'subtotal': subtotal,
    };
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
