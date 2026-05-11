import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

class ConfirmCodeScreen extends StatefulWidget {
  const ConfirmCodeScreen({super.key});

  @override
  State<ConfirmCodeScreen> createState() => _ConfirmCodeScreenState();
}

class _ConfirmCodeScreenState extends State<ConfirmCodeScreen> {
  final List<TextEditingController> _otpCtrls =
      List.generate(6, (_) => TextEditingController());
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
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Ingresa los 6 dígitos')),
      );
    }
  }

  Widget _otpBubble(int index) {
    return Container(
      width: 48,
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
    final isDark = Theme.of(context).brightness == Brightness.dark;
    const cardText = Color(0xFF181818);
    final args =
        (ModalRoute.of(context)?.settings.arguments as Map?) ?? const {};
    final correo = (args['correo'] ?? '').toString();

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
                    children: [
                      const Text(
                        'Código de verificación',
                        style: TextStyle(
                          color: cardText,
                          fontSize: 26,
                          fontWeight: FontWeight.w900,
                        ),
                      ),
                      const SizedBox(height: 10),
                      Text(
                        correo,
                        style: const TextStyle(color: Colors.black54),
                      ),
                      const SizedBox(height: 20),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                        children: List.generate(6, _otpBubble),
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

