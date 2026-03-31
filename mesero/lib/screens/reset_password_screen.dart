// ===== Pantalla `reset_password_screen.dart` | Aqui el usuario define y confirma su nueva contrasena. =====
import 'package:flutter/material.dart';

// ===== Clase `ResetPasswordScreen` | Representa el ultimo paso del flujo de restablecimiento de clave. =====
class ResetPasswordScreen extends StatefulWidget {
  const ResetPasswordScreen({super.key});

  @override
  State<ResetPasswordScreen> createState() => _ResetPasswordScreenState();
}

// ===== Estado `_ResetPasswordScreenState` | Controla validaciones, visibilidad y confirmacion de contrasenas. =====
class _ResetPasswordScreenState extends State<ResetPasswordScreen> {
  final _pass1Ctrl = TextEditingController(); // Nueva contraseña
  final _pass2Ctrl = TextEditingController(); // Confirmar contraseña
  bool _obscure1 = true; // visibilidad del campo 1
  bool _obscure2 = true; // visibilidad del campo 2

  @override
  void dispose() {
    _pass1Ctrl.dispose();
    _pass2Ctrl.dispose();
    super.dispose();
  }

  // Parametros de Seguraridad
  bool _strongPass(String v) {
    final reg = RegExp(
        r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&\.\-\_]).{8,}$');
    return reg.hasMatch(v);
  }

  // Resetear contraseña
  void _reset() {
    final p1 = _pass1Ctrl.text;
    final p2 = _pass2Ctrl.text;

    if (!_strongPass(p1)) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
          content: Text(
              'Incluye mayúscula, minúscula, número y símbolo (8+)')));
      return;
    }
    if (p1 != p2) {
      ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Las contraseñas no coinciden')));
      return;
    }

    Navigator.pushReplacementNamed(context, '/success');
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
                    )
                  ],
                ),
                child: Padding(
                  padding: const EdgeInsets.all(22),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      const Text('Restablecer contraseña',
                          style: TextStyle(
                              fontSize: 26, fontWeight: FontWeight.w900)),
                      const SizedBox(height: 12),
                      TextField(
                        controller: _pass1Ctrl,
                        obscureText: _obscure1,
                        decoration: InputDecoration(
                          hintText: 'Nueva contraseña',
                          suffixIcon: IconButton(
                            icon: Icon(_obscure1
                                ? Icons.visibility
                                : Icons.visibility_off),
                            onPressed: () =>
                                setState(() => _obscure1 = !_obscure1),
                          ),
                        ),
                      ),
                      const SizedBox(height: 16),
                      TextField(
                        controller: _pass2Ctrl,
                        obscureText: _obscure2,
                        decoration: InputDecoration(
                          hintText: 'Confirmar contraseña',
                          suffixIcon: IconButton(
                            icon: Icon(_obscure2
                                ? Icons.visibility
                                : Icons.visibility_off),
                            onPressed: () =>
                                setState(() => _obscure2 = !_obscure2),
                          ),
                        ),
                      ),
                      const SizedBox(height: 20),
                      ElevatedButton(
                          onPressed: _reset,
                          child: const Text('Restablecer contraseña')),
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
