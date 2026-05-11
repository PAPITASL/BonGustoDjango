// Pantalla del mapa para ubicar el restaurante y guiar al cliente.
import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:geolocator/geolocator.dart';
import 'package:latlong2/latlong.dart';
import 'package:url_launcher/url_launcher.dart';

import '../language_controller.dart';
import 'app_settings_controls.dart';
import 'home_screen.dart';
import 'pedidos_screen.dart';
import 'perfil_screen.dart';
import 'menu_screen.dart';
import 'qr_screen.dart';
import '../services/session_service.dart';

// Widget principal del modulo de mapa.
class MapScreen extends StatefulWidget {
  const MapScreen({super.key});

  @override
  State<MapScreen> createState() => _MapScreenState();
}

// Estado que maneja geolocalizacion, marcadores y acciones del mapa.
class _MapScreenState extends State<MapScreen> {
  static const Color _brandRed = Color(0xFFB2281D);
  static const Color _restaurantGold = Color(0xFFE7A12A);
  static const Color _restaurantOrange = Color(0xFFC64D2D);
  static const Color _userBlue = Color(0xFF2A6CF6);
  static const Color _userSky = Color(0xFF68A4F7);
  static const Color _ink = Color(0xFF181818);
  static const LatLng _restaurantLocation = LatLng(4.6563845, -74.0598855);
  static const String _restaurantName = 'Santa Juana Gastrobar';
  static const String _restaurantAddress = 'Cl. 71 #11-51, Bogota';

  final MapController _mapController = MapController();
  StreamSubscription<Position>? _positionSubscription;

  LatLng? _userLocation;
  int _currentIndex = 2;

  @override
  void initState() {
    super.initState();
    _getUserLocation();
  }

  @override
  void dispose() {
    _positionSubscription?.cancel();
    super.dispose();
  }

  Future<void> _getUserLocation() async {
    final serviceEnabled = await Geolocator.isLocationServiceEnabled();
    if (!serviceEnabled) return;

    LocationPermission permission = await Geolocator.checkPermission();
    if (permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission();
      if (permission == LocationPermission.denied) return;
    }

    if (permission == LocationPermission.deniedForever) return;

    final position = await Geolocator.getCurrentPosition();
    final currentLocation = LatLng(position.latitude, position.longitude);

    if (!mounted) return;
    setState(() => _userLocation = currentLocation);

    _positionSubscription = Geolocator.getPositionStream().listen((pos) {
      if (!mounted) return;
      setState(() {
        _userLocation = LatLng(pos.latitude, pos.longitude);
      });
    });
  }

  Future<void> _openWhatsApp() async {
    const numero = '573001112233';
    const mensaje = 'Hola, quiero hacer una reserva en Santa Juana Gastrobar.';
    final url = Uri.parse(
      'https://wa.me/$numero?text=${Uri.encodeComponent(mensaje)}',
    );

    if (await canLaunchUrl(url)) {
      await launchUrl(url, mode: LaunchMode.externalApplication);
    }
  }

  void _showRestaurantOptions() {
    showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) {
        final theme = Theme.of(context);
        final surface = theme.colorScheme.surface;
        final text = theme.colorScheme.onSurface;
        final muted = text.withValues(alpha: 0.62);

        return SafeArea(
          top: false,
          child: Container(
            margin: const EdgeInsets.all(12),
            padding: const EdgeInsets.fromLTRB(18, 10, 18, 18),
            decoration: BoxDecoration(
              color: surface,
              borderRadius: BorderRadius.circular(24),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withValues(alpha: 0.18),
                  blurRadius: 24,
                  offset: const Offset(0, 12),
                ),
              ],
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Center(
                  child: Container(
                    width: 42,
                    height: 5,
                    margin: const EdgeInsets.only(bottom: 16),
                    decoration: BoxDecoration(
                      color: muted.withValues(alpha: 0.32),
                      borderRadius: BorderRadius.circular(8),
                    ),
                  ),
                ),
                Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Container(
                      width: 52,
                      height: 52,
                      decoration: BoxDecoration(
                        color: const Color(0xFFFFECEE),
                        borderRadius: BorderRadius.circular(16),
                      ),
                      child: const Icon(
                        Icons.restaurant_rounded,
                        color: _brandRed,
                        size: 26,
                      ),
                    ),
                    const SizedBox(width: 14),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            _restaurantName,
                            style: TextStyle(
                              color: text,
                              fontSize: 22,
                              height: 1.05,
                              fontWeight: FontWeight.w900,
                            ),
                          ),
                          const SizedBox(height: 7),
                          Text(
                            _restaurantAddress,
                            style: TextStyle(
                              color: muted,
                              fontSize: 14,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: const [
                    _InfoPill(
                      icon: Icons.schedule_rounded,
                      label: '12 PM - 11 PM',
                    ),
                    _InfoPill(icon: Icons.place_outlined, label: 'Calle 71'),
                    _InfoPill(
                      icon: Icons.touch_app_rounded,
                      label: 'Toca una opcion',
                    ),
                  ],
                ),
                const SizedBox(height: 18),
                _SheetAction(
                  icon: Icons.qr_code_rounded,
                  title: 'Entrar al restaurante',
                  subtitle: 'Abrir acceso QR y experiencia en mesa.',
                  color: _brandRed,
                  onTap: () {
                    Navigator.pop(context);
                    Navigator.push(
                      context,
                      MaterialPageRoute(builder: (_) => const QRScreen()),
                    );
                  },
                ),
                const SizedBox(height: 10),
                _SheetAction(
                  icon: Icons.shopping_bag_outlined,
                  title: 'Pedir para llevar',
                  subtitle: 'Ver carta y armar tu pedido.',
                  color: _restaurantOrange,
                  onTap: () {
                    unawaited(SessionService.actualizarSesion({
                      'tipo_pedido': 'para_llevar',
                      'mesa_id': null,
                      'mesa_numero': null,
                      'mesa_label': '',
                      'mesa_estado': '',
                    }));
                    Navigator.pop(context);
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (_) => const MenuScreen(),
                      ),
                    );
                  },
                ),
                const SizedBox(height: 10),
                _SheetAction(
                  icon: Icons.chat_bubble_outline_rounded,
                  title: 'Reservar por WhatsApp',
                  subtitle: 'Hablar directo con Santa Juana.',
                  color: const Color(0xFF2F8F46),
                  onTap: () async {
                    Navigator.pop(context);
                    await _openWhatsApp();
                  },
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  void _onTabTapped(int i) {
    if (i == _currentIndex) return;
    setState(() => _currentIndex = i);

    if (i == 0) {
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (_) => const HomeScreen()),
      );
    } else if (i == 1) {
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (_) => const PedidosScreen()),
      );
    } else if (i == 3) {
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (_) => const PerfilScreen()),
      );
    }
  }

  Widget _restaurantMarker() {
    return GestureDetector(
      onTap: _showRestaurantOptions,
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: const Color(0xFFE5D4C8)),
              boxShadow: const [
                BoxShadow(
                  color: Color(0x26000000),
                  blurRadius: 10,
                  offset: Offset(0, 4),
                ),
              ],
            ),
            child: const Text(
              'Santa Juana',
              style: TextStyle(
                color: _ink,
                fontSize: 11,
                fontWeight: FontWeight.w800,
              ),
            ),
          ),
          const SizedBox(height: 5),
          Stack(
            alignment: Alignment.center,
            clipBehavior: Clip.none,
            children: [
              Container(
                width: 50,
                height: 50,
                decoration: const BoxDecoration(
                  shape: BoxShape.circle,
                  color: Color(0x22C64D2D),
                ),
              ),
              Container(
                width: 40,
                height: 40,
                decoration: BoxDecoration(
                  gradient: const LinearGradient(
                    colors: [_restaurantGold, _restaurantOrange],
                    begin: Alignment.topCenter,
                    end: Alignment.bottomCenter,
                  ),
                  shape: BoxShape.circle,
                  border: Border.all(color: Colors.white, width: 4),
                  boxShadow: const [
                    BoxShadow(
                      color: Color(0x33000000),
                      blurRadius: 10,
                      offset: Offset(0, 4),
                    ),
                  ],
                ),
                child: const Icon(
                  Icons.restaurant_rounded,
                  color: Colors.white,
                  size: 21,
                ),
              ),
              const Positioned(
                bottom: -12,
                child: Icon(
                  Icons.navigation_rounded,
                  color: _restaurantOrange,
                  size: 20,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _userMarker() {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 9, vertical: 5),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(8),
            border: Border.all(color: const Color(0xFFCEDCFF)),
            boxShadow: const [
              BoxShadow(
                color: Color(0x20000000),
                blurRadius: 10,
                offset: Offset(0, 4),
              ),
            ],
          ),
          child: const Text(
            'Tu ubicacion',
            style: TextStyle(
              color: _userBlue,
              fontSize: 10,
              fontWeight: FontWeight.w800,
            ),
          ),
        ),
        const SizedBox(height: 5),
        Stack(
          alignment: Alignment.center,
          clipBehavior: Clip.none,
          children: [
            Container(
              width: 48,
              height: 48,
              decoration: const BoxDecoration(
                shape: BoxShape.circle,
                color: Color(0x1F2A6CF6),
              ),
            ),
            Container(
              width: 36,
              height: 36,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                gradient: const LinearGradient(
                  colors: [_userSky, _userBlue],
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                ),
                border: Border.all(color: Colors.white, width: 3),
                boxShadow: const [
                  BoxShadow(
                    color: Color(0x26000000),
                    blurRadius: 10,
                    offset: Offset(0, 4),
                  ),
                ],
              ),
              child: const Icon(
                Icons.person_pin_circle_rounded,
                color: Colors.white,
                size: 22,
              ),
            ),
            const Positioned(
              bottom: -11,
              child: Icon(Icons.near_me_rounded, color: _userBlue, size: 19),
            ),
          ],
        ),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      backgroundColor: theme.scaffoldBackgroundColor,
      appBar: AppBar(
        title: const Text(
          _restaurantName,
          style: TextStyle(fontWeight: FontWeight.w900),
        ),
        backgroundColor: theme.scaffoldBackgroundColor,
        foregroundColor: theme.colorScheme.onSurface,
        actions: const [
          Padding(
            padding: EdgeInsets.only(right: 12),
            child: AppSettingsControls(),
          ),
        ],
      ),
      body: FlutterMap(
        mapController: _mapController,
        options: const MapOptions(
          initialCenter: _restaurantLocation,
          initialZoom: 16,
        ),
        children: [
          TileLayer(
            urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
            userAgentPackageName: 'com.example.bongustoap',
          ),
          MarkerLayer(
            markers: [
              Marker(
                width: 108,
                height: 96,
                point: _restaurantLocation,
                child: _restaurantMarker(),
              ),
              if (_userLocation != null)
                Marker(
                  width: 104,
                  height: 92,
                  point: _userLocation!,
                  child: _userMarker(),
                ),
            ],
          ),
        ],
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: _onTabTapped,
        type: BottomNavigationBarType.fixed,
        backgroundColor: theme.colorScheme.surface,
        selectedItemColor: _brandRed,
        unselectedItemColor: theme.colorScheme.onSurface.withValues(
          alpha: 0.58,
        ),
        items: [
          BottomNavigationBarItem(
            icon: const Icon(Icons.home_outlined),
            label: LanguageController.tr('Inicio'),
          ),
          BottomNavigationBarItem(
            icon: const Icon(Icons.list_alt_outlined),
            label: LanguageController.tr('Pedidos'),
          ),
          BottomNavigationBarItem(
            icon: const Icon(Icons.map_outlined),
            label: LanguageController.tr('Mapa'),
          ),
          BottomNavigationBarItem(
            icon: const Icon(Icons.person_outline),
            label: LanguageController.tr('Perfil'),
          ),
        ],
      ),
    );
  }
}

class _InfoPill extends StatelessWidget {
  const _InfoPill({required this.icon, required this.label});

  final IconData icon;
  final String label;

  @override
  Widget build(BuildContext context) {
    final text = Theme.of(context).colorScheme.onSurface;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
      decoration: BoxDecoration(
        color: text.withValues(alpha: 0.06),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, color: text.withValues(alpha: 0.72), size: 16),
          const SizedBox(width: 6),
          Text(
            label,
            style: TextStyle(
              color: text.withValues(alpha: 0.72),
              fontSize: 12,
              fontWeight: FontWeight.w800,
            ),
          ),
        ],
      ),
    );
  }
}

class _SheetAction extends StatelessWidget {
  const _SheetAction({
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.color,
    required this.onTap,
  });

  final IconData icon;
  final String title;
  final String subtitle;
  final Color color;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final text = Theme.of(context).colorScheme.onSurface;
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(16),
        child: Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: text.withValues(alpha: 0.08)),
          ),
          child: Row(
            children: [
              Container(
                width: 42,
                height: 42,
                decoration: BoxDecoration(
                  color: color.withValues(alpha: 0.12),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Icon(icon, color: color, size: 22),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      style: TextStyle(
                        color: text,
                        fontSize: 15,
                        fontWeight: FontWeight.w900,
                      ),
                    ),
                    const SizedBox(height: 3),
                    Text(
                      subtitle,
                      style: TextStyle(
                        color: text.withValues(alpha: 0.58),
                        fontSize: 12,
                        height: 1.25,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ],
                ),
              ),
              Icon(
                Icons.chevron_right_rounded,
                color: text.withValues(alpha: 0.46),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
