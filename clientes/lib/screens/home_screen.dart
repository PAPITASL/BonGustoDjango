// Pantalla principal del cliente con accesos rapidos al resto de modulos.
import 'dart:async';

import 'package:flutter/material.dart';

import '../app_theme.dart';
import '../language_controller.dart';
import '../services/bongusto_api.dart';
import '../services/session_service.dart';
import 'app_settings_controls.dart';
import 'mapa_screen.dart';
import 'notificaciones_screen.dart';
import 'pedidos_screen.dart';
import 'perfil_screen.dart';
import 'producto_global.dart';
import 'menu_screen.dart';
import 'qr_screen.dart';

// Widget principal del inicio de la app cliente.
class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

// Estado que carga datos destacados y maneja la navegacion base.
class _HomeScreenState extends State<HomeScreen> {
  static Color get _card => AppThemeColors.surface;
  static Color get _ink => AppThemeColors.text;
  static Color get _muted => AppThemeColors.muted;
  static const _accent = Color(0xFFD90416);
  static Color get _accentSoft => AppThemeColors.accentSoft;
  static Color get _line => AppThemeColors.line;

  int _currentIndex = 0;
  bool _loading = true;
  String? _error;
  List<Producto> _destacados = [];
  int _notificacionesPendientes = 0;

  @override
  void initState() {
    super.initState();
    _cargarHome();
  }

  Future<void> _cargarHome() async {
    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      final results = await Future.wait([
        BongustoApi.obtenerProductos(destacados: true),
        BongustoApi.obtenerNotificaciones(),
      ]);
      final response = List<Map<String, dynamic>>.from(results[0] as List);
      final notificaciones = Map<String, dynamic>.from(results[1] as Map);

      if (!mounted) {
        return;
      }

      setState(() {
        _destacados = response.map(Producto.fromApi).toList();
        _notificacionesPendientes =
            (notificaciones['no_leidas'] as num?)?.toInt() ?? 0;
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

  void _abrirSeccion(int index) {
    setState(() => _currentIndex = index);
    if (index == 0) {
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

  void _abrirRestaurante() {
    unawaited(SessionService.actualizarSesion({
      'tipo_pedido': 'restaurante',
    }));
    Navigator.push(
      context,
      MaterialPageRoute(builder: (_) => const QRScreen()),
    );
  }

  void _abrirPedidoParaLlevar() {
    unawaited(SessionService.actualizarSesion({
      'tipo_pedido': 'para_llevar',
      'mesa_id': null,
      'mesa_numero': null,
      'mesa_label': '',
      'mesa_estado': '',
    }));
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => const MenuScreen(),
      ),
    );
  }

  Future<void> _abrirNotificaciones() async {
    await Navigator.push(
      context,
      MaterialPageRoute(builder: (_) => const NotificacionesScreen()),
    );
    if (!mounted) {
      return;
    }
    _cargarHome();
  }

  Widget _bottomBar(BuildContext context) {
    final theme = Theme.of(context);

    return BottomNavigationBar(
      currentIndex: _currentIndex,
      onTap: _abrirSeccion,
      type: BottomNavigationBarType.fixed,
      backgroundColor: theme.colorScheme.surface,
      selectedItemColor: _accent,
      unselectedItemColor: theme.colorScheme.onSurface.withValues(alpha: 0.58),
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
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      backgroundColor: theme.scaffoldBackgroundColor,
      bottomNavigationBar: _bottomBar(context),
      body: SafeArea(
        child: RefreshIndicator(
          color: _accent,
          onRefresh: _cargarHome,
          child: ListView(
            padding: const EdgeInsets.fromLTRB(20, 16, 20, 100),
            children: [
              const Align(
                alignment: Alignment.centerRight,
                child: AppSettingsControls(),
              ),
              const SizedBox(height: 12),
              _heroSantaJuana(),
              const SizedBox(height: 18),
              if (_loading)
                Padding(
                  padding: EdgeInsets.all(32),
                  child: Center(child: CircularProgressIndicator()),
                )
              else if (_error != null)
                _errorState()
              else ...[
                _sectionHeader(
                  eyebrow: LanguageController.tr('EXPERIENCIA DESTACADA'),
                  title: LanguageController.tr('Platos listos para pedir'),
                  subtitle: '',
                ),
                const SizedBox(height: 14),
                _destacadosSection(),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _heroSantaJuana() {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(34),
        gradient: const LinearGradient(
          colors: [Color(0xFF8E1D16), Color(0xFFD90416)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.12),
            blurRadius: 24,
            offset: const Offset(0, 14),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                width: 56,
                height: 56,
                decoration: BoxDecoration(
                  color: Colors.white.withValues(alpha: 0.14),
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(
                    color: Colors.white.withValues(alpha: 0.18),
                  ),
                ),
                child: Icon(
                  Icons.restaurant_rounded,
                  color: Colors.white,
                  size: 28,
                ),
              ),
              const SizedBox(width: 14),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const SizedBox(height: 6),
                    Text(
                      'BonGusto',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 24,
                        fontWeight: FontWeight.w900,
                      ),
                    ),
                  ],
                ),
              ),
              Stack(
                clipBehavior: Clip.none,
                children: [
                  Material(
                    color: Colors.white.withValues(alpha: 0.16),
                    borderRadius: BorderRadius.circular(18),
                    child: InkWell(
                      borderRadius: BorderRadius.circular(18),
                      onTap: _abrirNotificaciones,
                      child: Padding(
                        padding: EdgeInsets.all(14),
                        child: Icon(
                          Icons.notifications_none_rounded,
                          color: Colors.white,
                          size: 24,
                        ),
                      ),
                    ),
                  ),
                  if (_notificacionesPendientes > 0)
                    Positioned(
                      right: -4,
                      top: -4,
                      child: Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 7,
                          vertical: 4,
                        ),
                        decoration: BoxDecoration(
                          color: const Color(0xFFFFD166),
                          borderRadius: BorderRadius.circular(999),
                        ),
                        child: Text(
                          '$_notificacionesPendientes',
                          style: TextStyle(
                            color: Color(0xFF181818),
                            fontSize: 11,
                            fontWeight: FontWeight.w900,
                          ),
                        ),
                      ),
                    ),
                ],
              ),
            ],
          ),
          const SizedBox(height: 24),
          const SizedBox(height: 12),
          Text(
            LanguageController.tr(
              'Desde aqui entras al restaurante o haces un pedido para llevar.',
            ),
            style: TextStyle(
              color: Color(0xFFFCECEC),
              fontSize: 14,
              height: 1.55,
            ),
          ),
          const SizedBox(height: 22),
          Row(
            children: [
              Expanded(
                child: ElevatedButton(
                  onPressed: _abrirRestaurante,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.white,
                    foregroundColor: _accent,
                    elevation: 0,
                    minimumSize: const Size.fromHeight(60),
                    padding: const EdgeInsets.symmetric(
                      horizontal: 16,
                      vertical: 16,
                    ),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(18),
                    ),
                  ),
                  child: Text(
                    LanguageController.tr('Entrar al restaurante'),
                    textAlign: TextAlign.center,
                    style: TextStyle(height: 1.2, fontWeight: FontWeight.w800),
                  ),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: OutlinedButton(
                  onPressed: _abrirPedidoParaLlevar,
                  style: OutlinedButton.styleFrom(
                    foregroundColor: Colors.white,
                    side: BorderSide(color: Colors.white24),
                    minimumSize: const Size.fromHeight(60),
                    padding: const EdgeInsets.symmetric(
                      horizontal: 16,
                      vertical: 16,
                    ),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(18),
                    ),
                  ),
                  child: Text(
                    LanguageController.tr('Pedir para llevar'),
                    textAlign: TextAlign.center,
                    style: TextStyle(height: 1.2, fontWeight: FontWeight.w800),
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _sectionHeader({
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
            letterSpacing: 3,
            fontWeight: FontWeight.w800,
          ),
        ),
        const SizedBox(height: 6),
        Text(
          title,
          style: TextStyle(
            color: _ink,
            fontSize: 25,
            height: 1.1,
            fontWeight: FontWeight.w900,
          ),
        ),
        const SizedBox(height: 8),
        Text(
          subtitle,
          style: TextStyle(color: _muted, fontSize: 14, height: 1.5),
        ),
      ],
    );
  }

  Widget _destacadosSection() {
    if (_destacados.isEmpty) {
      return _emptyCard(
        icon: Icons.local_dining_outlined,
        text: LanguageController.tr(
          'Todavia no hay platos destacados para mostrar en Santa Juana.',
        ),
      );
    }

    return Column(children: _destacados.map(_featuredDishCard).toList());
  }

  Widget _featuredDishCard(Producto producto) {
    return Container(
      margin: const EdgeInsets.only(bottom: 14),
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: _card,
        borderRadius: BorderRadius.circular(26),
        border: Border.all(color: _line),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 64,
            height: 64,
            decoration: BoxDecoration(
              color: _accentSoft,
              borderRadius: BorderRadius.circular(20),
            ),
            child: Icon(Icons.restaurant_rounded, color: _accent, size: 30),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  LanguageController.tr(producto.nombre),
                  style: TextStyle(
                    color: _ink,
                    fontSize: 18,
                    fontWeight: FontWeight.w800,
                  ),
                ),
                const SizedBox(height: 6),
                Text(
                  producto.descripcion.isEmpty
                      ? LanguageController.tr(
                          'Disponible ahora en la carta de Santa Juana.',
                        )
                      : LanguageController.tr(producto.descripcion),
                  maxLines: 3,
                  overflow: TextOverflow.ellipsis,
                  style: TextStyle(color: _muted, fontSize: 13, height: 1.45),
                ),
                const SizedBox(height: 12),
                Row(
                  children: [
                    Text(
                      '\$${producto.precio.toStringAsFixed(0)}',
                      style: TextStyle(
                        color: _ink,
                        fontSize: 18,
                        fontWeight: FontWeight.w900,
                      ),
                    ),
                    const Spacer(),
                    TextButton(
                      onPressed: _abrirPedidoParaLlevar,
                      style: TextButton.styleFrom(
                        foregroundColor: _accent,
                        padding: const EdgeInsets.symmetric(
                          horizontal: 14,
                          vertical: 10,
                        ),
                      ),
                      child: Text(
                        LanguageController.tr('Pedir'),
                        style: TextStyle(fontWeight: FontWeight.w800),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _emptyCard({required IconData icon, required String text}) {
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

  Widget _errorState() {
    return Container(
      padding: const EdgeInsets.all(22),
      decoration: BoxDecoration(
        color: _card,
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: _line),
      ),
      child: Column(
        children: [
          Icon(Icons.cloud_off_outlined, color: _accent, size: 34),
          const SizedBox(height: 12),
          Text(
            '${LanguageController.t('No se pudo cargar la experiencia de BonGusto.', 'Could not load the BonGusto experience.')}\n$_error',
            textAlign: TextAlign.center,
            style: TextStyle(color: _muted, height: 1.5),
          ),
          const SizedBox(height: 12),
          ElevatedButton(
            onPressed: _cargarHome,
            child: Text(LanguageController.tr('Reintentar')),
          ),
        ],
      ),
    );
  }
}
