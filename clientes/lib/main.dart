// Archivo principal de arranque de la aplicacion Flutter para clientes.
import 'package:flutter/material.dart';

import 'screens/confirm_code_screen.dart';
import 'screens/forgot_password_screen.dart';
import 'screens/home_screen.dart';
import 'screens/login_screen.dart';
import 'screens/mapa_screen.dart';
import 'screens/menu_screen.dart';
import 'screens/notificaciones_screen.dart';
import 'screens/opciones_pedido_screen.dart';
import 'screens/pedidos_screen.dart';
import 'screens/pesqueria_screen.dart';
import 'screens/register_screen.dart';
import 'screens/reset_password_screen.dart';
import 'screens/restaurante_screen.dart';
import 'screens/success_screen.dart';
import 'screens/welcome_screen.dart';
import 'services/bongusto_api.dart';
import 'services/session_service.dart';
import 'language_controller.dart';
import 'theme_controller.dart';

// Punto de entrada de la app de clientes.
Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await SessionService.init();
  await ThemeController.init();
  await LanguageController.init();
  if (SessionService.estaAutenticado) {
    try {
      final usuario = await BongustoApi.refrescarSesionActual();
      await SessionService.actualizarSesion(usuario);
    } catch (_) {}
  }
  runApp(const BonGustoApp());
}

// Paleta base compartida por la experiencia visual de clientes.
const kBrandRed = Color(0xFFD90416);
const kFieldFill = Color(0xFFF8F8FA);
const kPageBg = Color(0xFFF2F1F4);
const kTextColor = Color(0xFF181818);
const kMutedText = Color(0xFF73727A);
const kLineColor = Color(0xFFE8E6EB);

// Widget raiz que define tema, rutas y configuracion global de la app.
class BonGustoApp extends StatelessWidget {
  const BonGustoApp({super.key});

  @override
  Widget build(BuildContext context) {
    return ValueListenableBuilder<bool>(
      valueListenable: ThemeController.isDark,
      builder: (context, isDark, _) {
        return ValueListenableBuilder<String>(
          valueListenable: LanguageController.language,
          builder: (context, language, __) => MaterialApp(
            title: language == 'en' ? 'BonGusto' : 'BonGusto',
            debugShowCheckedModeBanner: false,
            themeMode: isDark ? ThemeMode.dark : ThemeMode.light,
            // Tema base reutilizado por todas las pantallas de la app cliente.
            theme: _lightTheme(),
            darkTheme: _darkTheme(),
            // Mapa central de rutas de navegacion del cliente.
            initialRoute: '/start',
            routes: {
              '/start': (_) => const WelcomeScreen(),
              '/login': (_) => const LoginScreen(),
              '/register': (_) => const RegisterScreen(),
              '/forgot': (_) => const ForgotPasswordScreen(),
              '/confirm': (_) => const ConfirmCodeScreen(),
              '/reset': (_) => const ResetPasswordScreen(),
              '/success': (_) => const SuccessScreen(),
              '/home': (_) => const HomeScreen(),
              '/pesqueria': (_) => const PesqueriaScreen(),
              '/menu': (_) => const MenuScreen(),
              '/notificaciones': (_) => const NotificacionesScreen(),
              '/opciones-pedido': (_) => const OpcionesPedidoScreen(),
              '/mapa': (_) => const MapScreen(),
              '/restaurante': (_) => const RestauranteScreen(),
              '/pedidos': (_) => const PedidosScreen(),
            },
          ),
        );
      },
    );
  }

  ThemeData _lightTheme() {
    return ThemeData(
      useMaterial3: true,
      primaryColor: kBrandRed,
      scaffoldBackgroundColor: kPageBg,
      cardColor: Colors.white,
      dividerColor: kLineColor,
      colorScheme: ColorScheme.fromSeed(
        seedColor: kBrandRed,
        primary: kBrandRed,
        surface: Colors.white,
        onSurface: kTextColor,
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
          textStyle: const TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
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
      chipTheme: ChipThemeData(
        backgroundColor: kFieldFill,
        selectedColor: const Color(0xFFFFECEE),
        side: const BorderSide(color: kLineColor),
        labelStyle: const TextStyle(
          color: kTextColor,
          fontWeight: FontWeight.w700,
        ),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
      ),
    );
  }

  ThemeData _darkTheme() {
    const darkBg = Color(0xFF0F1117);
    const darkSurface = Color(0xFF1A1D27);
    const darkField = Color(0xFF242837);
    const darkText = Color(0xFFF4F5F9);
    const darkMuted = Color(0xFFA7ADBD);
    const darkLine = Color(0xFF313544);

    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.dark,
      primaryColor: kBrandRed,
      scaffoldBackgroundColor: darkBg,
      colorScheme: ColorScheme.fromSeed(
        seedColor: kBrandRed,
        brightness: Brightness.dark,
        primary: kBrandRed,
        surface: darkSurface,
        onSurface: darkText,
      ),
      textTheme: ThemeData.dark().textTheme.apply(
        bodyColor: darkText,
        displayColor: darkText,
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: darkField,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: const BorderSide(color: darkLine),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: const BorderSide(color: darkLine),
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
          textStyle: const TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
        ),
      ),
      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(foregroundColor: kBrandRed),
      ),
      appBarTheme: const AppBarTheme(
        backgroundColor: darkBg,
        foregroundColor: darkText,
        elevation: 0,
        scrolledUnderElevation: 0,
      ),
      bottomNavigationBarTheme: const BottomNavigationBarThemeData(
        backgroundColor: darkSurface,
        selectedItemColor: kBrandRed,
        unselectedItemColor: darkMuted,
        type: BottomNavigationBarType.fixed,
        showUnselectedLabels: true,
      ),
      cardColor: darkSurface,
      dividerColor: darkLine,
      chipTheme: ChipThemeData(
        backgroundColor: darkField,
        selectedColor: const Color(0xFF3A1D24),
        side: const BorderSide(color: darkLine),
        labelStyle: const TextStyle(
          color: darkText,
          fontWeight: FontWeight.w700,
        ),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
      ),
    );
  }
}
