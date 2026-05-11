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
  static const Color _accent = Color(0xFFD90416);

  bool _loading = true;
  String _error = '';
  List<MenuData> _menus = [];
  Map<int, List<MenuProductData>> _productosPorMenu = {};

  static const String _todosMenusValue = '__todos__';
  String _menuDropdownValue = _todosMenusValue;
  String _searchText = '';
  final TextEditingController _searchController = TextEditingController();

  bool get _isDark => Theme.of(context).brightness == Brightness.dark;
  Color get _bg => _isDark ? const Color(0xFF0F1117) : const Color(0xFFF2F1F4);
  Color get _card => Colors.white;
  Color get _ink => const Color(0xFF181818);
  Color get _muted => const Color(0xFF54515A);
  Color get _line => _isDark ? const Color(0xFF313544) : const Color(0xFFE8E6EB);

  @override
  void initState() {
    super.initState();
    _cargar();
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
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
      final resultados = await Future.wait(
        menusTipados.map((menu) async {
          final productos = await BongustoApi.obtenerProductos(menuId: menu.id);
          return MapEntry(
            menu.id,
            productos.map(MenuProductData.fromMap).toList(),
          );
        }),
      );
      for (final entry in resultados) {
        productosPorMenu[entry.key] = entry.value;
      }
      if (!mounted) return;
      setState(() {
        _menus = menusTipados;
        _productosPorMenu = productosPorMenu;
        if (_menuDropdownValue != _todosMenusValue &&
            !_menus.any((menu) => menu.id.toString() == _menuDropdownValue)) {
          _menuDropdownValue = _todosMenusValue;
        }
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

  List<MenuData> get _menusFiltrados {
    final query = _searchText.trim().toLowerCase();
    return _menus.where((menu) {
      final matchesDropdown = _menuDropdownValue == _todosMenusValue ||
          menu.id.toString() == _menuDropdownValue;
      final nombre = menu.nombre.toLowerCase();
      final descripcion = menu.descripcion.toLowerCase();
      final matchesSearch =
          query.isEmpty || nombre.contains(query) || descripcion.contains(query);
      return matchesDropdown && matchesSearch;
    }).toList();
  }

  Widget _hero() {
    return Container(
      padding: const EdgeInsets.all(22),
      decoration: BoxDecoration(
        color: _card,
        borderRadius: BorderRadius.circular(30),
        border: Border.all(color: _line),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'MENU',
            style: TextStyle(
              color: _accent,
              fontSize: 12,
              letterSpacing: 3,
              fontWeight: FontWeight.w800,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Vista de consulta para meseros',
            style: TextStyle(
              color: _ink,
              fontSize: 30,
              height: 1.06,
              fontWeight: FontWeight.w900,
            ),
          ),
          const SizedBox(height: 10),
          Text(
            'Filtra por nombre o selecciona un menu para revisar sus platos.',
            style: TextStyle(color: _muted, fontSize: 14, height: 1.5),
          ),
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
          Text(
            text,
            textAlign: TextAlign.center,
            style: TextStyle(color: _ink),
          ),
          if (retry) ...[
            const SizedBox(height: 16),
            ElevatedButton(onPressed: _cargar, child: const Text('Reintentar')),
          ],
        ],
      ),
    );
  }


  Widget _searchCard() {
    return Container(
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(
        color: _card,
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: _line),
      ),
      child: TextField(
        controller: _searchController,
        style: TextStyle(color: _ink),
        onChanged: (value) => setState(() => _searchText = value),
        decoration: InputDecoration(
          hintText: 'Buscar menu, bebidas, brunch...',
          hintStyle: TextStyle(color: _muted),
          fillColor: const Color(0xFFF2F3F7),
          prefixIcon: Icon(Icons.search_rounded, color: _muted),
          suffixIcon: _searchText.isEmpty
              ? null
              : IconButton(
                  onPressed: () {
                    _searchController.clear();
                    setState(() => _searchText = '');
                  },
                  icon: Icon(Icons.close_rounded, color: _muted),
                ),
          border: InputBorder.none,
          contentPadding: const EdgeInsets.symmetric(
            horizontal: 14,
            vertical: 16,
          ),
        ),
      ),
    );
  }

  Widget _menuDropdown() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 2),
      decoration: BoxDecoration(
        color: _card,
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: _line),
      ),
      child: DropdownButtonHideUnderline(
        child: DropdownButton<String>(
          value: _menuDropdownValue,
          isExpanded: true,
          dropdownColor: _card,
          icon: Icon(Icons.keyboard_arrow_down_rounded, color: _muted),
          style: TextStyle(
            color: _ink,
            fontSize: 14,
            fontWeight: FontWeight.w700,
          ),
          items: [
            const DropdownMenuItem<String>(
              value: _todosMenusValue,
              child: Text('Menu: todos'),
            ),
            ..._menus.map(
              (menu) => DropdownMenuItem<String>(
                value: menu.id.toString(),
                child: Text(menu.nombre),
              ),
            ),
          ],
          onChanged: (value) {
            if (value == null) {
              return;
            }
            setState(() => _menuDropdownValue = value);
          },
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
          Text(label, style: TextStyle(color: _muted, fontSize: 12)),
          const SizedBox(height: 4),
          Text(
            value,
            style: TextStyle(
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
              style: TextStyle(
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
                style: TextStyle(color: _muted, height: 1.45),
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
            Row(
              children: [
                Text(
                  'Toca para ver los platos',
                  style: TextStyle(
                    color: _accent,
                    fontWeight: FontWeight.w800,
                  ),
                ),
                const SizedBox(width: 6),
                const Icon(Icons.arrow_forward_rounded, color: _accent, size: 18),
              ],
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final menusFiltrados = _menusFiltrados;

    return Scaffold(
      backgroundColor: _bg,
      appBar: AppBar(
        backgroundColor: _bg,
        foregroundColor: _isDark ? Colors.white : _ink,
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
            _searchCard(),
            if (_menus.isNotEmpty) ...[
              const SizedBox(height: 10),
              _menuDropdown(),
            ],
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
            else if (menusFiltrados.isEmpty)
              _stateCard(
                icon: Icons.search_off_rounded,
                text: 'No encontramos menus con ese filtro.',
              )
            else
              ...menusFiltrados.map(_menuCard),
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
