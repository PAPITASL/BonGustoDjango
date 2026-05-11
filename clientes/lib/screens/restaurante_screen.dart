// Pantalla principal para explorar el restaurante y sus productos destacados.
import 'dart:async';

import 'package:flutter/material.dart';

import '../app_theme.dart';
import '../services/bongusto_api.dart';
import '../services/session_service.dart';
import 'app_settings_controls.dart';
import 'carrito_global.dart';
import 'carrito_screen.dart';
import 'home_screen.dart';
import 'mapa_screen.dart';
import 'pedidos_screen.dart';
import 'perfil_screen.dart';
import 'platos_screen.dart';
import 'producto_global.dart';

// Widget principal del modulo de restaurante.
class RestauranteScreen extends StatefulWidget {
  const RestauranteScreen({
    super.key,
    this.tipoPedidoInicial = 'restaurante',
  });

  final String tipoPedidoInicial;

  @override
  State<RestauranteScreen> createState() => _RestauranteScreenState();
}

// Estado que carga productos, menus y accesos relacionados con el restaurante.
class _RestauranteScreenState extends State<RestauranteScreen> {
  static Color get _bg => AppThemeColors.bg;
  static Color get _card => AppThemeColors.surface;
  static Color get _ink => AppThemeColors.text;
  static Color get _muted => AppThemeColors.muted;
  static const _accent = Color(0xFFD90416);
  static Color get _accentSoft => AppThemeColors.accentSoft;
  static Color get _line => AppThemeColors.line;

  int _currentIndex = 0;
  bool _loading = true;
  String? _error;
  List<_CategoriaData> _categorias = [];
  List<Producto> _destacados = [];
  final Map<int, int> _cantidades = {};
  String _searchText = '';
  final TextEditingController _searchController = TextEditingController();

  @override
  void initState() {
    super.initState();
    unawaited(
      SessionService.actualizarSesion({
        'tipo_pedido': widget.tipoPedidoInicial,
      }),
    );
    _cargarCatalogo();
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  Future<void> _cargarCatalogo() async {
    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      final responses = await Future.wait([
        BongustoApi.obtenerCategorias(),
        BongustoApi.obtenerProductos(destacados: true),
      ]);
      if (!mounted) {
        return;
      }
      final categoriasTipadas = List<Map<String, dynamic>>.from(
        responses[0] as List,
      ).map(_CategoriaData.fromMap).toList();
      setState(() {
        _categorias = categoriasTipadas;
        _destacados = List<Map<String, dynamic>>.from(
          responses[1] as List,
        ).map(Producto.fromApi).toList();
        _loading = false;
      });
    } catch (e) {
      if (!mounted) {
        return;
      }
      setState(() {
        _error = '$e';
        _loading = false;
      });
    }
  }

  int _cantidadSeleccionada(Producto producto) =>
      _cantidades[producto.idProducto] ?? 0;

  void _cambiarCantidad(Producto producto, int delta) {
    final actual = _cantidadSeleccionada(producto);
    final nuevaCantidad = (actual + delta).clamp(0, 99);
    setState(() {
      if (nuevaCantidad == 0) {
        _cantidades.remove(producto.idProducto);
      } else {
        _cantidades[producto.idProducto] = nuevaCantidad;
      }
    });
  }

  void _agregarAlCarrito(Producto producto) {
    final cantidad = _cantidadSeleccionada(producto);
    if (cantidad <= 0) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Selecciona una cantidad para ${producto.nombre}'),
        ),
      );
      return;
    }

    CarritoGlobal.agregarProducto(producto.copia(cantidad: cantidad));
    setState(() {
      _cantidades.remove(producto.idProducto);
    });
    unawaited(CarritoGlobal.sincronizarConBackend());
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('${producto.nombre} agregado al pedido')),
    );
  }

  Future<void> _abrirCarrito() async {
    await Navigator.push(
      context,
      MaterialPageRoute(builder: (_) => const CarritoPage()),
    );
    if (mounted) {
      setState(() {});
    }
  }

  List<_CategoriaData> get _categoriasFiltradas {
    final query = _searchText.trim().toLowerCase();
    if (query.isEmpty) {
      return _categorias;
    }
    return _categorias
        .where((categoria) => categoria.nombre.toLowerCase().contains(query))
        .toList();
  }

  List<Producto> get _destacadosFiltrados {
    final query = _searchText.trim().toLowerCase();
    if (query.isEmpty) {
      return _destacados;
    }
    return _destacados.where((producto) {
      return producto.nombre.toLowerCase().contains(query) ||
          producto.descripcion.toLowerCase().contains(query) ||
          producto.nombreCategoria.toLowerCase().contains(query);
    }).toList();
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
      backgroundColor: _card,
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

  @override
  Widget build(BuildContext context) {
    final totalItems = CarritoGlobal.totalItems();
    final categoriasFiltradas = _categoriasFiltradas;
    final destacadosFiltrados = _destacadosFiltrados;

    return Scaffold(
      backgroundColor: _bg,
      bottomNavigationBar: _bottomBar(),
      body: SafeArea(
        child: RefreshIndicator(
          color: _accent,
          onRefresh: _cargarCatalogo,
          child: ListView(
            padding: const EdgeInsets.fromLTRB(18, 16, 18, 100),
            children: [
              _heroHeader(totalItems),
              const SizedBox(height: 22),
              if (_loading)
                Padding(
                  padding: EdgeInsets.all(32),
                  child: Center(child: CircularProgressIndicator()),
                )
              else if (_error != null)
                _errorState()
              else ...[
                _searchCard(),
                const SizedBox(height: 18),
                _sectionTitle(
                  eyebrow: 'SELECCION DE LA CASA',
                  title: 'Destacados del menu',
                  subtitle:
                      'Una carta limpia y elegante con productos cargados desde el administrador de BonGusto.',
                ),
                const SizedBox(height: 14),
                if (destacadosFiltrados.isEmpty)
                  _emptySearchState()
                else
                  ...destacadosFiltrados.map(_destacadoCard),
                const SizedBox(height: 28),
                _sectionTitle(
                  eyebrow: 'CARTA COMPLETA',
                  title: 'Explorar por categoria',
                  subtitle:
                      'Sin imagenes recargadas. Solo una navegacion clara para ordenar mejor.',
                ),
                const SizedBox(height: 14),
                Wrap(
                  spacing: 10,
                  runSpacing: 10,
                  children: categoriasFiltradas.map(_categoriaChip).toList(),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _heroHeader(int totalItems) {
    return Container(
      padding: const EdgeInsets.fromLTRB(18, 18, 18, 22),
      decoration: BoxDecoration(
        color: _card,
        borderRadius: BorderRadius.circular(28),
        border: Border.all(color: _line),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.05),
            blurRadius: 24,
            offset: const Offset(0, 10),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              _iconButton(
                icon: Icons.arrow_back_rounded,
                onTap: () => Navigator.pop(context),
              ),
              const Spacer(),
              AppSettingsControls(),
              const SizedBox(width: 8),
              _cartButton(totalItems),
            ],
          ),
          const SizedBox(height: 26),
          Text(
            'BONGUSTO',
            style: TextStyle(
              color: _accent,
              fontSize: 13,
              fontWeight: FontWeight.w800,
              letterSpacing: 3.2,
            ),
          ),
          const SizedBox(height: 10),
          Text(
            'Menu y ordenar',
            style: TextStyle(
              color: _ink,
              fontSize: 34,
              height: 1.05,
              fontWeight: FontWeight.w900,
            ),
          ),
          const SizedBox(height: 12),
          Text(
            'Una experiencia mas sobria, mas premium y enfocada en el plato. Menos ruido visual, mejor lectura y pedido mas claro.',
            style: TextStyle(color: _muted, fontSize: 14, height: 1.5),
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
        borderRadius: BorderRadius.circular(22),
        border: Border.all(color: _line),
      ),
      child: TextField(
        controller: _searchController,
        onChanged: (value) => setState(() => _searchText = value),
        decoration: InputDecoration(
          hintText: 'Buscar platos, categorías o antojos...',
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

  Widget _emptySearchState() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: _card,
        borderRadius: BorderRadius.circular(22),
        border: Border.all(color: _line),
      ),
      child: Column(
        children: [
          Icon(Icons.search_off_rounded, color: _accent, size: 30),
          SizedBox(height: 12),
          Text(
            'No encontramos resultados con ese filtro. Intenta otra palabra.',
            textAlign: TextAlign.center,
            style: TextStyle(color: _muted, height: 1.5),
          ),
        ],
      ),
    );
  }

  Widget _iconButton({required IconData icon, required VoidCallback onTap}) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(18),
      child: Container(
        width: 48,
        height: 48,
        decoration: BoxDecoration(
          color: _bg,
          borderRadius: BorderRadius.circular(18),
          border: Border.all(color: _line),
        ),
        child: Icon(icon, color: _ink),
      ),
    );
  }

  Widget _cartButton(int totalItems) {
    return Stack(
      clipBehavior: Clip.none,
      children: [
        InkWell(
          onTap: _abrirCarrito,
          borderRadius: BorderRadius.circular(18),
          child: Container(
            width: 52,
            height: 52,
            decoration: BoxDecoration(
              color: _card,
              borderRadius: BorderRadius.circular(18),
              border: Border.all(color: _line),
            ),
            child: Icon(Icons.shopping_bag_outlined, color: _ink),
          ),
        ),
        if (totalItems > 0)
          Positioned(
            right: -2,
            top: -4,
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 3),
              decoration: BoxDecoration(
                color: _accent,
                borderRadius: BorderRadius.circular(999),
              ),
              child: Text(
                '$totalItems',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 11,
                  fontWeight: FontWeight.w800,
                ),
              ),
            ),
          ),
      ],
    );
  }

  Widget _sectionTitle({
    required String eyebrow,
    required String title,
    required String subtitle,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          eyebrow,
          style: TextStyle(
            color: _accent,
            fontSize: 11,
            fontWeight: FontWeight.w800,
            letterSpacing: 2.8,
          ),
        ),
        const SizedBox(height: 6),
        Text(
          title,
          style: TextStyle(
            color: _ink,
            fontSize: 24,
            fontWeight: FontWeight.w800,
          ),
        ),
        const SizedBox(height: 6),
        Text(
          subtitle,
          style: TextStyle(color: _muted, fontSize: 14, height: 1.45),
        ),
      ],
    );
  }

  Widget _destacadoCard(Producto producto) {
    return Container(
      margin: const EdgeInsets.only(bottom: 14),
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
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      producto.nombreCategoria.isEmpty
                          ? 'CHEF SPECIAL'
                          : producto.nombreCategoria.toUpperCase(),
                      style: TextStyle(
                        color: _accent,
                        fontSize: 11,
                        letterSpacing: 2.2,
                        fontWeight: FontWeight.w800,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      producto.nombre,
                      style: TextStyle(
                        color: _ink,
                        fontSize: 22,
                        height: 1.1,
                        fontWeight: FontWeight.w800,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 12),
              Text(
                '\$${producto.precio.toStringAsFixed(0)}',
                style: TextStyle(
                  color: _ink,
                  fontSize: 22,
                  fontWeight: FontWeight.w900,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Text(
            producto.descripcion.isEmpty
                ? 'Preparacion disponible para ordenar desde la carta del restaurante.'
                : producto.descripcion,
            style: TextStyle(color: _muted, fontSize: 14, height: 1.5),
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              SizedBox(width: 134, child: _cantidadSelector(producto)),
              const SizedBox(width: 12),
              Expanded(
                child: SizedBox(
                  height: 52,
                  child: ElevatedButton(
                    onPressed: () => _agregarAlCarrito(producto),
                    style: ElevatedButton.styleFrom(
                      elevation: 0,
                      backgroundColor: _accent,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(horizontal: 18),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(16),
                      ),
                    ),
                    child: const FittedBox(
                      fit: BoxFit.scaleDown,
                      child: Text(
                        'Agregar al pedido',
                        maxLines: 1,
                        style: TextStyle(
                          fontSize: 15,
                          fontWeight: FontWeight.w800,
                        ),
                      ),
                    ),
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _cantidadSelector(Producto producto) {
    final cantidad = _cantidadSeleccionada(producto);
    return Container(
      height: 52,
      padding: const EdgeInsets.symmetric(horizontal: 8),
      decoration: BoxDecoration(
        color: _bg,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: _line),
      ),
      child: Row(
        children: [
          _qtyButton(
            icon: Icons.remove,
            onTap: cantidad > 0 ? () => _cambiarCantidad(producto, -1) : null,
          ),
          Expanded(
            child: Text(
              '$cantidad',
              textAlign: TextAlign.center,
              style: TextStyle(
                color: _ink,
                fontWeight: FontWeight.w800,
                fontSize: 16,
              ),
            ),
          ),
          _qtyButton(
            icon: Icons.add,
            onTap: () => _cambiarCantidad(producto, 1),
          ),
        ],
      ),
    );
  }

  Widget _qtyButton({required IconData icon, required VoidCallback? onTap}) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(12),
      child: Container(
        width: 34,
        height: 34,
        decoration: BoxDecoration(
          color: onTap == null ? _line : _accentSoft,
          borderRadius: BorderRadius.circular(12),
        ),
        child: Icon(icon, size: 18, color: onTap == null ? _muted : _accent),
      ),
    );
  }

  Widget _categoriaChip(_CategoriaData categoria) {
    final nombre = categoria.nombre;
    return InkWell(
      onTap: () {
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (_) =>
                PlatosPage(categoriaId: categoria.id, categoriaNombre: nombre),
          ),
        ).then((_) => setState(() {}));
      },
      borderRadius: BorderRadius.circular(18),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
        decoration: BoxDecoration(
          color: _card,
          borderRadius: BorderRadius.circular(18),
          border: Border.all(color: _line),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.restaurant_menu, size: 18, color: _accent),
            const SizedBox(width: 10),
            Text(
              nombre,
              style: TextStyle(color: _ink, fontWeight: FontWeight.w700),
            ),
          ],
        ),
      ),
    );
  }

  Widget _errorState() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: _card,
        borderRadius: BorderRadius.circular(22),
        border: Border.all(color: _line),
      ),
      child: Column(
        children: [
          Icon(Icons.cloud_off_outlined, color: _accent, size: 34),
          const SizedBox(height: 12),
          Text(
            'No se pudo cargar la carta.\n$_error',
            textAlign: TextAlign.center,
            style: TextStyle(color: _muted, height: 1.5),
          ),
          const SizedBox(height: 12),
          ElevatedButton(
            onPressed: _cargarCatalogo,
            style: ElevatedButton.styleFrom(
              backgroundColor: _accent,
              foregroundColor: Colors.white,
            ),
            child: Text('Reintentar'),
          ),
        ],
      ),
    );
  }
}

class _CategoriaData {
  final int id;
  final String nombre;

  const _CategoriaData({required this.id, required this.nombre});

  factory _CategoriaData.fromMap(Map<String, dynamic> json) {
    return _CategoriaData(
      id: int.tryParse('${json['id_cate']}') ?? 0,
      nombre: (json['nombre_cate'] ?? '').toString(),
    );
  }
}
