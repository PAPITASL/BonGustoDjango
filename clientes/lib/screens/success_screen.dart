// Pantalla de confirmacion visual para operaciones exitosas del usuario.
import 'package:flutter/material.dart';

import '../app_theme.dart';
import 'app_settings_controls.dart';

// Widget simple de exito despues de un flujo de autenticacion o recuperacion.
class SuccessScreen extends StatelessWidget {
  const SuccessScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppThemeColors.bg,
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Align(
                alignment: Alignment.centerRight,
                child: AppSettingsControls(),
              ),
              const SizedBox(height: 10),
              Padding(
                padding: EdgeInsets.only(left: 4, bottom: 12),
                child: Text(
                  'Confirmacion-exitosa',
                  style: TextStyle(
                    fontSize: 20,
                    color: AppThemeColors.muted,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
              Container(
                height: MediaQuery.of(context).size.height * 0.78,
                decoration: AppThemeColors.card(radius: 12, shadow: true),
                child: Center(
                  child: Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 24),
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Text(
                          'Contraseña cambiada',
                          textAlign: TextAlign.center,
                          style: TextStyle(
                            color: AppThemeColors.text,
                            fontSize: 26,
                            fontWeight: FontWeight.w900,
                          ),
                        ),
                        const SizedBox(height: 10),
                        Text(
                          'Tu contraseña ha sido cambiada exitosamente.',
                          textAlign: TextAlign.center,
                          style: TextStyle(
                            fontSize: 14,
                            color: AppThemeColors.muted,
                          ),
                        ),
                        const SizedBox(height: 26),
                        SizedBox(
                          width: double.infinity,
                          child: Padding(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 16.0,
                            ),
                            child: ElevatedButton(
                              onPressed: () =>
                                  Navigator.pushNamedAndRemoveUntil(
                                    context,
                                    '/login',
                                    (_) => false,
                                  ),
                              child: const Text('Volver al inicio de sesión'),
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
