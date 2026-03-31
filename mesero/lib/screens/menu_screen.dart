// ===== Pantalla `menu_screen.dart` | Consulta y muestra los menus creados en Django en modo lectura para el mesero. =====
import 'package:flutter/material.dart';

import '../services/bongusto_api.dart';
import 'menu_detalle_screen.dart';

// ===== Clase `MenuScreen` | Define la vista principal para listar menus disponibles. =====
class MenuScreen extends StatefulWidget {
  const MenuScreen({super.key});

  @override
  State<MenuScreen> createState() => _MenuScreenState();
}

// ===== Estado `_MenuScreenState` | Controla la carga remota de menus y la construccion visual de sus tarjetas. =====
class _MenuScreenState extends State<MenuScreen> {
  static const _bg = Color(0xFFF2F1F4);
  static const _card = Color(0xFFFFFFFF);
  static const _ink = Color(0xFF181818);
  static const _muted = Color(0xFF73727A);
  static const _accent = Color(0xFFD90416);
  static const _line = Color(0xFFE8E6EB);

  bool _loading = true;
  String _error = '';
  List<MenuData> _menus = [];
  Map<int, List<MenuProductData>> _productosPorMenu = {};

  @override
  void initState() {
    super.initState();
    _cargar();
  }

  Future<void> _cargar() async {
    setState(() {
      _loading = true;
      _error = '';
    });
    try {
      final menus = await BongustoApi.obtenerMenus();
      final menusTipados = menus.map(MenuData.fromMap).toList();
      final productosPorMenu = <int, List<MenuProductData>>{};
      for (final menu in menusTipados) {
        productosPorMenu[menu.id] = (await BongustoApi.obtenerProductos(
          menuId: menu.id,
        )).map(MenuProductData.fromMap).toList();
      }
      if (!mounted) return;
      setState(() {
        _menus = menusTipados;
        _productosPorMenu = productosPorMenu;
        _loading = false;
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
            'MENU',
            style: TextStyle(
              color: _accent,
              fontSize: 12,
              letterSpacing: 3,
              fontWeight: FontWeight.w800,
            ),
          ),
          SizedBox(height: 8),
          Text(
            'Solo lectura para el equipo',
            style: TextStyle(
              color: _ink,
              fontSize: 30,
              height: 1.06,
              fontWeight: FontWeight.w900,
            ),
          ),
          SizedBox(height: 10),
        ],
      ),
    );
  }

  Widget _stateCard({required IconData icon, required String text, bool retry = false}) {
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
          if (retry) ...[
            const SizedBox(height: 16),
            ElevatedButton(onPressed: _cargar, child: const Text('Reintentar')),
          ],
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

  Widget _menuCard(MenuData menu) {
    final idMenu = menu.id;
    final productos = _productosPorMenu[idMenu] ?? const [];
    return GestureDetector(
      onTap: () {
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (_) => MenuDetalleScreen(
              menu: menu.toMap(),
              productos: productos.map((item) => item.toMap()).toList(),
            ),
          ),
        );
      },
      child: Container(
        margin: const EdgeInsets.only(bottom: 16),
        padding: const EdgeInsets.all(18),
        decoration: BoxDecoration(
          color: _card,
          borderRadius: BorderRadius.circular(28),
          border: Border.all(color: _line),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              menu.nombre,
              style: const TextStyle(
                color: _ink,
                fontSize: 22,
                fontWeight: FontWeight.w900,
              ),
            ),
            if (menu.descripcion.trim().isNotEmpty) ...[
              const SizedBox(height: 8),
              Text(
                menu.descripcion,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
                style: const TextStyle(color: _muted, height: 1.45),
              ),
            ],
            const SizedBox(height: 14),
            Row(
              children: [
                Expanded(child: _metric('Platos', '${productos.length}')),
                const SizedBox(width: 10),
                Expanded(child: _metric('Menu ID', '$idMenu')),
              ],
            ),
            const SizedBox(height: 12),
            const Row(
              children: [
                Text(
                  'Toca para ver los platos',
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

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: _bg,
      appBar: AppBar(
        backgroundColor: _bg,
        foregroundColor: _ink,
        title: const Text('Menu', style: TextStyle(fontWeight: FontWeight.w800)),
      ),
      body: RefreshIndicator(
        color: _accent,
        onRefresh: _cargar,
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
                text: 'No se pudo cargar el menu.\n$_error',
                retry: true,
              )
            else if (_menus.isEmpty)
              _stateCard(
                icon: Icons.menu_book_outlined,
                text: 'No hay menus creados en Django.',
              )
            else
              ..._menus.map(_menuCard),
          ],
        ),
      ),
    );
  }
}

class MenuData {
  final int id;
  final String nombre;
  final String descripcion;

  const MenuData({
    required this.id,
    required this.nombre,
    required this.descripcion,
  });

  factory MenuData.fromMap(Map<String, dynamic> json) {
    return MenuData(
      id: MenuProductData.asInt(json['id_menu']),
      nombre: (json['nombre_menu'] ?? 'Menu').toString(),
      descripcion: (json['descripcion_menu'] ?? '').toString(),
    );
  }

  Map<String, dynamic> toMap() {
    return {
      'id_menu': id,
      'nombre_menu': nombre,
      'descripcion_menu': descripcion,
    };
  }
}

class MenuProductData {
  final String nombre;
  final String descripcion;
  final double precio;

  const MenuProductData({
    required this.nombre,
    required this.descripcion,
    required this.precio,
  });

  factory MenuProductData.fromMap(Map<String, dynamic> json) {
    return MenuProductData(
      nombre: (json['nombre_producto'] ?? '').toString(),
      descripcion: (json['descripcion_producto'] ?? '').toString(),
      precio: asDouble(json['precio_producto']),
    );
  }

  Map<String, dynamic> toMap() {
    return {
      'nombre_producto': nombre,
      'descripcion_producto': descripcion,
      'precio_producto': precio,
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
