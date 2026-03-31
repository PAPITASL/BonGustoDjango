// ===== Pantalla `perfil_screen.dart` | Reune la informacion del mesero autenticado y acciones relacionadas con su cuenta. =====
import 'package:flutter/material.dart';

import '../services/session_service.dart';

// ===== Clase `PerfilScreen` | Muestra el resumen del perfil y accesos secundarios del usuario activo. =====
class PerfilScreen extends StatelessWidget {
  const PerfilScreen({super.key});

  static const _bg = Color(0xFFF2F1F4);
  static const _card = Color(0xFFFFFFFF);
  static const _ink = Color(0xFF181818);
  static const _muted = Color(0xFF73727A);
  static const _accent = Color(0xFFD90416);
  static const _line = Color(0xFFE8E6EB);

  @override
  Widget build(BuildContext context) {
    final nombre = SessionService.nombreCompleto.trim().isEmpty
        ? 'Mesero'
        : SessionService.nombreCompleto.trim();
    final correo = SessionService.correo.trim().isEmpty
        ? 'sin-correo@bongusto.com'
        : SessionService.correo.trim();

    return Scaffold(
      backgroundColor: _bg,
      appBar: AppBar(
        backgroundColor: _bg,
        foregroundColor: _ink,
        title: const Text('Perfil', style: TextStyle(fontWeight: FontWeight.w800)),
      ),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(20, 12, 20, 24),
        children: [
          Container(
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              color: _card,
              borderRadius: BorderRadius.circular(30),
              border: Border.all(color: _line),
            ),
            child: Column(
              children: [
                Container(
                  width: 88,
                  height: 88,
                  decoration: BoxDecoration(
                    gradient: const LinearGradient(
                      colors: [Color(0xFF8E1D16), Color(0xFFD90416)],
                    ),
                    borderRadius: BorderRadius.circular(28),
                  ),
                  child: const Icon(Icons.person_outline, color: Colors.white, size: 42),
                ),
                const SizedBox(height: 16),
                Text(
                  nombre,
                  style: const TextStyle(
                    color: _ink,
                    fontWeight: FontWeight.w900,
                    fontSize: 24,
                  ),
                ),
                const SizedBox(height: 6),
                Text(
                  correo,
                  style: const TextStyle(
                    color: _muted,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),
          _actionCard(
            icon: Icons.lock_outline,
            title: 'Cambiar contrasena',
            subtitle: 'Accede al flujo de recuperacion y cambio.',
            onTap: () => Navigator.pushNamed(context, '/reset'),
          ),
          const SizedBox(height: 12),
          _actionCard(
            icon: Icons.logout,
            title: 'Cerrar sesion',
            subtitle: 'Salir del panel de meseros sin tocar datos operativos.',
            onTap: () async {
              await SessionService.cerrarSesion();
              if (!context.mounted) {
                return;
              }
              Navigator.pushNamedAndRemoveUntil(context, '/login', (_) => false);
            },
          ),
        ],
      ),
    );
  }

  Widget _actionCard({
    required IconData icon,
    required String title,
    required String subtitle,
    required VoidCallback onTap,
  }) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(24),
      child: Container(
        padding: const EdgeInsets.all(18),
        decoration: BoxDecoration(
          color: _card,
          borderRadius: BorderRadius.circular(24),
          border: Border.all(color: _line),
        ),
        child: Row(
          children: [
            Container(
              width: 52,
              height: 52,
              decoration: BoxDecoration(
                color: const Color(0xFFFFECEE),
                borderRadius: BorderRadius.circular(18),
              ),
              child: Icon(icon, color: _accent),
            ),
            const SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: const TextStyle(
                      color: _ink,
                      fontWeight: FontWeight.w800,
                      fontSize: 16,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    subtitle,
                    style: const TextStyle(color: _muted, height: 1.35),
                  ),
                ],
              ),
            ),
            const Icon(Icons.arrow_forward_ios_rounded, size: 18, color: _muted),
          ],
        ),
      ),
    );
  }
}
