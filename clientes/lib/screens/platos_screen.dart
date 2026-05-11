// Pantalla que lista platos o productos filtrados por categoria o menu.
import 'dart:async';

import 'package:flutter/material.dart';

import '../app_theme.dart';
import '../services/bongusto_api.dart';
import 'app_settings_controls.dart';
import 'carrito_global.dart';
import 'carrito_screen.dart';
import 'producto_global.dart';

// Widget principal del listado de platos disponibles.
class PlatosPage extends StatefulWidget {
  final int? categoriaId;
  final String categoriaNombre;
  final int? menuId;
  final String? menuNombre;

  const PlatosPage({
    super.key,
    required this.categoriaId,
    required this.categoriaNombre,
    this.menuId,
    this.menuNombre,
  });

  @override
  State<PlatosPage> createState() => _PlatosPageState();
}

class _PlatosPageState extends State<PlatosPage> {
  // Estado que carga productos, filtra resultados y los agrega al carrito.
  static Color get _bg => AppThemeColors.bg;
  static Color get _card => AppThemeColors.surface;
  static Color get _ink => AppThemeColors.text;
  static Color get _muted => AppThemeColors.muted;
  static const _accent = Color(0xFFD90416);
  static Color get _accentSoft => AppThemeColors.accentSoft;
  static Color get _line => AppThemeColors.line;
  static const String _todasCategoriasValue = '__todas__';

  bool _loading = true;
  String? _error;
  List<Producto> _productos = [];
  List<String> _categoriasRestaurante = [];
  final Map<int, int> _cantidades = {};
  String _searchText = '';
  _OrdenPlatos _ordenSeleccionado = _OrdenPlatos.relevancia;
  String _categoriaDropdownValue = _todasCategoriasValue;
  final Set<_RangoPrecioFiltro> _rangosPrecioSeleccionados = {};
  final TextEditingController _searchController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _cargarProductos();
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  Future<void> _cargarProductos() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final responses = await Future.wait([
        BongustoApi.obtenerProductos(
          categoriaId: widget.categoriaId,
          menuId: widget.menuId,
        ),
        BongustoApi.obtenerCategorias(),
      ]);
      if (!mounted) {
        return;
      }
      final categorias = List<Map<String, dynamic>>.from(responses[1] as List)
          .map((item) => (item['nombre_cate'] ?? '').toString().trim())
          .where((categoria) => categoria.isNotEmpty)
          .toSet()
          .toList()
        ..sort((a, b) => a.toLowerCase().compareTo(b.toLowerCase()));
      setState(() {
        _productos = List<Map<String, dynamic>>.from(
          responses[0] as List,
        ).map(Producto.fromApi).toList();
        _categoriasRestaurante = categorias;
        if (_categoriaDropdownValue != _todasCategoriasValue &&
            !_categoriasRestaurante.contains(_categoriaDropdownValue)) {
          _categoriaDropdownValue = _todasCategoriasValue;
        }
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

  List<Producto> get _productosFiltrados {
    final query = _searchText.trim().toLowerCase();
    final categoriaSeleccionada = _categoriaDropdownValue == _todasCategoriasValue
        ? null
        : _categoriaDropdownValue.toLowerCase().trim();
    final filtrados = _productos.where((producto) {
      final nombre = producto.nombre.toLowerCase();
      final descripcion = producto.descripcion.toLowerCase();
      final categoria = producto.nombreCategoria.toLowerCase();
      final matchesQuery =
          query.isEmpty ||
          nombre.contains(query) ||
          descripcion.contains(query) ||
          categoria.contains(query);
      final matchesCategoria =
          categoriaSeleccionada == null ||
          categoriaSeleccionada ==
              producto.nombreCategoria.toLowerCase().trim();
      final matchesPrecio =
          _rangosPrecioSeleccionados.isEmpty ||
          _rangosPrecioSeleccionados.any((filtro) => filtro.matches(producto));

      return matchesQuery && matchesCategoria && matchesPrecio;
    }).toList();

    switch (_ordenSeleccionado) {
      case _OrdenPlatos.relevancia:
        return filtrados;
      case _OrdenPlatos.precioMenor:
        filtrados.sort((a, b) => a.precio.compareTo(b.precio));
        return filtrados;
      case _OrdenPlatos.precioMayor:
        filtrados.sort((a, b) => b.precio.compareTo(a.precio));
        return filtrados;
      case _OrdenPlatos.nombre:
        filtrados.sort(
          (a, b) => a.nombre.toLowerCase().compareTo(b.nombre.toLowerCase()),
        );
        return filtrados;
    }
  }

  List<String> get _categoriasDisponibles {
    if (_categoriasRestaurante.isNotEmpty) {
      return _categoriasRestaurante;
    }
    final categoriasProductos = _productos
        .map((producto) => producto.nombreCategoria.trim())
        .where((categoria) => categoria.isNotEmpty)
        .toSet()
        .toList()
      ..sort((a, b) => a.toLowerCase().compareTo(b.toLowerCase()));
    return categoriasProductos;
  }

  int get _filtrosActivos =>
      (_categoriaDropdownValue == _todasCategoriasValue ? 0 : 1) +
      _rangosPrecioSeleccionados.length +
      (_searchText.trim().isEmpty ? 0 : 1);

  void _limpiarFiltros() {
    _searchController.clear();
    setState(() {
      _searchText = '';
      _categoriaDropdownValue = _todasCategoriasValue;
      _rangosPrecioSeleccionados.clear();
      _ordenSeleccionado = _OrdenPlatos.relevancia;
    });
  }

  @override
  Widget build(BuildContext context) {
    final totalItems = CarritoGlobal.totalItems();
    final productosFiltrados = _productosFiltrados;

    return Scaffold(
      backgroundColor: _bg,
      appBar: AppBar(
        backgroundColor: _bg,
        foregroundColor: _ink,
        elevation: 0,
        scrolledUnderElevation: 0,
        titleSpacing: 0,
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              (widget.menuNombre ?? widget.categoriaNombre).toUpperCase(),
              style: TextStyle(
                color: _accent,
                fontSize: 11,
                letterSpacing: 2.4,
                fontWeight: FontWeight.w800,
              ),
            ),
            Text(
              'Platos del menu',
              style: TextStyle(
                color: _ink,
                fontSize: 20,
                fontWeight: FontWeight.w800,
              ),
            ),
          ],
        ),
        actions: [
          Padding(
            padding: const EdgeInsets.only(right: 8),
            child: AppSettingsControls(),
          ),
          Padding(
            padding: const EdgeInsets.only(right: 12),
            child: _cartActionButton(totalItems),
          ),
        ],
      ),
      body: RefreshIndicator(
        color: _accent,
        onRefresh: _cargarProductos,
        child: _loading
            ? Center(child: CircularProgressIndicator())
            : _error != null
            ? ListView(
                padding: const EdgeInsets.all(18),
                children: [
                  Container(
                    padding: const EdgeInsets.all(20),
                    decoration: BoxDecoration(
                      color: _card,
                      borderRadius: BorderRadius.circular(22),
                      border: Border.all(color: _line),
                    ),
                    child: Column(
                      children: [
                        Icon(Icons.cloud_off_outlined, color: _accent),
                        const SizedBox(height: 12),
                        Text(
                          'No se pudieron cargar los platos.\n$_error',
                          textAlign: TextAlign.center,
                          style: TextStyle(color: _muted, height: 1.5),
                        ),
                        const SizedBox(height: 12),
                        ElevatedButton(
                          onPressed: _cargarProductos,
                          style: ElevatedButton.styleFrom(
                            backgroundColor: _accent,
                            foregroundColor: Colors.white,
                          ),
                          child: Text('Reintentar'),
                        ),
                      ],
                    ),
                  ),
                ],
              )
            : _productos.isEmpty
            ? ListView(
                padding: const EdgeInsets.all(24),
                children: [
                  Center(
                    child: Text(
                      'No hay productos en esta categoria',
                      style: TextStyle(color: _muted),
                    ),
                  ),
                ],
              )
            : ListView(
                padding: const EdgeInsets.fromLTRB(18, 10, 18, 100),
                children: [
                  _filtersBar(productosFiltrados.length),
                  const SizedBox(height: 14),
                  if (productosFiltrados.isEmpty)
                    _emptyFilterState()
                  else
                    ...List.generate(productosFiltrados.length, (index) {
                      final producto = productosFiltrados[index];
                      return Padding(
                        padding: EdgeInsets.only(
                          bottom: index == productosFiltrados.length - 1
                              ? 0
                              : 12,
                        ),
                        child: _platoCard(producto),
                      );
                    }),
                ],
              ),
      ),
    );
  }

  Widget _filtersBar(int totalResultados) {
    final categorias = _categoriasDisponibles;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
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
              hintText: 'Buscar plato, ingrediente o categoría...',
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
        ),
        if (categorias.isNotEmpty) ...[
          const SizedBox(height: 10),
          _menuDropdown(categorias),
        ],
        const SizedBox(height: 12),
        Row(
          children: [
            Expanded(
              child: Text(
                _filtrosActivos == 0
                    ? '$totalResultados platos disponibles'
                    : '$totalResultados resultados · $_filtrosActivos filtros',
                style: TextStyle(
                  color: _muted,
                  fontSize: 13,
                  fontWeight: FontWeight.w700,
                ),
              ),
            ),
            TextButton.icon(
              onPressed: _filtrosActivos == 0 ? null : _limpiarFiltros,
              icon: Icon(Icons.restart_alt_rounded, size: 18),
              label: Text('Ver todo'),
              style: TextButton.styleFrom(
                foregroundColor: _accent,
                disabledForegroundColor: _muted.withValues(alpha: 0.45),
              ),
            ),
          ],
        ),
        const SizedBox(height: 4),
        _filterSection(
          title: 'Precio',
          children: _RangoPrecioFiltro.values.map((rango) {
            return _filterChip(
              label: rango.label,
              icon: Icons.payments_outlined,
              selected: _rangosPrecioSeleccionados.contains(rango),
              onSelected: (selected) {
                setState(() {
                  if (selected) {
                    _rangosPrecioSeleccionados.add(rango);
                  } else {
                    _rangosPrecioSeleccionados.remove(rango);
                  }
                });
              },
            );
          }).toList(),
        ),
        const SizedBox(height: 2),
        Text(
          'Ordenar por',
          style: TextStyle(
            color: _ink,
            fontSize: 13,
            fontWeight: FontWeight.w900,
          ),
        ),
        const SizedBox(height: 8),
        SingleChildScrollView(
          scrollDirection: Axis.horizontal,
          child: Row(
            children: _OrdenPlatos.values.map((orden) {
              final selected = orden == _ordenSeleccionado;
              return Padding(
                padding: const EdgeInsets.only(right: 8),
                child: ChoiceChip(
                  label: Text(orden.label),
                  selected: selected,
                  onSelected: (_) => setState(() => _ordenSeleccionado = orden),
                  selectedColor: _accentSoft,
                  backgroundColor: _card,
                  labelStyle: TextStyle(
                    color: selected ? _accent : _ink,
                    fontWeight: FontWeight.w700,
                  ),
                  side: BorderSide(color: selected ? _accent : _line),
                ),
              );
            }).toList(),
          ),
        ),
      ],
    );
  }

  Widget _menuDropdown(List<String> categorias) {
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
          value: _categoriaDropdownValue,
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
              value: _todasCategoriasValue,
              child: Text('Menu: todas las categorias'),
            ),
            ...categorias.map(
              (categoria) => DropdownMenuItem<String>(
                value: categoria,
                child: Text(categoria),
              ),
            ),
          ],
          onChanged: (value) {
            if (value == null) {
              return;
            }
            setState(() => _categoriaDropdownValue = value);
          },
        ),
      ),
    );
  }

  Widget _filterSection({
    required String title,
    required List<Widget> children,
  }) {
    return Container(
      width: double.infinity,
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: _card,
        borderRadius: BorderRadius.circular(22),
        border: Border.all(color: _line),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: TextStyle(
              color: _ink,
              fontSize: 13,
              fontWeight: FontWeight.w900,
            ),
          ),
          const SizedBox(height: 10),
          Wrap(spacing: 8, runSpacing: 8, children: children),
        ],
      ),
    );
  }

  Widget _filterChip({
    required String label,
    required IconData icon,
    required bool selected,
    required ValueChanged<bool> onSelected,
  }) {
    return FilterChip(
      selected: selected,
      onSelected: onSelected,
      showCheckmark: false,
      avatar: Icon(
        selected ? Icons.check_circle_rounded : icon,
        size: 18,
        color: selected ? _accent : _muted,
      ),
      label: Text(label),
      selectedColor: _accentSoft,
      backgroundColor: AppThemeColors.surfaceAlt,
      side: BorderSide(color: selected ? _accent : _line),
      labelStyle: TextStyle(
        color: selected ? _accent : _ink,
        fontWeight: FontWeight.w800,
      ),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
    );
  }

  Widget _emptyFilterState() {
    return Container(
      padding: const EdgeInsets.all(24),
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
            'No encontramos platos con ese filtro. Prueba otro nombre o cambia el orden.',
            textAlign: TextAlign.center,
            style: TextStyle(color: _muted, height: 1.5),
          ),
        ],
      ),
    );
  }

  Widget _cartActionButton(int totalItems) {
    return Stack(
      clipBehavior: Clip.none,
      children: [
        InkWell(
          onTap: _abrirCarrito,
          borderRadius: BorderRadius.circular(16),
          child: Container(
            width: 46,
            height: 46,
            decoration: BoxDecoration(
              color: _card,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: _line),
            ),
            child: Icon(Icons.shopping_bag_outlined, color: _ink),
          ),
        ),
        if (totalItems > 0)
          Positioned(
            right: -3,
            top: -5,
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
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

  Widget _statusChip(
    String label,
    IconData icon,
    Color foreground,
    Color background,
  ) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 7),
      decoration: BoxDecoration(
        color: background,
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 16, color: foreground),
          const SizedBox(width: 6),
          Text(
            label,
            style: TextStyle(
              color: foreground,
              fontSize: 12,
              fontWeight: FontWeight.w800,
            ),
          ),
        ],
      ),
    );
  }

  Widget _platoCard(Producto producto) {
    final disponible = producto.disponible;

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: _card,
        borderRadius: BorderRadius.circular(26),
        border: Border.all(color: _line),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.03),
            blurRadius: 12,
            offset: const Offset(0, 6),
          ),
        ],
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
                      producto.nombre,
                      style: TextStyle(
                        color: _ink,
                        fontSize: 19,
                        fontWeight: FontWeight.w800,
                        height: 1.15,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      producto.descripcion.isEmpty
                          ? 'Seleccion de carta disponible para ordenar.'
                          : producto.descripcion,
                      style: TextStyle(
                        color: _muted,
                        fontSize: 14,
                        height: 1.45,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 16),
              Text(
                '\$${producto.precio.toStringAsFixed(0)}',
                style: TextStyle(
                  color: _ink,
                  fontSize: 18,
                  fontWeight: FontWeight.w900,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              _statusChip(
                disponible ? 'Disponible' : 'No disponible',
                disponible
                    ? Icons.check_circle_rounded
                    : Icons.do_not_disturb_on_rounded,
                disponible ? const Color(0xFF2F6E39) : _muted,
                disponible ? const Color(0xFFE8F3EA) : const Color(0xFFF2F1F4),
              ),
              if (producto.nombreCategoria.isNotEmpty)
                _statusChip(
                  producto.nombreCategoria,
                  Icons.restaurant_menu_rounded,
                  _accent,
                  _accentSoft,
                ),
            ],
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
                    onPressed: disponible
                        ? () => _agregarAlCarrito(producto)
                        : null,
                    style: ElevatedButton.styleFrom(
                      elevation: 0,
                      backgroundColor: _accent,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(horizontal: 18),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(18),
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
        color: const Color(0xFFF7F7FB),
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
                color: const Color(0xFF181818),
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
}

enum _OrdenPlatos {
  relevancia('Mas pedidos primero'),
  precioMenor('Precio menor'),
  precioMayor('Precio mayor'),
  nombre('Nombre A-Z');

  const _OrdenPlatos(this.label);
  final String label;
}

enum _RangoPrecioFiltro {
  economico('Hasta \$20k', null, 20000),
  medio('\$20k - \$40k', 20000, 40000),
  alto('Mas de \$40k', 40000, null);

  const _RangoPrecioFiltro(this.label, this.min, this.max);
  final String label;
  final double? min;
  final double? max;

  bool matches(Producto producto) {
    final precio = producto.precio;
    final aboveMin = min == null || precio >= min!;
    final belowMax = max == null || precio <= max!;
    return aboveMin && belowMax;
  }
}
