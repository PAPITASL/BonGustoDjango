// ===== Pantalla `menu_detalle_screen.dart` | Presenta el detalle completo de un menu y sus productos asociados. =====
import 'package:flutter/material.dart';

// ===== Clase `MenuDetalleScreen` | Muestra la informacion extendida del menu seleccionado. =====
class MenuDetalleScreen extends StatelessWidget {
  const MenuDetalleScreen({
    super.key,
    required this.menu,
    required this.productos,
  });

  final Map<String, dynamic> menu;
  final List<Map<String, dynamic>> productos;

  static const _bg = Color(0xFFF2F1F4);
  static const _card = Color(0xFFFFFFFF);
  static const _ink = Color(0xFF181818);
  static const _muted = Color(0xFF73727A);
  static const _accent = Color(0xFFD90416);
  static const _line = Color(0xFFE8E6EB);

  @override
  Widget build(BuildContext context) {
    final menuData = MenuDetailData.fromDynamic(menu);
    final productosData = productos
        .map((item) => MenuProductDetailData.fromDynamic(item))
        .toList();

    return Scaffold(
      backgroundColor: _bg,
      appBar: AppBar(
        backgroundColor: _bg,
        foregroundColor: _ink,
        title: Text(
          menuData.nombre,
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
                  menuData.nombre,
                  style: const TextStyle(
                    color: _ink,
                    fontSize: 24,
                    fontWeight: FontWeight.w900,
                  ),
                ),
                if (menuData.descripcion.trim().isNotEmpty) ...[
                  const SizedBox(height: 8),
                  Text(
                    menuData.descripcion,
                    style: const TextStyle(color: _muted, height: 1.45),
                  ),
                ],
                const SizedBox(height: 14),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                  decoration: BoxDecoration(
                    color: const Color(0xFFFFECEE),
                    borderRadius: BorderRadius.circular(999),
                  ),
                  child: Text(
                    '${productosData.length} platos',
                    style: const TextStyle(
                      color: _accent,
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 18),
          if (productosData.isEmpty)
            Container(
              padding: const EdgeInsets.all(24),
              decoration: BoxDecoration(
                color: _card,
                borderRadius: BorderRadius.circular(22),
                border: Border.all(color: _line),
              ),
              child: const Text(
                'Este menu no tiene productos activos.',
                style: TextStyle(color: _muted),
              ),
            )
          else
            ...productosData.map(_productoCard),
        ],
      ),
    );
  }

  Widget _productoCard(MenuProductDetailData producto) {
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
                  style: const TextStyle(
                    color: _ink,
                    fontSize: 17,
                    fontWeight: FontWeight.w900,
                  ),
                ),
              ),
              const SizedBox(width: 12),
              Text(
                '\$${producto.precio.toStringAsFixed(0)}',
                style: const TextStyle(
                  color: _accent,
                  fontWeight: FontWeight.w900,
                ),
              ),
            ],
          ),
          if (producto.descripcion.trim().isNotEmpty) ...[
            const SizedBox(height: 8),
            Text(
              producto.descripcion,
              style: const TextStyle(
                color: _muted,
                fontSize: 13,
                height: 1.45,
              ),
            ),
          ],
        ],
      ),
    );
  }
}

class MenuDetailData {
  final String nombre;
  final String descripcion;

  const MenuDetailData({
    required this.nombre,
    required this.descripcion,
  });

  factory MenuDetailData.fromDynamic(dynamic value) {
    final json = Map<String, dynamic>.from(value as Map);
    return MenuDetailData(
      nombre: (json['nombre_menu'] ?? 'Menu').toString(),
      descripcion: (json['descripcion_menu'] ?? '').toString(),
    );
  }
}

class MenuProductDetailData {
  final String nombre;
  final String descripcion;
  final double precio;

  const MenuProductDetailData({
    required this.nombre,
    required this.descripcion,
    required this.precio,
  });

  factory MenuProductDetailData.fromDynamic(dynamic value) {
    final json = Map<String, dynamic>.from(value as Map);
    return MenuProductDetailData(
      nombre: (json['nombre_producto'] ?? '').toString(),
      descripcion: (json['descripcion_producto'] ?? '').toString(),
      precio: double.tryParse('${json['precio_producto']}') ?? 0,
    );
  }
}
