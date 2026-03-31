// ===== Pantalla `login_screen.dart` | Gestiona el acceso del mesero a la aplicacion mediante correo y contrasena. =====
import 'package:flutter/material.dart';

import '../services/bongusto_api.dart';
import '../services/session_service.dart';

// ===== Clase `LoginScreen` | Define la vista principal de autenticacion del modulo meseros. =====
class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

// ===== Estado `_LoginScreenState` | Maneja validaciones, campos del formulario y el proceso de inicio de sesion. =====
class _LoginScreenState extends State<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailCtrl = TextEditingController();
  final _passCtrl = TextEditingController();

  bool _obscure = true;
  bool _emailValido = false;

  @override
  void dispose() {
    _emailCtrl.dispose();
    _passCtrl.dispose();
    super.dispose();
  }

  bool _isValidEmail(String v) {
    final reg = RegExp(r'^[\w\.\-]+@([\w\-]+\.)+[a-zA-Z]{2,}$');
    return reg.hasMatch(v);
  }

  Future<void> _login() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    final email = _emailCtrl.text.trim();
    final pass = _passCtrl.text.trim();

    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (_) => const Center(child: CircularProgressIndicator()),
    );

    try {
      final userData = await BongustoApi.loginMesero(
        correo: email,
        clave: pass,
      );
      if (!mounted) {
        return;
      }
      Navigator.of(context).pop();
      await SessionService.iniciarSesion(userData);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            'Bienvenido ${userData['nombre_completo'] ?? userData['nombre'] ?? ''}',
          ),
        ),
      );
      Navigator.pushReplacementNamed(context, '/home');
    } catch (e) {
      if (!mounted) {
        return;
      }
      Navigator.of(context).pop();
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error de conexion: $e')),
      );
    }
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
                  child: Form(
                    key: _formKey,
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        const Text(
                          'Iniciar sesion',
                          style: TextStyle(
                            fontSize: 28,
                            fontWeight: FontWeight.w900,
                          ),
                        ),
                        const SizedBox(height: 24),
                        const Text('Correo electronico'),
                        const SizedBox(height: 6),
                        TextFormField(
                          controller: _emailCtrl,
                          keyboardType: TextInputType.emailAddress,
                          onChanged: (v) =>
                              setState(() => _emailValido = _isValidEmail(v)),
                          decoration: InputDecoration(
                            hintText: 'ejemplo@bongusto.com',
                            suffixIcon: _emailValido
                                ? const Icon(
                                    Icons.check_circle,
                                    color: Color(0xFFB2281D),
                                  )
                                : null,
                          ),
                          validator: (v) {
                            if (v == null || v.trim().isEmpty) {
                              return 'Ingrese su correo';
                            }
                            if (!_isValidEmail(v.trim())) {
                              return 'Correo no valido';
                            }
                            return null;
                          },
                        ),
                        const SizedBox(height: 16),
                        const Text('Contrasena'),
                        const SizedBox(height: 6),
                        TextFormField(
                          controller: _passCtrl,
                          obscureText: _obscure,
                          decoration: InputDecoration(
                            hintText: 'ingresar contrasena',
                            suffixIcon: IconButton(
                              icon: Icon(
                                _obscure
                                    ? Icons.visibility_off
                                    : Icons.visibility,
                              ),
                              onPressed: () =>
                                  setState(() => _obscure = !_obscure),
                            ),
                          ),
                          validator: (v) {
                            if (v == null || v.isEmpty) {
                              return 'Ingrese su contrasena';
                            }
                            if (v.length < 8) {
                              return 'Minimo 8 caracteres';
                            }
                            return null;
                          },
                        ),
                        const SizedBox(height: 12),
                        Align(
                          alignment: Alignment.centerRight,
                          child: GestureDetector(
                            onTap: () =>
                                Navigator.pushNamed(context, '/forgot'),
                            child: const Text(
                              'Olvidaste tu contrasena?',
                              style: TextStyle(color: Colors.red),
                            ),
                          ),
                        ),
                        const SizedBox(height: 20),
                        ElevatedButton(
                          onPressed: _login,
                          child: const Text('Iniciar sesion'),
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
