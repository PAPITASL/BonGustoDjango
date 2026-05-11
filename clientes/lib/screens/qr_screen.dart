// Pantalla para escanear o escribir el codigo QR del restaurante.
import 'package:flutter/material.dart';
import 'package:mobile_scanner/mobile_scanner.dart';

import '../app_theme.dart';
import '../services/bongusto_api.dart';
import '../services/session_service.dart';
import 'menu_screen.dart';

// Widget principal del acceso por QR.
class QRScreen extends StatefulWidget {
  const QRScreen({super.key});

  @override
  State<QRScreen> createState() => _QRScreenState();
}

// Estado que administra el scanner y la validacion del codigo permitido.
class _QRScreenState extends State<QRScreen> {
  static const kBrandRed = Color(0xFFD90416);
  static Color get kPageBg => AppThemeColors.bg;
  static Color get kSurface => AppThemeColors.surface;
  static Color get kText => AppThemeColors.text;
  static Color get kMuted => AppThemeColors.muted;
  static Color get kLine => AppThemeColors.line;

  final TextEditingController _codeController = TextEditingController();
  final MobileScannerController _scannerController = MobileScannerController(
    detectionSpeed: DetectionSpeed.noDuplicates,
  );

  bool _isProcessing = false;
  bool _torchEnabled = false;

  @override
  void initState() {
    super.initState();
    _codeController.text = '';
  }

  @override
  void dispose() {
    _codeController.dispose();
    _scannerController.dispose();
    super.dispose();
  }

  void _goToMenu() {
    Navigator.pushReplacement(
      context,
      MaterialPageRoute(builder: (_) => const MenuScreen()),
    );
  }

  int? _resolverNumeroMesa(String code) {
    final clean = code.trim().toLowerCase();
    if (clean.isEmpty) return null;
    final directo = int.tryParse(clean);
    if (directo != null && directo > 0) {
      return directo;
    }
    final match = RegExp(r'(\d+)').firstMatch(clean);
    final numero = int.tryParse(match?.group(1) ?? '');
    if (numero == null || numero <= 0) {
      return null;
    }
    return numero;
  }

  Future<void> _asegurarMesaAsignada(String code) async {
    final idUsuario = SessionService.idUsuario;
    if (idUsuario == null) {
      return;
    }

    final numeroMesa = _resolverNumeroMesa(code);
    if (numeroMesa == null) {
      throw Exception('El codigo no corresponde a una mesa valida.');
    }

    final mesa = await BongustoApi.asignarMesa(
      idUsuario: idUsuario,
      numeroMesa: numeroMesa,
      codigoMesa: code,
    );
    await SessionService.guardarMesa(mesa);
    await SessionService.actualizarSesion({
      'tipo_pedido': 'restaurante',
    });
  }

  Future<void> _handleCode(String? code) async {
    final scannedCode = (code?.trim() ?? '').toLowerCase();
    if (scannedCode.isEmpty || _isProcessing) return;

    final numeroMesa = _resolverNumeroMesa(scannedCode);
    if (numeroMesa == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Codigo invalido. Debe incluir un numero de mesa valido.'),
        ),
      );
      return;
    }

    setState(() {
      _isProcessing = true;
      _codeController.text = scannedCode;
    });

    await _scannerController.stop();

    try {
      await _asegurarMesaAsignada(scannedCode);
    } catch (e) {
      if (!mounted) return;
      setState(() => _isProcessing = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('$e')),
      );
      return;
    }

    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          SessionService.mesaLabel.trim().isNotEmpty
              ? 'Codigo detectado: $scannedCode. Tu mesa es ${SessionService.mesaLabel}.'
              : SessionService.mesaId != null
              ? 'Codigo detectado: $scannedCode. Tu mesa es la ${SessionService.mesaNumero ?? SessionService.mesaId}.'
              : 'Codigo detectado: $scannedCode. Mesa $numeroMesa confirmada.',
        ),
      ),
    );
    _goToMenu();
  }

  @override
  Widget build(BuildContext context) {
    final keyboardInset = MediaQuery.of(context).viewInsets.bottom;

    return Scaffold(
      backgroundColor: kPageBg,
      resizeToAvoidBottomInset: true,
      appBar: AppBar(
        title: Text(
          'Escanea Codigo',
          style: TextStyle(fontWeight: FontWeight.w800),
        ),
        backgroundColor: kPageBg,
        elevation: 0,
        foregroundColor: kText,
        actions: [
          IconButton(
            onPressed: () async {
              await _scannerController.toggleTorch();
              if (!mounted) return;
              setState(() => _torchEnabled = !_torchEnabled);
            },
            icon: Icon(_torchEnabled ? Icons.flash_on : Icons.flash_off),
          ),
        ],
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: EdgeInsets.fromLTRB(20, 12, 20, 24 + keyboardInset),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Container(
                padding: const EdgeInsets.fromLTRB(20, 22, 20, 22),
                decoration: BoxDecoration(
                  color: kSurface,
                  borderRadius: BorderRadius.circular(28),
                  border: Border.all(color: kLine),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withValues(alpha: 0.05),
                      blurRadius: 18,
                      offset: const Offset(0, 8),
                    ),
                  ],
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Text(
                      'ACCESO AL MENU',
                      textAlign: TextAlign.center,
                      style: TextStyle(
                        color: kBrandRed,
                        fontSize: 12,
                        fontWeight: FontWeight.w800,
                        letterSpacing: 2.8,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'Escanea el codigo QR',
                      textAlign: TextAlign.center,
                      style: TextStyle(
                        color: kText,
                        fontSize: 28,
                        height: 1.1,
                        fontWeight: FontWeight.w900,
                      ),
                    ),
                    const SizedBox(height: 10),
                    Text(
                      'Enfoca el codigo de tu mesa o ingresa el codigo manualmente para abrir la carta.',
                      textAlign: TextAlign.center,
                      style: TextStyle(
                        color: kMuted,
                        fontSize: 14,
                        height: 1.5,
                      ),
                    ),
                    const SizedBox(height: 22),
                    Container(
                      decoration: BoxDecoration(
                        color: Colors.black,
                        borderRadius: BorderRadius.circular(26),
                        border: Border.all(color: kLine),
                      ),
                      child: ClipRRect(
                        borderRadius: BorderRadius.circular(26),
                        child: AspectRatio(
                          aspectRatio: 1,
                          child: Stack(
                            fit: StackFit.expand,
                            children: [
                              MobileScanner(
                                controller: _scannerController,
                                onDetect: (capture) {
                                  if (capture.barcodes.isEmpty) return;
                                  _handleCode(capture.barcodes.first.rawValue);
                                },
                              ),
                              IgnorePointer(
                                child: Center(
                                  child: Container(
                                    width: 210,
                                    height: 210,
                                    decoration: BoxDecoration(
                                      borderRadius: BorderRadius.circular(28),
                                      border: Border.all(
                                        color: Colors.white,
                                        width: 2.5,
                                      ),
                                      boxShadow: [
                                        BoxShadow(
                                          color: Colors.black.withValues(
                                            alpha: 0.12,
                                          ),
                                          blurRadius: 12,
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
                    ),
                    const SizedBox(height: 20),
                    Text(
                      'Codigo manual',
                      style: TextStyle(
                        color: kText,
                        fontSize: 15,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                    const SizedBox(height: 8),
                    TextField(
                      controller: _codeController,
                      textAlign: TextAlign.center,
                      decoration: InputDecoration(
                        hintText:
                            'Ingresa el codigo de la mesa, por ejemplo mesa-3 o 3',
                        hintStyle: TextStyle(color: kMuted),
                        filled: true,
                        fillColor: const Color(0xFFF8F8FA),
                        contentPadding: const EdgeInsets.symmetric(
                          horizontal: 16,
                          vertical: 16,
                        ),
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(18),
                          borderSide: BorderSide(color: kLine),
                        ),
                        enabledBorder: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(18),
                          borderSide: BorderSide(color: kLine),
                        ),
                        focusedBorder: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(18),
                          borderSide: BorderSide(color: kBrandRed),
                        ),
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'El codigo debe incluir el numero real de la mesa.',
                      textAlign: TextAlign.center,
                      style: TextStyle(
                        color: kMuted,
                        fontSize: 13,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    const SizedBox(height: 18),
                    SizedBox(
                      height: 54,
                      child: ElevatedButton(
                        style: ElevatedButton.styleFrom(
                          elevation: 0,
                          backgroundColor: kBrandRed,
                          foregroundColor: Colors.white,
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(18),
                          ),
                        ),
                        onPressed: () {
                          if (_codeController.text.trim().isNotEmpty) {
                            _handleCode(_codeController.text);
                          } else {
                            ScaffoldMessenger.of(context).showSnackBar(
                              const SnackBar(
                                content: Text('Por favor ingresa un codigo'),
                              ),
                            );
                          }
                        },
                        child: Text(
                          'Continuar al menu',
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.w700,
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
