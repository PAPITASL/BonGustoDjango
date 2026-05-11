import 'package:flutter/material.dart';

import '../app_theme.dart';
import '../language_controller.dart';
import '../services/bongusto_api.dart';
import 'app_settings_controls.dart';

class ForgotPasswordScreen extends StatefulWidget {
  const ForgotPasswordScreen({super.key});

  @override
  State<ForgotPasswordScreen> createState() => _ForgotPasswordScreenState();
}

class _ForgotPasswordScreenState extends State<ForgotPasswordScreen> {
  final _emailCtrl = TextEditingController();
  bool _sending = false;

  @override
  void dispose() {
    _emailCtrl.dispose();
    super.dispose();
  }

  Future<void> _sendLink() async {
    final correo = _emailCtrl.text.trim().toLowerCase();
    if (correo.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            LanguageController.t('Ingrese su correo', 'Enter your email'),
          ),
        ),
      );
      return;
    }

    setState(() => _sending = true);
    try {
      final response = await BongustoApi.solicitarEnlaceRecuperacion(
        correo: correo,
      );
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            LanguageController.tr(
              (response['message'] ??
                      'Si el correo está registrado, recibirás un enlace de recuperación.')
                  .toString(),
            ),
          ),
        ),
      );
      final token = (response['token'] ?? '').toString();
      if ((response['demo_mode'] == true || response['demo_mode'] == 'true') &&
          token.isNotEmpty) {
        Navigator.pushNamed(context, '/reset', arguments: {'token': token});
      }
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('$e')));
    } finally {
      if (mounted) {
        setState(() => _sending = false);
      }
    }
  }

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
              Container(
                decoration: AppThemeColors.card(radius: 12, shadow: true),
                child: Padding(
                  padding: const EdgeInsets.fromLTRB(22, 26, 22, 26),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      Align(
                        alignment: Alignment.centerLeft,
                        child: InkWell(
                          onTap: () => Navigator.pop(context),
                          borderRadius: BorderRadius.circular(12),
                          child: Container(
                            width: 40,
                            height: 40,
                            decoration: BoxDecoration(
                              color: AppThemeColors.surfaceAlt,
                              borderRadius: BorderRadius.circular(12),
                            ),
                            child: const Icon(Icons.arrow_back, size: 20),
                          ),
                        ),
                      ),
                      const SizedBox(height: 18),
                      Text(
                        LanguageController.t(
                          '¿Olvidaste tu contraseña?',
                          'Forgot your password?',
                        ),
                        style: TextStyle(
                          color: AppThemeColors.text,
                          fontSize: 28,
                          height: 1.1,
                          letterSpacing: -0.2,
                          fontWeight: FontWeight.w900,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        LanguageController.t(
                          'Ingresa el correo asociado a tu cuenta y te enviaremos un código de seguridad.',
                          'Enter the email linked to your account and we will send you a security code.',
                        ),
                        style: TextStyle(
                          fontSize: 14,
                          color: AppThemeColors.muted,
                        ),
                      ),
                      const SizedBox(height: 22),
                      Text(
                        LanguageController.t('Correo electrónico', 'Email'),
                        style: TextStyle(
                          fontSize: 14,
                          color: AppThemeColors.text,
                        ),
                      ),
                      const SizedBox(height: 6),
                      TextField(
                        controller: _emailCtrl,
                        keyboardType: TextInputType.emailAddress,
                        decoration: InputDecoration(
                          hintText: LanguageController.t(
                            'Ingresa tu correo electrónico',
                            'Enter your email',
                          ),
                        ),
                      ),
                      const SizedBox(height: 18),
                      ElevatedButton(
                        onPressed: _sending ? null : _sendLink,
                        child: Text(
                          _sending
                              ? LanguageController.tr('Enviando...')
                              : LanguageController.tr('Enviar enlace'),
                        ),
                      ),
                      const SizedBox(height: 10),
                      TextButton(
                        onPressed: _sending
                            ? null
                            : () => Navigator.pushNamed(context, '/confirm'),
                        child: Text(
                          LanguageController.t(
                            'Usar código de seguridad',
                            'Use security code',
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 18),
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text(
                    LanguageController.t(
                      '¿Recordaste tu contraseña? ',
                      'Remembered your password? ',
                    ),
                    style: TextStyle(color: AppThemeColors.muted),
                  ),
                  GestureDetector(
                    onTap: () =>
                        Navigator.pushReplacementNamed(context, '/login'),
                    child: Text(
                      LanguageController.t('Inicia sesión', 'Sign in'),
                      style: const TextStyle(color: Colors.red),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}
