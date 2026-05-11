import 'package:flutter/material.dart';

import '../app_theme.dart';
import '../services/bongusto_api.dart';
import '../utils/password_rules.dart';
import 'app_settings_controls.dart';

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

    if (!PasswordRules.isStrong(p1)) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text(PasswordRules.helpText)));
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
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('$e')));
    } finally {
      if (mounted) {
        setState(() => _saving = false);
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
              Padding(
                padding: EdgeInsets.only(left: 4, bottom: 12),
                child: Text(
                  'Cambiar contraseña',
                  style: TextStyle(
                    fontSize: 20,
                    color: AppThemeColors.muted,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
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
                        'Restablecer contraseña',
                        style: TextStyle(
                          color: AppThemeColors.text,
                          fontSize: 28,
                          height: 1.1,
                          letterSpacing: -0.2,
                          fontWeight: FontWeight.w900,
                        ),
                      ),
                      const SizedBox(height: 6),
                      Text(
                        'Escribe una contraseña segura para volver a entrar a tu cuenta.',
                        style: TextStyle(
                          fontSize: 14,
                          color: AppThemeColors.muted,
                        ),
                      ),
                      const SizedBox(height: 22),
                      Text(
                        'Nueva contraseña',
                        style: TextStyle(
                          fontSize: 14,
                          color: AppThemeColors.text,
                        ),
                      ),
                      const SizedBox(height: 6),
                      TextField(
                        controller: _pass1Ctrl,
                        obscureText: _obscure1,
                        decoration: InputDecoration(
                          hintText: 'Crear nueva contraseña',
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
                      const SizedBox(height: 6),
                      Align(
                        alignment: Alignment.centerLeft,
                        child: Text(
                          PasswordRules.helpText,
                          style: TextStyle(
                            fontSize: 12,
                            color: AppThemeColors.muted,
                          ),
                        ),
                      ),
                      const SizedBox(height: 16),
                      Text(
                        'Confirmar nueva contraseña',
                        style: TextStyle(
                          fontSize: 14,
                          color: AppThemeColors.text,
                        ),
                      ),
                      const SizedBox(height: 6),
                      TextField(
                        controller: _pass2Ctrl,
                        obscureText: _obscure2,
                        decoration: InputDecoration(
                          hintText: 'Repetir contraseña',
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
                      const SizedBox(height: 22),
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
