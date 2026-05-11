// Pantalla que lista el historial de pedidos del cliente autenticado.
import 'dart:async';

import 'package:flutter/material.dart';

import '../app_theme.dart';
import '../language_controller.dart';
import '../services/bongusto_api.dart';
import '../services/session_service.dart';
import 'app_settings_controls.dart';
import 'home_screen.dart';
import 'mapa_screen.dart';
import 'pedido_detalle_screen.dart';
import 'pedido_global.dart';
import 'perfil_screen.dart';

// Widget principal del modulo de pedidos.
class PedidosScreen extends StatefulWidget {
  const PedidosScreen({super.key});

  @override
  State<PedidosScreen> createState() => _PedidosScreenState();
}

// Estado que consulta pedidos, refresca la lista y abre el detalle.
class _PedidosScreenState extends State<PedidosScreen> {
  static Color get _card => AppThemeColors.surface;
  static Color get _ink => AppThemeColors.text;
  static Color get _muted => AppThemeColors.muted;
  static const _accent = Color(0xFFD90416);
  static Color get _line => AppThemeColors.line;
  bool _isDark(BuildContext context) =>
      Theme.of(context).brightness == Brightness.dark;

  bool _loading = true;
  String? _error;
  List<Pedido> _pedidos = [];
  int _currentIndex = 1;
  Timer? _refreshTimer;

  @override
  void initState() {
    super.initState();
    _cargarPedidos();
    _refreshTimer = Timer.periodic(const Duration(seconds: 5), (_) {
      _cargarPedidos(silent: true);
    });
  }

  @override
  void dispose() {
    _refreshTimer?.cancel();
    super.dispose();
  }

  Future<void> _cargarPedidos({bool silent = false}) async {
    final idUsuario = SessionService.idUsuario;
    if (idUsuario == null) {
      setState(() {
        _loading = false;
        _error = 'Debes iniciar sesion para ver tus pedidos';
      });
      return;
    }

    if (!silent) {
      setState(() {
        _loading = true;
        _error = null;
      });
    }

    try {
      final response = await BongustoApi.obtenerPedidosUsuario(idUsuario);
      if (!mounted) {
        return;
      }
      setState(() {
        _pedidos = response.map(Pedido.fromApi).toList();
        _loading = false;
        _error = null;
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

  void _abrirSeccion(int index) {
    if (index == _currentIndex) {
      return;
    }

    setState(() => _currentIndex = index);
    if (index == 0) {
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (_) => const HomeScreen()),
      );
    } else if (index == 2) {
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (_) => const MapScreen()),
      );
    } else if (index == 3) {
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (_) => const PerfilScreen()),
      );
    }
  }

  void _abrirDetallePedido(Pedido pedido) {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (_) => PedidoDetalleScreen(pedido: pedido)),
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      backgroundColor: theme.scaffoldBackgroundColor,
      appBar: AppBar(
        backgroundColor: theme.scaffoldBackgroundColor,
        foregroundColor: theme.colorScheme.onSurface,
        elevation: 0,
        scrolledUnderElevation: 0,
        title: Text(
          LanguageController.tr('Mis pedidos'),
          style: TextStyle(
            fontWeight: FontWeight.w900,
            fontSize: 28,
            letterSpacing: -0.2,
          ),
        ),
        actions: [
          Padding(
            padding: EdgeInsets.only(right: 12),
            child: AppSettingsControls(),
          ),
        ],
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: _abrirSeccion,
        type: BottomNavigationBarType.fixed,
        backgroundColor: theme.colorScheme.surface,
        selectedItemColor: _accent,
        unselectedItemColor: theme.colorScheme.onSurface.withValues(
          alpha: 0.58,
        ),
        showUnselectedLabels: true,
        items: [
          BottomNavigationBarItem(
            icon: Icon(Icons.home_outlined),
            label: LanguageController.tr('Inicio'),
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.list_alt_outlined),
            label: LanguageController.tr('Pedidos'),
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.map_outlined),
            label: LanguageController.tr('Mapa'),
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.person_outline),
            label: LanguageController.tr('Perfil'),
          ),
        ],
      ),
      body: RefreshIndicator(
        color: _accent,
        onRefresh: _cargarPedidos,
        child: _loading
            ? Center(child: CircularProgressIndicator())
            : _error != null
            ? ListView(
                padding: const EdgeInsets.all(20),
                children: [
                  _infoCard(
                    icon: Icons.cloud_off_outlined,
                    title: 'No pudimos cargar tus pedidos',
                    message: _error!,
                  ),
                ],
              )
            : _pedidos.isEmpty
            ? ListView(
                padding: const EdgeInsets.all(20),
                children: [_EmptyOrdersCard()],
              )
            : ListView.builder(
                padding: const EdgeInsets.fromLTRB(20, 8, 20, 100),
                itemCount: _pedidos.length,
                itemBuilder: (context, index) {
                  final pedido = _pedidos[index];
                  return _pedidoCard(pedido);
                },
              ),
      ),
    );
  }

  Widget _pedidoCard(Pedido pedido) {
    final totalCantidad = pedido.productos.fold<int>(
      0,
      (sum, item) => sum + item.cantidad,
    );
    final productosPreview = pedido.productos
        .take(3)
        .map((item) => item.nombre)
        .join(' | ');
    return GestureDetector(
      onTap: () => _abrirDetallePedido(pedido),
      child: Container(
        margin: const EdgeInsets.only(bottom: 14),
        padding: const EdgeInsets.all(18),
        decoration: BoxDecoration(
          color: _card,
          borderRadius: BorderRadius.circular(26),
          border: Border.all(color: _line),
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
            Row(
              children: [
                Container(
                  width: 52,
                  height: 52,
                  decoration: BoxDecoration(
                    color: const Color(0xFFFFECEE),
                    borderRadius: BorderRadius.circular(18),
                  ),
                  child: Icon(
                    Icons.receipt_long_rounded,
                    color: _accent,
                    size: 28,
                  ),
                ),
                const SizedBox(width: 14),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Pedido #${pedido.id}',
                        style: TextStyle(
                          color: _ink,
                          fontSize: 20,
                          fontWeight: FontWeight.w900,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        pedido.fechaPedido,
                        style: TextStyle(
                          color: _muted,
                          fontSize: 13,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      if (pedido.mesaLabel.isNotEmpty) ...[
                        const SizedBox(height: 4),
                        Text(
                          pedido.mesaLabel,
                          style: TextStyle(
                            color: _accent,
                            fontSize: 13,
                            fontWeight: FontWeight.w700,
                          ),
                        ),
                      ],
                    ],
                  ),
                ),
                _statusPill(pedido.estado),
              ],
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: _detailBlock(
                    context,
                    label: 'Items',
                    value: '$totalCantidad',
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _detailBlock(
                    context,
                    label: 'Total',
                    value: '\$${pedido.total.toStringAsFixed(0)}',
                  ),
                ),
              ],
            ),
            if (productosPreview.isNotEmpty) ...[
              const SizedBox(height: 14),
              Text(
                productosPreview,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
                style: TextStyle(
                  color: _muted,
                  height: 1.4,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
            const SizedBox(height: 10),
            Row(
              children: [
                Text(
                  'Toca para ver detalles',
                  style: TextStyle(color: _accent, fontWeight: FontWeight.w800),
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

  Widget _detailBlock(
    BuildContext context, {
    required String label,
    required String value,
  }) {
    final dark = _isDark(context);
    final blockColor = dark ? const Color(0xFF232737) : const Color(0xFFF4F4F7);
    final labelColor = dark ? const Color(0xFFC8CEDB) : const Color(0xFF62636D);
    final valueColor = dark ? const Color(0xFFF4F5F9) : const Color(0xFF111217);

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 14),
      decoration: BoxDecoration(
        color: blockColor,
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: _line),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            label,
            style: TextStyle(
              color: labelColor,
              fontSize: 12,
              letterSpacing: 1.2,
              fontWeight: FontWeight.w700,
            ),
          ),
          const SizedBox(height: 6),
          Text(
            value,
            style: TextStyle(
              color: valueColor,
              fontSize: 18,
              fontWeight: FontWeight.w900,
            ),
          ),
        ],
      ),
    );
  }

  Widget _statusPill(String estado) {
    final dark = _isDark(context);
    final status = estado.toLowerCase();
    final isActive =
        status.contains('activo') ||
        status.contains('pend') ||
        status.contains('prepar');
    final inactiveBg = dark ? const Color(0xFF232737) : const Color(0xFFF2F2F5);
    final inactiveText = dark ? const Color(0xFFE3E7F2) : const Color(0xFF3A3B41);
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: isActive ? AppThemeColors.successSoft : inactiveBg,
        borderRadius: BorderRadius.circular(999),
        border: Border.all(color: _line),
      ),
      child: Text(
        estado,
        style: TextStyle(
          color: isActive ? AppThemeColors.success : inactiveText,
          fontWeight: FontWeight.w800,
        ),
      ),
    );
  }

  Widget _infoCard({
    required IconData icon,
    required String title,
    required String message,
  }) {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: _card,
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: _line),
      ),
      child: Column(
        children: [
          Icon(icon, color: _accent, size: 34),
          const SizedBox(height: 14),
          Text(
            title,
            textAlign: TextAlign.center,
            style: TextStyle(
              color: _ink,
              fontSize: 20,
              fontWeight: FontWeight.w900,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            message,
            textAlign: TextAlign.center,
            style: TextStyle(color: _muted, height: 1.5),
          ),
        ],
      ),
    );
  }
}

class _EmptyOrdersCard extends StatelessWidget {
  const _EmptyOrdersCard();

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: AppThemeColors.surface,
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: AppThemeColors.line),
      ),
      child: Column(
        children: [
          Icon(
            Icons.shopping_bag_outlined,
            color: AppThemeColors.accent,
            size: 34,
          ),
          SizedBox(height: 14),
          Text(
            'Aun no tienes pedidos',
            textAlign: TextAlign.center,
            style: TextStyle(
              color: AppThemeColors.text,
              fontSize: 20,
              fontWeight: FontWeight.w900,
            ),
          ),
          SizedBox(height: 8),
          Text(
            'Cuando hagas tu primer pedido en Santa Juana, aparecera aqui con su estado y total.',
            textAlign: TextAlign.center,
            style: TextStyle(color: AppThemeColors.muted, height: 1.5),
          ),
        ],
      ),
    );
  }
}
