// Pantalla que muestra el detalle completo de un pedido individual.
import 'package:flutter/material.dart';

import '../app_theme.dart';
import 'pedido_global.dart';

// Widget encargado de pintar productos, totales y estado del pedido.
class PedidoDetalleScreen extends StatelessWidget {
  const PedidoDetalleScreen({super.key, required this.pedido});

  final Pedido pedido;

  static Color get _pageBg => AppThemeColors.bg;
  static Color get _card => AppThemeColors.surface;
  static Color get _ink => AppThemeColors.text;
  static Color get _muted => AppThemeColors.muted;
  static const _accent = Color(0xFFD90416);
  static Color get _line => AppThemeColors.line;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: _pageBg,
      appBar: AppBar(
        backgroundColor: _pageBg,
        foregroundColor: _ink,
        elevation: 0,
        scrolledUnderElevation: 0,
        title: Text(
          'Pedido #${pedido.id}',
          style: TextStyle(fontWeight: FontWeight.w900),
        ),
      ),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(20, 8, 20, 28),
        children: [
          _summaryCard(),
          const SizedBox(height: 18),
          Text(
            'Detalle del pedido',
            style: TextStyle(
              color: _ink,
              fontSize: 20,
              fontWeight: FontWeight.w900,
            ),
          ),
          const SizedBox(height: 12),
          if (pedido.productos.isEmpty)
            _emptyItemsCard()
          else
            ...pedido.productos.map(_itemCard),
        ],
      ),
    );
  }

  Widget _summaryCard() {
    return Container(
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
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      pedido.fechaPedido.isEmpty
                          ? 'Sin fecha registrada'
                          : pedido.fechaPedido,
                      style: TextStyle(
                        color: _muted,
                        fontSize: 13,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    const SizedBox(height: 6),
                    Text(
                      pedido.estado,
                      style: TextStyle(
                        color: _accent,
                        fontSize: 16,
                        fontWeight: FontWeight.w900,
                      ),
                    ),
                    if (pedido.mesaLabel.isNotEmpty) ...[
                      const SizedBox(height: 6),
                      Text(
                        pedido.mesaLabel,
                        style: TextStyle(
                          color: _accent,
                          fontSize: 14,
                          fontWeight: FontWeight.w800,
                        ),
                      ),
                    ],
                  ],
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: 14,
                  vertical: 10,
                ),
                decoration: BoxDecoration(
                  color: const Color(0xFFFFECEE),
                  borderRadius: BorderRadius.circular(999),
                ),
                child: Text(
                  '${pedido.productos.length} items',
                  style: TextStyle(color: _accent, fontWeight: FontWeight.w800),
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: _metric('Total', '\$${pedido.total.toStringAsFixed(0)}'),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _metric(
                  'Cantidad total',
                  '${pedido.productos.fold<int>(0, (sum, item) => sum + item.cantidad)}',
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
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 14),
      decoration: BoxDecoration(
        color: const Color(0xFFF8F8FA),
        borderRadius: BorderRadius.circular(18),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            label,
            style: TextStyle(
              color: _muted,
              fontSize: 12,
              fontWeight: FontWeight.w700,
            ),
          ),
          const SizedBox(height: 6),
          Text(
            value,
            style: TextStyle(
              color: _ink,
              fontSize: 18,
              fontWeight: FontWeight.w900,
            ),
          ),
        ],
      ),
    );
  }

  Widget _itemCard(dynamic producto) {
    final subtotal = producto.precio * producto.cantidad;
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
                  producto.nombre,
                  style: TextStyle(
                    color: _ink,
                    fontSize: 17,
                    fontWeight: FontWeight.w900,
                  ),
                ),
              ),
              const SizedBox(width: 12),
              Text(
                '\$${subtotal.toStringAsFixed(0)}',
                style: TextStyle(color: _accent, fontWeight: FontWeight.w900),
              ),
            ],
          ),
          if ((producto.descripcion).trim().isNotEmpty) ...[
            const SizedBox(height: 8),
            Text(
              producto.descripcion,
              style: TextStyle(color: _muted, height: 1.4),
            ),
          ],
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(child: _miniMetric('Cantidad', '${producto.cantidad}')),
              const SizedBox(width: 10),
              Expanded(
                child: _miniMetric(
                  'Unitario',
                  '\$${producto.precio.toStringAsFixed(0)}',
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _miniMetric(String label, String value) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 12),
      decoration: BoxDecoration(
        color: const Color(0xFFF8F8FA),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(label, style: TextStyle(color: _muted, fontSize: 12)),
          const SizedBox(height: 4),
          Text(
            value,
            style: TextStyle(color: _ink, fontWeight: FontWeight.w800),
          ),
        ],
      ),
    );
  }

  Widget _emptyItemsCard() {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: _card,
        borderRadius: BorderRadius.circular(22),
        border: Border.all(color: _line),
      ),
      child: Text(
        'Este pedido no tiene items disponibles para mostrar.',
        style: TextStyle(color: _muted),
      ),
    );
  }
}
