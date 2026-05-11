import 'package:flutter/material.dart';

import '../language_controller.dart';
import '../services/bongusto_api.dart';

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
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text(LanguageController.t('Ingrese su correo', 'Enter your email'))));
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
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('$e')),
      );
    } finally {
      if (mounted) {
        setState(() => _sending = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    const cardText = Color(0xFF181818);
    const cardMuted = Color(0xFF66636D);
    return Scaffold(
      backgroundColor: isDark ? const Color(0xFF101218) : const Color(0xFFF5F5F5),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(20),
          child: Column(
            children: [
              Container(
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(12),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withValues(alpha: 0.06),
                      blurRadius: 18,
                      offset: const Offset(0, 8),
                    ),
                  ],
                ),
                child: Padding(
                  padding: const EdgeInsets.all(22),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      Text(
                        LanguageController.t('¿Olvidaste tu contraseña?', 'Forgot your password?'),
                        style: const TextStyle(
                          color: cardText,
                          fontSize: 28,
                          fontWeight: FontWeight.w900,
                        ),
                      ),
                      const SizedBox(height: 12),
                      Text(
                        LanguageController.t(
                          'Ingresa el correo asociado a tu cuenta para recibir un código de seguridad.',
                          'Enter the email linked to your account to receive a security code.',
                        ),
                        style: const TextStyle(color: cardMuted),
                      ),
                      const SizedBox(height: 22),
                      TextField(
                        controller: _emailCtrl,
                        style: const TextStyle(color: cardText),
                        decoration: const InputDecoration(
                          hintText: 'ejemplo@bongusto.com',
                        ),
                      ),
                      const SizedBox(height: 20),
                      ElevatedButton(
                        onPressed: _sending ? null : _sendLink,
                        child: Text(_sending ? LanguageController.tr('Enviando...') : LanguageController.tr('Enviar enlace')),
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
            ],
          ),
        ),
      ),
    );
  }
}

