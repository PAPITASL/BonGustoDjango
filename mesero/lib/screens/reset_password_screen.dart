import 'package:flutter/material.dart';

import '../services/bongusto_api.dart';

class ResetPasswordScreen extends StatefulWidget {
  const ResetPasswordScreen({super.key});

  @override
  State<ResetPasswordScreen> createState() => _ResetPasswordScreenState();
}

class _ResetPasswordScreenState extends State<ResetPasswordScreen> {
  final _pass1Ctrl = TextEditingController();
  final _pass2Ctrl = TextEditingController();
  bool _obscure1 = true;
  bool _obscure2 = true;
  bool _saving = false;

  @override
  void dispose() {
    _pass1Ctrl.dispose();
    _pass2Ctrl.dispose();
    super.dispose();
  }

  bool _strongPass(String v) {
    final reg = RegExp(
      r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&\.\-_]).{8,}$',
    );
    return reg.hasMatch(v);
  }

  Future<void> _reset() async {
    final args =
        (ModalRoute.of(context)?.settings.arguments as Map?) ?? const {};
    final correo = (args['correo'] ?? '').toString();
    final codigo = (args['codigo'] ?? '').toString();
    final token = (args['token'] ?? '').toString();
    final p1 = _pass1Ctrl.text;
    final p2 = _pass2Ctrl.text;

    final usaToken = token.isNotEmpty;
    if (!usaToken && (correo.isEmpty || codigo.isEmpty)) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('El flujo de recuperación no es válido')),
      );
      return;
    }

    if (!_strongPass(p1)) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text(
            'Incluye mayúscula, minúscula, número y símbolo (8+)',
          ),
        ),
      );
      return;
    }
    if (p1 != p2) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Las contraseñas no coinciden')),
      );
      return;
    }

    setState(() => _saving = true);
    try {
      final response = usaToken
          ? await BongustoApi.restablecerContrasenaConToken(
              token: token,
              password: p1,
              passwordConfirm: p2,
            )
          : await BongustoApi.restablecerContrasena(
              correo: correo,
              codigo: codigo,
              password: p1,
              passwordConfirm: p2,
            );
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            (response['message'] ??
                    response['mensaje'] ??
                    'Contraseña actualizada')
                .toString(),
          ),
        ),
      );
      Navigator.pushReplacementNamed(context, '/success');
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('$e')),
      );
    } finally {
      if (mounted) {
        setState(() => _saving = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    const cardText = Color(0xFF181818);
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
                      const Text(
                        'Restablecer contraseña',
                        style: TextStyle(
                          color: cardText,
                          fontSize: 26,
                          fontWeight: FontWeight.w900,
                        ),
                      ),
                      const SizedBox(height: 12),
                      TextField(
                        controller: _pass1Ctrl,
                        style: const TextStyle(color: cardText),
                        obscureText: _obscure1,
                        decoration: InputDecoration(
                          hintText: 'Nueva contraseña',
                          suffixIcon: IconButton(
                            icon: Icon(
                              _obscure1
                                  ? Icons.visibility
                                  : Icons.visibility_off,
                            ),
                            onPressed: () =>
                                setState(() => _obscure1 = !_obscure1),
                          ),
                        ),
                      ),
                      const SizedBox(height: 16),
                      TextField(
                        controller: _pass2Ctrl,
                        style: const TextStyle(color: cardText),
                        obscureText: _obscure2,
                        decoration: InputDecoration(
                          hintText: 'Confirmar contraseña',
                          suffixIcon: IconButton(
                            icon: Icon(
                              _obscure2
                                  ? Icons.visibility
                                  : Icons.visibility_off,
                            ),
                            onPressed: () =>
                                setState(() => _obscure2 = !_obscure2),
                          ),
                        ),
                      ),
                      const SizedBox(height: 20),
                      ElevatedButton(
                        onPressed: _saving ? null : _reset,
                        child: Text(
                          _saving
                              ? 'Actualizando...'
                              : 'Restablecer contraseña',
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

