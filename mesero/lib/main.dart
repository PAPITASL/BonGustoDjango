// ===== Archivo principal `main.dart` | Aqui se arranca la app de meseros, se define el tema global y se registran las rutas principales. =====
import 'package:flutter/material.dart';

import 'screens/confirm_code_screen.dart';
import 'screens/forgot_password_screen.dart';
import 'screens/gestion_mesas_screen.dart';
import 'screens/home_screen.dart';
import 'screens/interaccion_screen.dart';
import 'screens/login_screen.dart';
import 'screens/menu_screen.dart';
import 'screens/musica_screen.dart';
import 'screens/notificaciones_admin_screen.dart';
import 'screens/pedidos_screen.dart';
import 'screens/perfil_screen.dart';
import 'screens/reset_password_screen.dart';
import 'screens/success_screen.dart';
import 'screens/welcome_screen.dart';
import 'services/bongusto_api.dart';
import 'services/session_service.dart';

// Punto de entrada de la app operativa para meseros.
Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await SessionService.init();
  if (SessionService.estaAutenticado) {
    try {
      final usuario = await BongustoApi.refrescarSesionActual();
      await SessionService.actualizarSesion(usuario);
    } catch (_) {}
  }
  runApp(const BonGustoApp());
}

// Paleta base compartida por la experiencia visual de meseros.
const kBrandRed = Color(0xFFD90416);
const kFieldFill = Color(0xFFF8F8FA);
const kPageBg = Color(0xFFF2F1F4);
const kTextColor = Color(0xFF181818);
const kMutedText = Color(0xFF73727A);
const kLineColor = Color(0xFFE8E6EB);

// ===== Clase `BonGustoApp` | Representa la raiz del `MaterialApp` y la navegacion general del proyecto Flutter. =====
class BonGustoApp extends StatelessWidget {
  const BonGustoApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'BonGusto Meseros',
      debugShowCheckedModeBanner: false,
      // Tema base reutilizado por las pantallas internas del flujo de meseros.
      theme: ThemeData(
        useMaterial3: true,
        primaryColor: kBrandRed,
        scaffoldBackgroundColor: kPageBg,
        colorScheme: ColorScheme.fromSeed(
          seedColor: kBrandRed,
          primary: kBrandRed,
          surface: Colors.white,
        ),
        textTheme: ThemeData.light().textTheme.apply(
          bodyColor: kTextColor,
          displayColor: kTextColor,
        ),
        inputDecorationTheme: InputDecorationTheme(
          filled: true,
          fillColor: kFieldFill,
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(14),
            borderSide: const BorderSide(color: kLineColor),
          ),
          enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(14),
            borderSide: const BorderSide(color: kLineColor),
          ),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(14),
            borderSide: const BorderSide(color: kBrandRed),
          ),
          contentPadding: const EdgeInsets.symmetric(
            horizontal: 14,
            vertical: 14,
          ),
        ),
        elevatedButtonTheme: ElevatedButtonThemeData(
          style: ElevatedButton.styleFrom(
            backgroundColor: kBrandRed,
            foregroundColor: Colors.white,
            padding: const EdgeInsets.symmetric(vertical: 16),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
            ),
            textStyle: const TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.w600,
            ),
          ),
        ),
        textButtonTheme: TextButtonThemeData(
          style: TextButton.styleFrom(foregroundColor: kBrandRed),
        ),
        appBarTheme: const AppBarTheme(
          backgroundColor: kPageBg,
          foregroundColor: kTextColor,
          elevation: 0,
          scrolledUnderElevation: 0,
        ),
        bottomNavigationBarTheme: const BottomNavigationBarThemeData(
          backgroundColor: Colors.white,
          selectedItemColor: kBrandRed,
          unselectedItemColor: kMutedText,
          type: BottomNavigationBarType.fixed,
          showUnselectedLabels: true,
        ),
      ),
      // Mapa central de navegacion para el equipo de servicio.
      initialRoute: '/start',
      routes: {
        '/start': (_) => const WelcomeScreen(),
        '/login': (_) => const LoginScreen(),
        '/forgot': (_) => const ForgotPasswordScreen(),
        '/confirm': (_) => const ConfirmCodeScreen(),
        '/reset': (_) => const ResetPasswordScreen(),
        '/success': (_) => const SuccessScreen(),
        '/home': (_) => const HomeScreen(),
        '/notificaciones': (_) => const NotificacionesAdminScreen(),
        '/menu': (_) => const MenuScreen(),
        '/pedidos': (_) => const PedidosScreen(),
        '/mesas': (_) => const GestionMesasScreen(),
        '/interaccion': (_) => const InteraccionScreen(),
        '/musica': (_) => const MusicaScreen(),
        '/perfil': (_) => const PerfilScreen(),
      },
    );
  }
}
