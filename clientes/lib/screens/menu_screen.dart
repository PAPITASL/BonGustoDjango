// Pantalla que lista menus y categorias disponibles para el cliente.
import 'package:flutter/material.dart';

import '../app_theme.dart';
import '../services/bongusto_api.dart';
import 'app_settings_controls.dart';
import 'home_screen.dart';
import 'mapa_screen.dart';
import 'pedidos_screen.dart';
import 'perfil_screen.dart';
import 'platos_screen.dart';

// Widget principal del modulo de menu.
class MenuScreen extends StatefulWidget {
  const MenuScreen({super.key});

  @override
  State<MenuScreen> createState() => _MenuScreenState();
}

// Estado que carga menus desde la API y construye la vista principal.
class _MenuScreenState extends State<MenuScreen> {
  static Color get _bg => AppThemeColors.bg;
  static Color get _card => AppThemeColors.surface;
  static Color get _ink => AppThemeColors.text;
  static Color get _muted => AppThemeColors.muted;
  static const _accent = Color(0xFFD90416);
  static Color get _accentSoft => AppThemeColors.accentSoft;
  static Color get _line => AppThemeColors.line;
  static const _artRose = Color(0xFFE1B5B3);
  static const _artCream = Color(0xFFF7E2BA);
  static const _artGreen = Color(0xFFD6E8B4);
  static const _artBlue = Color(0xFFD9E0F4);
  static const _artSand = Color(0xFFE6D4B7);

  int _currentIndex = 0;
  bool _loading = true;
  String? _error;
  List<_MenuItemData> _menus = [];
  int? _selectedMenuId;
  String _searchText = '';
  static const String _todosMenusValue = '__todos__';
  String _menuDropdownValue = _todosMenusValue;
  final TextEditingController _searchController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _cargarMenus();
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  Future<void> _cargarMenus() async {
    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      final menus = await BongustoApi.obtenerMenus();
      if (!mounted) return;
      final menusTipados = menus.map(_MenuItemData.fromMap).toList();
      setState(() {
        _menus = menusTipados;
        _selectedMenuId = menusTipados.isNotEmpty
            ? menusTipados.first.id
            : null;
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

  void _abrirSeccion(int index) {
    setState(() => _currentIndex = index);
    if (index == 0) {
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (_) => const HomeScreen()),
      );
      return;
    }
    if (index == 1) {
      Navigator.push(
        context,
        MaterialPageRoute(builder: (_) => const PedidosScreen()),
      );
      return;
    }
    if (index == 2) {
      Navigator.push(
        context,
        MaterialPageRoute(builder: (_) => const MapScreen()),
      );
      return;
    }
    if (index == 3) {
      Navigator.push(
        context,
        MaterialPageRoute(builder: (_) => const PerfilScreen()),
      );
    }
  }

  Widget _bottomBar() {
    return BottomNavigationBar(
      currentIndex: _currentIndex,
      onTap: _abrirSeccion,
      type: BottomNavigationBarType.fixed,
      selectedItemColor: _accent,
      unselectedItemColor: _muted,
      showUnselectedLabels: true,
      items: [
        BottomNavigationBarItem(
          icon: Icon(Icons.home_outlined),
          label: 'Inicio',
        ),
        BottomNavigationBarItem(
          icon: Icon(Icons.list_alt_outlined),
          label: 'Pedidos',
        ),
        BottomNavigationBarItem(icon: Icon(Icons.map_outlined), label: 'Mapa'),
        BottomNavigationBarItem(
          icon: Icon(Icons.person_outline),
          label: 'Perfil',
        ),
      ],
    );
  }

  void _abrirMenu(_MenuItemData menu) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => PlatosPage(
          categoriaId: null,
          categoriaNombre: menu.nombre,
          menuId: menu.id,
          menuNombre: menu.nombre,
        ),
      ),
    );
  }

  List<_MenuItemData> get _menusFiltrados {
    final query = _searchText.trim().toLowerCase();
    return _menus.where((menu) {
      final matchesDropdown =
          _menuDropdownValue == _todosMenusValue ||
          menu.id.toString() == _menuDropdownValue;
      final nombre = menu.nombre.toLowerCase();
      final descripcion = menu.descripcion.toLowerCase();
      final matchesSearch =
          query.isEmpty || nombre.contains(query) || descripcion.contains(query);
      return matchesDropdown && matchesSearch;
    }).toList();
  }

  @override
  Widget build(BuildContext context) {
    final menusFiltrados = _menusFiltrados;
    return Scaffold(
      backgroundColor: _bg,
      appBar: AppBar(
        backgroundColor: _bg,
        foregroundColor: _ink,
        title: Text('Menus', style: TextStyle(fontWeight: FontWeight.w800)),
        actions: [
          Padding(
            padding: const EdgeInsets.only(right: 12),
            child: AppSettingsControls(),
          ),
        ],
      ),
      bottomNavigationBar: _bottomBar(),
      body: RefreshIndicator(
        color: _accent,
        onRefresh: _cargarMenus,
        child: ListView(
          padding: const EdgeInsets.fromLTRB(20, 8, 20, 100),
          children: [
            Container(
              padding: const EdgeInsets.fromLTRB(22, 24, 22, 24),
              decoration: BoxDecoration(
                color: _card,
                borderRadius: BorderRadius.circular(30),
                border: Border.all(color: _line),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'CARTA BONGUSTO',
                    style: TextStyle(
                      color: _accent,
                      fontSize: 12,
                      letterSpacing: 3,
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                  SizedBox(height: 8),
                  Text(
                    'Selecciona un menu',
                    style: TextStyle(
                      color: _ink,
                      fontSize: 31,
                      height: 1.06,
                      fontWeight: FontWeight.w900,
                    ),
                  ),
                  SizedBox(height: 10),
                  Text(
                    'Primero eliges el menu. Luego te mostramos todos los platos de ese menu en una carta.',
                    style: TextStyle(color: _muted, fontSize: 14, height: 1.5),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 18),
            _searchCard(),
            if (_menus.isNotEmpty) ...[
              const SizedBox(height: 10),
              _menuDropdown(),
            ],
            const SizedBox(height: 18),
            if (_loading)
              Padding(
                padding: EdgeInsets.all(32),
                child: Center(child: CircularProgressIndicator()),
              )
            else if (_error != null)
              _stateCard(
                icon: Icons.cloud_off_outlined,
                text: 'No se pudieron cargar los menus.\n$_error',
              )
            else if (_menus.isEmpty)
              _stateCard(
                icon: Icons.menu_book_outlined,
                text: 'No hay menus creados en el administrador de Django.',
              )
            else if (menusFiltrados.isEmpty)
              _stateCard(
                icon: Icons.search_off_rounded,
                text:
                    'No encontramos un menu con ese nombre. Prueba con otra palabra.',
              )
            else
              GridView.builder(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                itemCount: menusFiltrados.length,
                gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                  crossAxisCount: 2,
                  crossAxisSpacing: 14,
                  mainAxisSpacing: 14,
                  mainAxisExtent: 250,
                ),
                itemBuilder: (context, index) {
                  final menu = menusFiltrados[index];
                  final selected = menu.id == _selectedMenuId;
                  return _menuCard(menu, selected: selected);
                },
              ),
          ],
        ),
      ),
    );
  }

  Widget _stateCard({required IconData icon, required String text}) {
    return Container(
      padding: const EdgeInsets.all(22),
      decoration: BoxDecoration(
        color: _card,
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: _line),
      ),
      child: Column(
        children: [
          Icon(icon, color: _accent, size: 30),
          const SizedBox(height: 12),
          Text(
            text,
            textAlign: TextAlign.center,
            style: TextStyle(color: _muted, height: 1.5),
          ),
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
        onChanged: (value) => setState(() => _searchText = value),
        decoration: InputDecoration(
          hintText: 'Buscar menu, brunch, bebidas, postres...',
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

  Widget _menuCard(_MenuItemData menu, {required bool selected}) {
    return InkWell(
      onTap: () {
        setState(() {
          _selectedMenuId = menu.id;
        });
        _abrirMenu(menu);
      },
      borderRadius: BorderRadius.circular(28),
      child: Container(
        padding: const EdgeInsets.all(18),
        decoration: BoxDecoration(
          color: selected ? _accentSoft : _card,
          borderRadius: BorderRadius.circular(28),
          border: Border.all(
            color: selected ? _accent : _line,
            width: selected ? 1.6 : 1.0,
          ),
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
            _menuArtwork(menu.nombre, selected: selected),
            const SizedBox(height: 18),
            Text(
              menu.nombre,
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
              style: TextStyle(
                color: _ink,
                fontSize: 19,
                height: 1.1,
                fontWeight: FontWeight.w800,
              ),
            ),
            const SizedBox(height: 10),
            Expanded(
              child: Text(
                menu.descripcion.isEmpty
                    ? 'Toca para ver todos los platos de este menu.'
                    : menu.descripcion,
                maxLines: 4,
                overflow: TextOverflow.ellipsis,
                style: TextStyle(color: _muted, fontSize: 13, height: 1.45),
              ),
            ),
            const SizedBox(height: 14),
            Row(
              children: [
                Text(
                  'Ver platos',
                  style: TextStyle(
                    color: selected ? _accent : _ink,
                    fontWeight: FontWeight.w800,
                    fontSize: 16,
                  ),
                ),
                const SizedBox(width: 8),
                Icon(
                  Icons.arrow_forward_rounded,
                  size: 20,
                  color: selected ? _accent : _ink,
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _menuArtwork(String nombre, {required bool selected}) {
    final style = _artStyle(nombre);
    return Container(
      width: 86,
      height: 86,
      decoration: BoxDecoration(
        color: style.background,
        borderRadius: BorderRadius.circular(22),
        border: Border.all(
          color: selected ? _accent.withValues(alpha: 0.28) : Colors.white,
          width: 2,
        ),
      ),
      child: _menuIllustration(nombre, style),
    );
  }

  Widget _menuIllustration(String nombre, _MenuArtStyle style) {
    final key = nombre.toLowerCase();
    if (key.contains('brunch') || key.contains('desayuno')) {
      return Stack(
        children: [
          Positioned(
            left: -6,
            top: 8,
            child: Container(
              width: 70,
              height: 46,
              decoration: BoxDecoration(
                color: const Color(0xFFFFF6DE),
                borderRadius: BorderRadius.circular(30),
              ),
            ),
          ),
          Positioned(
            left: 8,
            top: 18,
            child: Container(
              width: 26,
              height: 26,
              decoration: BoxDecoration(
                color: Color(0xFFF4C531),
                shape: BoxShape.circle,
              ),
            ),
          ),
          Positioned(
            right: 8,
            bottom: 10,
            child: Transform.rotate(
              angle: -0.45,
              child: Container(
                width: 26,
                height: 18,
                decoration: BoxDecoration(
                  color: const Color(0xFF86B96E),
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: const Color(0xFF4E7E38), width: 2),
                ),
              ),
            ),
          ),
          Positioned(
            right: 16,
            bottom: 14,
            child: Container(
              width: 6,
              height: 6,
              decoration: BoxDecoration(
                color: Color(0xFFDAF0C6),
                shape: BoxShape.circle,
              ),
            ),
          ),
        ],
      );
    }
    if (key.contains('waffle') || key.contains('cafe')) {
      return Stack(
        children: [
          Positioned(
            left: 8,
            top: 10,
            child: Container(
              width: 42,
              height: 42,
              decoration: BoxDecoration(
                color: const Color(0xFFE8C78B),
                borderRadius: BorderRadius.circular(16),
              ),
            ),
          ),
          Positioned(
            left: 18,
            top: 20,
            child: Container(
              width: 22,
              height: 2,
              color: const Color(0xFFC0944C),
            ),
          ),
          Positioned(
            left: 18,
            top: 28,
            child: Container(
              width: 22,
              height: 2,
              color: const Color(0xFFC0944C),
            ),
          ),
          Positioned(
            left: 22,
            top: 16,
            child: Container(
              width: 2,
              height: 22,
              color: const Color(0xFFC0944C),
            ),
          ),
          Positioned(
            left: 32,
            top: 16,
            child: Container(
              width: 2,
              height: 22,
              color: const Color(0xFFC0944C),
            ),
          ),
          Positioned(
            right: 12,
            bottom: 14,
            child: Container(
              width: 24,
              height: 24,
              decoration: BoxDecoration(
                color: Color(0xFF7B4B2A),
                shape: BoxShape.circle,
              ),
            ),
          ),
          Positioned(
            right: 10,
            bottom: 12,
            child: Container(
              width: 28,
              height: 28,
              decoration: BoxDecoration(
                border: Border.all(color: const Color(0xFFF1E4D6), width: 4),
                shape: BoxShape.circle,
              ),
            ),
          ),
        ],
      );
    }
    if (key.contains('fuerte') || key.contains('almuerzo')) {
      return Stack(
        children: [
          Positioned(
            left: 10,
            bottom: 12,
            child: Container(
              width: 56,
              height: 28,
              decoration: BoxDecoration(
                color: const Color(0xFFC77469),
                borderRadius: BorderRadius.circular(24),
              ),
            ),
          ),
          Positioned(
            left: 20,
            bottom: 18,
            child: Container(
              width: 18,
              height: 18,
              decoration: BoxDecoration(
                color: const Color(0xFF8A463C),
                borderRadius: BorderRadius.circular(20),
              ),
            ),
          ),
          Positioned(
            left: 30,
            bottom: 22,
            child: Transform.rotate(
              angle: 0.5,
              child: Container(
                width: 30,
                height: 8,
                decoration: BoxDecoration(
                  color: const Color(0xFFF4EBDD),
                  borderRadius: BorderRadius.circular(10),
                ),
              ),
            ),
          ),
          Positioned(
            right: 10,
            top: 10,
            child: Container(
              width: 16,
              height: 16,
              decoration: BoxDecoration(
                color: Color(0xFFF0D6D1),
                shape: BoxShape.circle,
              ),
            ),
          ),
        ],
      );
    }
    if (key.contains('veg') || key.contains('salud')) {
      return Stack(
        children: [
          Positioned(
            right: 8,
            top: 10,
            child: Transform.rotate(
              angle: 0.35,
              child: Container(
                width: 16,
                height: 42,
                decoration: BoxDecoration(
                  color: const Color(0xFF9EC67A),
                  borderRadius: BorderRadius.circular(20),
                ),
              ),
            ),
          ),
          Positioned(
            right: 24,
            top: 8,
            child: Container(
              width: 12,
              height: 12,
              decoration: BoxDecoration(
                color: Color(0xFF7AA44D),
                shape: BoxShape.circle,
              ),
            ),
          ),
          Positioned(
            left: 12,
            bottom: 12,
            child: Container(
              width: 30,
              height: 30,
              decoration: BoxDecoration(
                color: Color(0xFF8FB65E),
                shape: BoxShape.circle,
              ),
            ),
          ),
          Positioned(
            left: 20,
            bottom: 20,
            child: Container(
              width: 10,
              height: 10,
              decoration: BoxDecoration(
                color: Color(0xFFDDF2C3),
                shape: BoxShape.circle,
              ),
            ),
          ),
        ],
      );
    }
    if (key.contains('coctel') ||
        key.contains('bar') ||
        key.contains('bebida')) {
      return Stack(
        children: [
          Positioned(
            right: 14,
            bottom: 12,
            child: Container(
              width: 48,
              height: 28,
              decoration: BoxDecoration(
                color: Color(0xFFF2B1B7),
                borderRadius: BorderRadius.only(
                  topLeft: Radius.circular(24),
                  topRight: Radius.circular(24),
                  bottomLeft: Radius.circular(10),
                  bottomRight: Radius.circular(10),
                ),
              ),
            ),
          ),
          Positioned(
            right: 24,
            bottom: 8,
            child: Container(
              width: 4,
              height: 24,
              decoration: BoxDecoration(
                color: const Color(0xFF8C4648),
                borderRadius: BorderRadius.circular(8),
              ),
            ),
          ),
          Positioned(
            left: 14,
            top: 14,
            child: Transform.rotate(
              angle: -0.45,
              child: Container(
                width: 24,
                height: 24,
                decoration: BoxDecoration(
                  color: const Color(0xFFF8E095),
                  borderRadius: BorderRadius.circular(16),
                ),
              ),
            ),
          ),
        ],
      );
    }
    if (key.contains('tostada') || key.contains('postre')) {
      return Stack(
        children: [
          Positioned(
            left: 14,
            top: 16,
            child: Container(
              width: 42,
              height: 28,
              decoration: BoxDecoration(
                color: const Color(0xFFD69763),
                borderRadius: BorderRadius.circular(14),
              ),
            ),
          ),
          Positioned(
            left: 18,
            top: 20,
            child: Container(
              width: 34,
              height: 20,
              decoration: BoxDecoration(
                color: const Color(0xFFF3D7B8),
                borderRadius: BorderRadius.circular(12),
              ),
            ),
          ),
          Positioned(
            right: 16,
            bottom: 14,
            child: Container(
              width: 26,
              height: 26,
              decoration: BoxDecoration(
                color: const Color(0xFFF6E4B3),
                borderRadius: BorderRadius.circular(14),
              ),
            ),
          ),
        ],
      );
    }

    return Stack(
      children: [
        Positioned(
          left: 10,
          bottom: 10,
          child: Container(
            width: 52,
            height: 34,
            decoration: BoxDecoration(
              color: style.primary,
              borderRadius: BorderRadius.circular(24),
            ),
          ),
        ),
        Positioned(
          right: 10,
          top: 12,
          child: Container(
            width: 18,
            height: 18,
            decoration: BoxDecoration(
              color: style.secondary,
              shape: BoxShape.circle,
            ),
          ),
        ),
      ],
    );
  }

  _MenuArtStyle _artStyle(String nombre) {
    final key = nombre.toLowerCase();
    if (key.contains('brunch') || key.contains('desayuno')) {
      return const _MenuArtStyle(
        background: _artRose,
        primary: Color(0xFFC96F66),
        secondary: Color(0xFFF7DDD7),
        accent: Color(0xFF8B4138),
        icon: Icons.restaurant_rounded,
      );
    }
    if (key.contains('tostada') || key.contains('postre')) {
      return const _MenuArtStyle(
        background: _artCream,
        primary: Color(0xFFF0CF8F),
        secondary: Color(0xFFFFF6DE),
        accent: Color(0xFFD29D2E),
        icon: Icons.icecream_rounded,
      );
    }
    if (key.contains('waffle') || key.contains('cafe')) {
      return const _MenuArtStyle(
        background: _artSand,
        primary: Color(0xFFD0B18A),
        secondary: Color(0xFFF3E4D0),
        accent: Color(0xFF9A6B3A),
        icon: Icons.coffee_rounded,
      );
    }
    if (key.contains('fuerte') || key.contains('almuerzo')) {
      return const _MenuArtStyle(
        background: _artBlue,
        primary: Color(0xFF9FB0DA),
        secondary: Color(0xFFF3F5FD),
        accent: Color(0xFF556EA8),
        icon: Icons.dinner_dining_rounded,
      );
    }
    if (key.contains('veg') || key.contains('salud')) {
      return const _MenuArtStyle(
        background: _artGreen,
        primary: Color(0xFF8EBA6E),
        secondary: Color(0xFFEAF6D8),
        accent: Color(0xFF5B8A39),
        icon: Icons.eco_rounded,
      );
    }
    if (key.contains('coctel') ||
        key.contains('bar') ||
        key.contains('bebida')) {
      return const _MenuArtStyle(
        background: _artRose,
        primary: Color(0xFFE58C97),
        secondary: Color(0xFFFFE3E7),
        accent: Color(0xFFBB4655),
        icon: Icons.local_bar_rounded,
      );
    }
    return const _MenuArtStyle(
      background: _artRose,
      primary: Color(0xFFD39592),
      secondary: Color(0xFFF7E6E4),
      accent: Color(0xFFA45955),
      icon: Icons.restaurant_menu_rounded,
    );
  }
}

class _MenuItemData {
  final int id;
  final String nombre;
  final String descripcion;

  const _MenuItemData({
    required this.id,
    required this.nombre,
    required this.descripcion,
  });

  factory _MenuItemData.fromMap(Map<String, dynamic> json) {
    return _MenuItemData(
      id: int.tryParse('${json['id_menu']}') ?? 0,
      nombre: (json['nombre_menu'] ?? 'Menu').toString(),
      descripcion: (json['descripcion_menu'] ?? '').toString(),
    );
  }
}

class _MenuArtStyle {
  final Color background;
  final Color primary;
  final Color secondary;
  final Color accent;
  final IconData icon;

  const _MenuArtStyle({
    required this.background,
    required this.primary,
    required this.secondary,
    required this.accent,
    required this.icon,
  });
}
