import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../app_theme.dart';
import 'app_settings_controls.dart';

class ConfirmCodeScreen extends StatefulWidget {
  const ConfirmCodeScreen({super.key});

  @override
  State<ConfirmCodeScreen> createState() => _ConfirmCodeScreenState();
}

class _ConfirmCodeScreenState extends State<ConfirmCodeScreen> {
  final List<TextEditingController> _otpCtrls = List.generate(
    6,
    (_) => TextEditingController(),
  );
  final List<FocusNode> _otpNodes = List.generate(6, (_) => FocusNode());

  @override
  void dispose() {
    for (final c in _otpCtrls) {
      c.dispose();
    }
    for (final f in _otpNodes) {
      f.dispose();
    }
    super.dispose();
  }

  void _onOtpChanged(int index, String value) {
    if (value.isNotEmpty && index < _otpNodes.length - 1) {
      _otpNodes[index + 1].requestFocus();
    }
    if (value.isEmpty && index > 0) {
      _otpNodes[index - 1].requestFocus();
    }
    setState(() {});
  }

  String get _code => _otpCtrls.map((c) => c.text).join();

  void _confirm() {
    final args =
        (ModalRoute.of(context)?.settings.arguments as Map?) ?? const {};
    final correo = (args['correo'] ?? '').toString();

    if (correo.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Primero solicita el código por correo')),
      );
      return;
    }

    if (_code.length == 6) {
      Navigator.pushNamed(
        context,
        '/reset',
        arguments: {'correo': correo, 'codigo': _code},
      );
    } else {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text('Ingresa los 6 dígitos')));
    }
  }

  Widget _otpBubble(int index) {
    return Container(
      width: 48,
      height: 58,
      decoration: BoxDecoration(
        color: AppThemeColors.accentSoft,
        borderRadius: BorderRadius.circular(18),
      ),
      alignment: Alignment.center,
      child: TextField(
        controller: _otpCtrls[index],
        focusNode: _otpNodes[index],
        textAlign: TextAlign.center,
        keyboardType: TextInputType.number,
        maxLength: 1,
        inputFormatters: [FilteringTextInputFormatter.digitsOnly],
        decoration: const InputDecoration(
          counterText: '',
          border: InputBorder.none,
        ),
        style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w600),
        onChanged: (v) => _onOtpChanged(index, v),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final args =
        (ModalRoute.of(context)?.settings.arguments as Map?) ?? const {};
    final correo = (args['correo'] ?? '').toString();

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
                  'Confirmación',
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
                  padding: const EdgeInsets.fromLTRB(22, 22, 22, 22),
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
                      Center(
                        child: Text(
                          'Código',
                          style: TextStyle(
                            color: AppThemeColors.text,
                            fontSize: 28,
                            height: 1.1,
                            letterSpacing: -0.2,
                            fontWeight: FontWeight.w900,
                          ),
                        ),
                      ),
                      const SizedBox(height: 10),
                      Center(
                        child: Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 14,
                            vertical: 8,
                          ),
                          decoration: BoxDecoration(
                            color: AppThemeColors.surfaceAlt,
                            borderRadius: BorderRadius.circular(24),
                          ),
                          child: Text(
                            correo,
                            style: TextStyle(
                              fontSize: 14,
                              color: AppThemeColors.text,
                              letterSpacing: 0.2,
                            ),
                          ),
                        ),
                      ),
                      const SizedBox(height: 22),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                        children: List.generate(6, _otpBubble),
                      ),
                      const SizedBox(height: 28),
                      Center(
                        child: SizedBox(
                          width: 240,
                          child: ElevatedButton(
                            onPressed: _confirm,
                            child: const Text('Confirmar'),
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
