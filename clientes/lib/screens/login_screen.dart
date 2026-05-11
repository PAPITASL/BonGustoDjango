// Pantalla de inicio de sesion para los clientes de la app.
import 'package:flutter/material.dart';

import '../app_theme.dart';
import '../language_controller.dart';
import '../services/bongusto_api.dart';
import '../services/session_service.dart';
import 'app_settings_controls.dart';

// Widget principal del formulario de autenticacion.
class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

// Estado que administra validacion, campos y envio de credenciales.
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

  void _login() {
    if (_formKey.currentState!.validate()) {
      _performLogin();
    }
  }

  Future<void> _performLogin() async {
    final email = _emailCtrl.text.trim();
    final password = _passCtrl.text;

    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (_) => const Center(child: CircularProgressIndicator()),
    );

    try {
      final user = await BongustoApi.login(correo: email, clave: password);
      if (!mounted) {
        return;
      }
      Navigator.of(context).pop();
      await SessionService.iniciarSesion(user);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Bienvenido ${user['nombre_completo'] ?? ''}')),
      );
      Navigator.pushReplacementNamed(context, '/home');
    } catch (e) {
      if (!mounted) {
        return;
      }
      Navigator.of(context).pop();
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text('Error: $e')));
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
                  child: Form(
                    key: _formKey,
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        Text(
                          LanguageController.t('Iniciar sesión', 'Sign in'),
                          style: TextStyle(
                            color: AppThemeColors.text,
                            fontSize: 28,
                            height: 1.1,
                            letterSpacing: -0.2,
                            fontWeight: FontWeight.w900,
                          ),
                        ),
                        const SizedBox(height: 24),
                        Text(
                          LanguageController.t('Correo electrónico', 'Email'),
                          style: TextStyle(
                            fontSize: 14,
                            color: AppThemeColors.text,
                          ),
                        ),
                        const SizedBox(height: 6),
                        TextFormField(
                          controller: _emailCtrl,
                          keyboardType: TextInputType.emailAddress,
                          onChanged: (v) => setState(() {
                            _emailValido = _isValidEmail(v.trim());
                          }),
                          decoration: InputDecoration(
                            hintText: 'ejemplo@gmail.com',
                            suffixIcon: _emailValido
                                ? const Icon(
                                    Icons.check_circle_rounded,
                                    color: Color(0xFFB2281D),
                                  )
                                : null,
                          ),
                          validator: (v) {
                            if (v == null || v.trim().isEmpty) {
                              return LanguageController.t(
                                'Ingrese su correo',
                                'Enter your email',
                              );
                            }
                            if (!_isValidEmail(v.trim())) {
                              return LanguageController.t(
                                'Correo no válido',
                                'Invalid email',
                              );
                            }
                            return null;
                          },
                        ),
                        const SizedBox(height: 16),
                        Text(
                          LanguageController.t('Contraseña', 'Password'),
                          style: TextStyle(
                            fontSize: 14,
                            color: AppThemeColors.text,
                          ),
                        ),
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
                              return LanguageController.t(
                                'Ingrese su contraseña',
                                'Enter your password',
                              );
                            }
                            if (v.length < 8) {
                              return LanguageController.t(
                                'Mínimo 8 caracteres',
                                'Minimum 8 characters',
                              );
                            }
                            return null;
                          },
                        ),
                        const SizedBox(height: 10),
                        Align(
                          alignment: Alignment.centerRight,
                          child: GestureDetector(
                            onTap: () =>
                                Navigator.pushNamed(context, '/forgot'),
                            child: Text(
                              LanguageController.t(
                                '¿Olvidaste tu contraseña?',
                                'Forgot your password?',
                              ),
                              style: const TextStyle(color: Colors.red),
                            ),
                          ),
                        ),
                        const SizedBox(height: 18),
                        ElevatedButton(
                          onPressed: _login,
                          child: Text(
                            LanguageController.t('Iniciar sesión', 'Sign in'),
                          ),
                        ),
                        const SizedBox(height: 22),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Text(
                              LanguageController.t(
                                '¿No tienes una cuenta? ',
                                "Don't have an account? ",
                              ),
                              style: TextStyle(color: AppThemeColors.muted),
                            ),
                            GestureDetector(
                              onTap: () =>
                                  Navigator.pushNamed(context, '/register'),
                              child: Text(
                                LanguageController.t('Regístrate', 'Sign up'),
                                style: const TextStyle(color: Colors.red),
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 16),
            ],
          ),
        ),
      ),
    );
  }
}
