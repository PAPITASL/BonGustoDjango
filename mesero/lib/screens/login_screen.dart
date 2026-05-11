// ===== Pantalla `login_screen.dart` | Gestiona el acceso del mesero a la aplicacion mediante correo y contrasena. =====
import 'package:flutter/material.dart';

import '../language_controller.dart';
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
      if (!mounted) {
        return;
      }
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
      final mensaje = e.toString().replaceFirst('Exception: ', '').trim();
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            mensaje.isEmpty ? 'No fue posible iniciar sesion.' : mensaje,
          ),
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final bool isDark = Theme.of(context).brightness == Brightness.dark;
    final Color pageBg = isDark ? const Color(0xFF0F1117) : const Color(0xFFF5F5F5);
    final Color cardBg = isDark ? const Color(0xFF1A1D27) : Colors.white;
    final Color titleColor = isDark ? const Color(0xFFF4F5F9) : const Color(0xFF181818);
    final Color subtitleColor = isDark ? const Color(0xFFA7ADBD) : const Color(0xFF66636D);

    return Scaffold(
      backgroundColor: pageBg,
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
          child: Column(
            children: [
              Container(
                decoration: BoxDecoration(
                  color: cardBg,
                  borderRadius: BorderRadius.circular(16),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withValues(alpha: 0.06),
                      blurRadius: 18,
                      offset: const Offset(0, 8),
                    ),
                  ],
                ),
                child: Column(
                  children: [
                    ClipRRect(
                      borderRadius: const BorderRadius.only(
                        topLeft: Radius.circular(16),
                        topRight: Radius.circular(16),
                      ),
                      child: Stack(
                        children: [
                          SizedBox(
                            height: 220,
                            width: double.infinity,
                            child: Image.asset(
                              'assets/cocktail.png',
                              fit: BoxFit.cover,
                              alignment: Alignment.topCenter,
                            ),
                          ),
                          Positioned.fill(
                            child: DecoratedBox(
                              decoration: BoxDecoration(
                                gradient: LinearGradient(
                                  begin: Alignment.topCenter,
                                  end: Alignment.bottomCenter,
                                  colors: [
                                    Colors.transparent,
                                    cardBg.withValues(alpha: 0.98),
                                  ],
                                  stops: const [0.64, 1.0],
                                ),
                              ),
                            ),
                          ),
                          Positioned(
                            left: 16,
                            top: 14,
                            child: Container(
                              padding: const EdgeInsets.symmetric(
                                horizontal: 10,
                                vertical: 6,
                              ),
                              decoration: BoxDecoration(
                                color: Colors.black.withValues(alpha: 0.48),
                                borderRadius: BorderRadius.circular(999),
                              ),
                              child: const Text(
                                'PORTAL MESEROS',
                                style: TextStyle(
                                  color: Colors.white,
                                  fontSize: 11,
                                  letterSpacing: 1.1,
                                  fontWeight: FontWeight.w800,
                                ),
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                    Padding(
                      padding: const EdgeInsets.fromLTRB(22, 18, 22, 24),
                      child: Form(
                        key: _formKey,
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.stretch,
                          children: [
                            Text(
                              LanguageController.t('Iniciar sesion', 'Sign in'),
                              style: TextStyle(
                                color: titleColor,
                                fontSize: 28,
                                fontWeight: FontWeight.w900,
                              ),
                            ),
                            const SizedBox(height: 8),
                            Text(
                              LanguageController.t(
                                'Acceso operativo del equipo de meseros.',
                                'Operational access for the waiters team.',
                              ),
                              style: TextStyle(
                                color: subtitleColor,
                                fontSize: 13,
                                height: 1.45,
                              ),
                            ),
                            const SizedBox(height: 20),
                            Text(
                              LanguageController.t('Correo electronico', 'Email'),
                              style: TextStyle(color: titleColor),
                            ),
                            const SizedBox(height: 6),
                            TextFormField(
                              controller: _emailCtrl,
                              keyboardType: TextInputType.emailAddress,
                              style: const TextStyle(color: Colors.black87),
                              onChanged: (v) =>
                                  setState(() => _emailValido = _isValidEmail(v)),
                              decoration: InputDecoration(
                                hintText: 'ejemplo@bongusto.com',
                                fillColor: const Color(0xFFF2F3F7),
                                hintStyle: const TextStyle(color: Colors.black54),
                                suffixIcon: _emailValido
                                    ? const Icon(
                                        Icons.check_circle,
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
                                    'Correo no valido',
                                    'Invalid email',
                                  );
                                }
                                return null;
                              },
                            ),
                            const SizedBox(height: 16),
                            Text(
                              LanguageController.t('Contrasena', 'Password'),
                              style: TextStyle(color: titleColor),
                            ),
                            const SizedBox(height: 6),
                            TextFormField(
                              controller: _passCtrl,
                              obscureText: _obscure,
                              style: const TextStyle(color: Colors.black87),
                              decoration: InputDecoration(
                                hintText: 'ingresar contrasena',
                                fillColor: const Color(0xFFF2F3F7),
                                hintStyle: const TextStyle(color: Colors.black54),
                                suffixIcon: IconButton(
                                  icon: Icon(
                                    _obscure
                                        ? Icons.visibility_off
                                        : Icons.visibility,
                                    color: Colors.black54,
                                  ),
                                  onPressed: () =>
                                      setState(() => _obscure = !_obscure),
                                ),
                              ),
                              validator: (v) {
                                if (v == null || v.isEmpty) {
                                  return LanguageController.t(
                                    'Ingrese su contrasena',
                                    'Enter your password',
                                  );
                                }
                                if (v.length < 8) {
                                  return LanguageController.t(
                                    'Minimo 8 caracteres',
                                    'Minimum 8 characters',
                                  );
                                }
                                return null;
                              },
                            ),
                            const SizedBox(height: 12),
                            Align(
                              alignment: Alignment.centerRight,
                              child: GestureDetector(
                                onTap: () => Navigator.pushNamed(context, '/forgot'),
                                child: Text(
                                  LanguageController.t(
                                    'Olvidaste tu contrasena?',
                                    'Forgot your password?',
                                  ),
                                  style: const TextStyle(color: Colors.red),
                                ),
                              ),
                            ),
                            const SizedBox(height: 20),
                            ElevatedButton(
                              onPressed: _login,
                              child: Text(
                                LanguageController.t('Iniciar sesion', 'Sign in'),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ],
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
