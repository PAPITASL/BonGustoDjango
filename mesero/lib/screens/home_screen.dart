// ===== Pantalla `home_screen.dart` | Funciona como panel principal del turno y agrupa los accesos rapidos del mesero. =====
import 'package:flutter/material.dart';

import '../services/session_service.dart';

// ===== Clase `HomeScreen` | Expone la vista inicial despues de autenticarse. =====
class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

// ===== Modelo `_HomeCard` | Define la informacion que usa cada tarjeta del panel principal. =====
class _HomeCard {
  final String title;
  final String subtitle;
  final IconData icon;
  final String route;
  final Color tint;

  const _HomeCard({
    required this.title,
    required this.subtitle,
    required this.icon,
    required this.route,
    required this.tint,
  });
}

// ===== Estado `_HomeScreenState` | Organiza el dashboard de accesos y su estilo local. =====
class _HomeScreenState extends State<HomeScreen> {
  static const _bg = Color(0xFFF2F1F4);
  static const _card = Color(0xFFFFFFFF);
  static const _ink = Color(0xFF181818);
  static const _muted = Color(0xFF73727A);
  static const _accent = Color(0xFFD90416);
  static const _line = Color(0xFFE8E6EB);

  int _currentIndex = 0;

  late final List<_HomeCard> _cards = [
    const _HomeCard(
      title: 'Pedidos',
      subtitle: 'Pedidos creados por clientes.',
      icon: Icons.receipt_long_outlined,
      route: '/pedidos',
      tint: Color(0xFFFFECEE),
    ),
    const _HomeCard(
      title: 'Llamados',
      subtitle: 'Clientes que pidieron mesero desde la app.',
      icon: Icons.notifications_active_outlined,
      route: '/notificaciones',
      tint: Color(0xFFFFF4EA),
    ),
    const _HomeCard(
      title: 'Chat',
      subtitle: 'Aqui puedes hablar con el administrador.',
      icon: Icons.chat_bubble_outline_rounded,
      route: '/interaccion',
      tint: Color(0xFFEFF6FF),
    ),
    const _HomeCard(
      title: 'Menu',
      subtitle: 'Vista del menu y precios.',
      icon: Icons.menu_book_outlined,
      route: '/menu',
      tint: Color(0xFFF5F2FF),
    ),
    const _HomeCard(
      title: 'Musica',
      subtitle: 'Cola actual de solicitudes musicales de clientes.',
      icon: Icons.queue_music_rounded,
      route: '/musica',
      tint: Color(0xFFFFF6EC),
    ),
    const _HomeCard(
      title: 'Mesas',
      subtitle: 'Mesas con cliente y productos asignados por pedido.',
      icon: Icons.table_restaurant_outlined,
      route: '/mesas',
      tint: Color(0xFFEFF4F1),
    ),
  ];

  Widget _homeCard(_HomeCard card) {
    return InkWell(
      onTap: () => Navigator.pushNamed(context, card.route),
      borderRadius: BorderRadius.circular(28),
      child: Container(
        padding: const EdgeInsets.all(18),
        decoration: BoxDecoration(
          color: _card,
          borderRadius: BorderRadius.circular(28),
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
            Container(
              width: 62,
              height: 62,
              decoration: BoxDecoration(
                color: card.tint,
                borderRadius: BorderRadius.circular(20),
              ),
              child: Icon(card.icon, color: _accent, size: 30),
            ),
            const Spacer(),
            Text(
              card.title,
              style: const TextStyle(
                color: _ink,
                fontSize: 22,
                height: 1.05,
                fontWeight: FontWeight.w900,
              ),
            ),
            const SizedBox(height: 10),
            Text(
              card.subtitle,
              maxLines: 4,
              overflow: TextOverflow.fade,
              style: const TextStyle(
                color: _muted,
                fontSize: 13,
                height: 1.45,
              ),
            ),
            const SizedBox(height: 14),
            const Row(
              children: [
                Text(
                  'Abrir',
                  style: TextStyle(
                    color: _ink,
                    fontSize: 15,
                    fontWeight: FontWeight.w800,
                  ),
                ),
                SizedBox(width: 6),
                Icon(Icons.arrow_forward_rounded, size: 18, color: _ink),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _hero(String nombre) {
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
                child: const Icon(
                  Icons.room_service_rounded,
                  color: Colors.white,
                  size: 28,
                ),
              ),
              const SizedBox(width: 14),
              const Expanded(
                child: Text(
                  'OPERACION MESEROS',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 11,
                    letterSpacing: 2.8,
                    fontWeight: FontWeight.w800,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 22),
          const Text(
            'Todo el piso en un solo panel.',
            style: TextStyle(
              color: Colors.white,
              fontSize: 30,
              height: 1.06,
              fontWeight: FontWeight.w900,
            ),
          ),
          const SizedBox(height: 10),
          Text(
            'Bienvenido, $nombre. Desde aqui revisas pedidos, llamados, mesas, menu, cola musical y chat.',
            style: TextStyle(
              color: Colors.white.withValues(alpha: 0.86),
              fontSize: 14,
              height: 1.5,
            ),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final nombre = SessionService.nombreCompleto.trim().isEmpty
        ? 'Mesero'
        : SessionService.nombreCompleto.trim();

    return Scaffold(
      backgroundColor: _bg,
      appBar: AppBar(
        backgroundColor: _bg,
        foregroundColor: _ink,
        automaticallyImplyLeading: false,
        title: const Text(
          'Inicio',
          style: TextStyle(fontWeight: FontWeight.w800),
        ),
      ),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.fromLTRB(20, 10, 20, 100),
          children: [
            _hero(nombre),
            const SizedBox(height: 18),
            const Text(
              'Accesos del turno',
              style: TextStyle(
                color: _ink,
                fontSize: 22,
                fontWeight: FontWeight.w900,
              ),
            ),
            const SizedBox(height: 8),
            const SizedBox(height: 16),
            GridView.builder(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              itemCount: _cards.length,
              gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: 2,
                crossAxisSpacing: 14,
                mainAxisSpacing: 14,
                mainAxisExtent: 230,
              ),
              itemBuilder: (_, i) => _homeCard(_cards[i]),
            ),
          ],
        ),
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (i) {
          setState(() => _currentIndex = i);
          if (i == 1) {
            Navigator.pushNamed(context, '/perfil');
          }
        },
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.home_outlined),
            label: 'Inicio',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.person_outline),
            label: 'Perfil',
          ),
        ],
      ),
    );
  }
}
