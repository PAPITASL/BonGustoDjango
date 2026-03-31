// ===== Pantalla `confirm_code_screen.dart` | En esta vista se valida el codigo OTP antes de cambiar la contrasena. =====
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

// ===== Clase `ConfirmCodeScreen` | Define la pantalla donde se ingresan los digitos del codigo recibido. =====
class ConfirmCodeScreen extends StatefulWidget {
  const ConfirmCodeScreen({super.key});

  @override
  State<ConfirmCodeScreen> createState() => _ConfirmCodeScreenState();
}

// ===== Estado `_ConfirmCodeScreenState` | Maneja controladores, foco y validacion del codigo OTP. =====
class _ConfirmCodeScreenState extends State<ConfirmCodeScreen> {
  final List<TextEditingController> _otpCtrls = List.generate(
    5,
    (_) => TextEditingController(),
  ); // Controla dígitos
  final List<FocusNode> _otpNodes = List.generate(
    5,
    (_) => FocusNode(),
  ); // Controla foco

  @override
  void dispose() {
    for (final c in _otpCtrls) c.dispose();
    for (final f in _otpNodes) f.dispose();
    super.dispose();
  }

  // Cambio de foco automático
  void _onOtpChanged(int index, String value) {
    if (value.isNotEmpty && index < _otpNodes.length - 1) {
      _otpNodes[index + 1].requestFocus();
    }
    if (value.isEmpty && index > 0) {
      _otpNodes[index - 1].requestFocus();
    }
    setState(() {});
  }

  // Obtiene el codigo completo
  String get _code => _otpCtrls.map((c) => c.text).join();

  // Confirmar
  void _confirm() {
    if (_code.length == 5) {
      Navigator.pushNamed(context, '/reset');
    } else {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text('Ingresa los 5 dígitos')));
    }
  }

  // Widget burbuja
  Widget _otpBubble(int index) {
    return Container(
      width: 58,
      height: 58,
      decoration: BoxDecoration(
        color: const Color(0xFFF1DADA),
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
                    children: [
                      const Text(
                        'Código de verificación',
                        style: TextStyle(
                          fontSize: 26,
                          fontWeight: FontWeight.w900,
                        ),
                      ),
                      const SizedBox(height: 20),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                        children: List.generate(5, _otpBubble),
                      ),
                      const SizedBox(height: 28),
                      ElevatedButton(
                        onPressed: _confirm,
                        child: const Text('Confirmar'),
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
