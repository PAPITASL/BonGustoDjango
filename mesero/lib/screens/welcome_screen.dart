// ===== Pantalla `welcome_screen.dart` | Aqui se muestra la bienvenida inicial antes de entrar al flujo de autenticacion. =====
import 'package:flutter/material.dart';

import '../language_controller.dart';

// ===== Clase `WelcomeScreen` | Representa la portada de ingreso del modulo de meseros. =====
class WelcomeScreen extends StatelessWidget {
  const WelcomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final bool isDark = Theme.of(context).brightness == Brightness.dark;
    final Color pageBg = isDark ? const Color(0xFF0F1117) : const Color(0xFFF5F5F5);
    final Color cardBg = isDark ? const Color(0xFF1A1D27) : Colors.white;
    final Color titleColor = isDark ? const Color(0xFFF4F5F9) : const Color(0xFF181818);
    final Color subtitleColor = isDark ? const Color(0xFFA7ADBD) : const Color(0xFF66636D);

    return Scaffold(
      backgroundColor: pageBg,
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
          child: Column(
            children: [
              Container(
                decoration: BoxDecoration(
                  color: cardBg,
                  borderRadius: BorderRadius.circular(16),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withValues(alpha: 0.06),
                      blurRadius: 18,
                      offset: const Offset(0, 8),
                    ),
                  ],
                ),
                child: Column(
                  children: [
                    ClipRRect(
                      borderRadius: const BorderRadius.only(
                        topLeft: Radius.circular(16),
                        topRight: Radius.circular(16),
                      ),
                      child: Stack(
                        children: [
                          SizedBox(
                            height: 460,
                            width: double.infinity,
                            child: Image.asset(
                              'assets/cocktail.png',
                              fit: BoxFit.cover,
                              alignment: Alignment.topCenter,
                            ),
                          ),
                          Positioned.fill(
                            child: DecoratedBox(
                              decoration: BoxDecoration(
                                gradient: LinearGradient(
                                  begin: Alignment.topCenter,
                                  end: Alignment.bottomCenter,
                                  colors: [
                                    Colors.transparent,
                                    cardBg.withValues(alpha: 0.98),
                                  ],
                                  stops: const [0.68, 1.0],
                                ),
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                    Padding(
                      padding: const EdgeInsets.fromLTRB(20, 20, 20, 22),
                      child: Column(
                        children: [
                          Text(
                            LanguageController.t('BonGusto Meseros', 'BonGusto Waiters'),
                            style: TextStyle(
                              color: titleColor,
                              fontSize: 22,
                              fontWeight: FontWeight.w800,
                            ),
                          ),
                          const SizedBox(height: 10),
                          Text(
                            LanguageController.t(
                              'Acceso operativo para gestion de mesas, pedidos y servicio en tiempo real.',
                              'Operational access for tables, orders, and real-time service.',
                            ),
                            textAlign: TextAlign.center,
                            style: TextStyle(
                              color: subtitleColor,
                              fontSize: 14,
                              height: 1.4,
                            ),
                          ),
                          const SizedBox(height: 22),
                          SizedBox(
                            width: double.infinity,
                            child: ElevatedButton(
                              style: ElevatedButton.styleFrom(
                                shape: const StadiumBorder(),
                              ),
                              onPressed: () => Navigator.pushNamed(context, '/login'),
                              child: Text(LanguageController.t('Iniciar sesion', 'Sign in')),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 20),
            ],
          ),
        ),
      ),
    );
  }
}
