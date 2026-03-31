// ===== Pantalla `forgot_password_screen.dart` | Permite solicitar el envio del codigo para recuperar la cuenta. =====
import 'package:flutter/material.dart';

// ===== Clase `ForgotPasswordScreen` | Define la vista donde el usuario ingresa su correo para recuperar acceso. =====
class ForgotPasswordScreen extends StatefulWidget {
  const ForgotPasswordScreen({super.key});

  @override
  State<ForgotPasswordScreen> createState() => _ForgotPasswordScreenState();
}

// ===== Estado `_ForgotPasswordScreenState` | Controla el formulario de correo y la transicion al siguiente paso. =====
class _ForgotPasswordScreenState extends State<ForgotPasswordScreen> {
  final _emailCtrl = TextEditingController(); // Controlador email

  @override
  void dispose() {
    _emailCtrl.dispose();
    super.dispose();
  }

  // Accion: Enviar Codigo
  void _sendCode() {
    if (_emailCtrl.text.trim().isEmpty) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text('Ingrese su correo')));
      return;
    }
    Navigator.pushNamed(context, '/confirm');
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF5F5F5),
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
                      const Text(
                        '¿Olvidaste tu contraseña?',
                        style: TextStyle(
                          fontSize: 28,
                          fontWeight: FontWeight.w900,
                        ),
                      ),
                      const SizedBox(height: 12),
                      const Text(
                        'Ingresa el correo asociado a tu cuenta para recibir un código.',
                      ),
                      const SizedBox(height: 22),
                      TextField(
                        controller: _emailCtrl,
                        decoration: const InputDecoration(
                          hintText: 'ejemplo@bongusto.com',
                        ),
                      ),
                      const SizedBox(height: 20),
                      ElevatedButton(
                        onPressed: _sendCode,
                        child: const Text('Enviar código'),
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
