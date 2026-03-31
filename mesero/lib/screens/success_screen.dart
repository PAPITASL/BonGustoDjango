// ===== Pantalla `success_screen.dart` | Esta vista confirma que el proceso de recuperacion o cambio de clave termino correctamente. =====
import 'package:flutter/material.dart';

// ===== Clase `SuccessScreen` | Muestra el mensaje final de exito y el regreso al login. =====
class SuccessScreen extends StatelessWidget {
  const SuccessScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF5F5F5),
      body: SafeArea(
        child: Center(
          child: Padding(
            padding: const EdgeInsets.all(22),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Text('Contraseña cambiada',
                    style:
                        TextStyle(fontSize: 26, fontWeight: FontWeight.w900)),
                const SizedBox(height: 12),
                const Text('Tu contraseña ha sido cambiada exitosamente.'),
                const SizedBox(height: 24),
                ElevatedButton(
                  onPressed: () =>
                      Navigator.pushNamedAndRemoveUntil(context, '/login', (_) => false),
                  child: const Text('Volver al inicio de sesión'),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
