// Pantalla donde el cliente califica comida, servicio y ambiente de su pedido.
import 'dart:async';
import 'package:flutter/material.dart';

import '../app_theme.dart';
import '../services/bongusto_api.dart';
import '../services/session_service.dart';

// Widget principal del formulario de calificacion.
class CalificacionScreen extends StatefulWidget {
  const CalificacionScreen({super.key, this.idPedido});

  final int? idPedido;

  @override
  State<CalificacionScreen> createState() => _CalificacionScreenState();
}

// Estado que administra estrellas, observaciones y envio al backend.
class _CalificacionScreenState extends State<CalificacionScreen> {
  static const Color _brandRed = Color(0xFFD90416);

  int comida = 0;
  int servicio = 0;
  int ambiente = 0;
  int? _pedidoIdCalificacion;
  bool _cargandoPedido = true;
  bool _submitting = false;
  Timer? _reintentoPedido;
  final TextEditingController observacionesController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _cargarPedidoCalificable();
  }

  Future<void> _cargarPedidoCalificable() async {
    final idUsuario = SessionService.idUsuario;
    if (idUsuario == null) {
      if (mounted) {
        setState(() => _cargandoPedido = false);
      }
      return;
    }

    try {
      final pedido = await BongustoApi.obtenerPedidoPendienteCalificacion(
        idUsuario: idUsuario,
      );
      final pedidoId = _asInt(pedido['id_pedido']);
      _pedidoIdCalificacion = pedidoId > 0 ? pedidoId : null;
    } catch (_) {
      _pedidoIdCalificacion = null;
    } finally {
      if (mounted) {
        setState(() => _cargandoPedido = false);
        if (_pedidoIdCalificacion == null) {
          _iniciarReintentoPedido();
        } else {
          _reintentoPedido?.cancel();
          _reintentoPedido = null;
        }
      }
    }
  }

  void _iniciarReintentoPedido() {
    _reintentoPedido?.cancel();
    _reintentoPedido = Timer.periodic(const Duration(seconds: 4), (timer) async {
      if (!mounted) {
        timer.cancel();
        return;
      }

      final idUsuario = SessionService.idUsuario;
      if (idUsuario == null) {
        timer.cancel();
        return;
      }

      try {
        final pedido = await BongustoApi.obtenerPedidoPendienteCalificacion(
          idUsuario: idUsuario,
        );
        final pedidoId = _asInt(pedido['id_pedido']);
        if (pedidoId > 0) {
          if (!mounted) {
            timer.cancel();
            return;
          }
          setState(() {
            _pedidoIdCalificacion = pedidoId;
            _cargandoPedido = false;
          });
          timer.cancel();
        }
      } catch (_) {
        // Se reintenta hasta que exista un pedido finalizado pendiente.
      }
    });
  }

  @override
  void dispose() {
    _reintentoPedido?.cancel();
    observacionesController.dispose();
    super.dispose();
  }

  Widget _buildStarRow(int value, ValueChanged<int> onChange) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: List.generate(
        5,
        (index) => IconButton(
          icon: Icon(
            Icons.star_rounded,
            size: 34,
            color: value > index
                ? const Color(0xFFFFC83D)
                : const Color(0xFFD8D8DD),
          ),
          onPressed: () => setState(() => onChange(index + 1)),
        ),
      ),
    );
  }

  Future<void> enviarCalificacion() async {
    final idUsuario = SessionService.idUsuario;
    if (idUsuario == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Debes iniciar sesion para calificar.')),
      );
      return;
    }

    if (comida == 0 || servicio == 0 || ambiente == 0) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Por favor completa todas las calificaciones.'),
        ),
      );
      return;
    }

    if (_pedidoIdCalificacion == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('No hay un pedido finalizado pendiente por calificar.'),
        ),
      );
      return;
    }

    setState(() => _submitting = true);

    try {
      await BongustoApi.enviarCalificacion(
        idUsuario: idUsuario,
        idPedido: _pedidoIdCalificacion,
        calificacionComida: comida,
        calificacionServicio: servicio,
        calificacionAmbiente: ambiente,
        observaciones: observacionesController.text.trim(),
      );

      if (!mounted) {
        return;
      }

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Gracias por tu calificacion.')),
      );

      _pedidoIdCalificacion = null;
      Navigator.pushNamedAndRemoveUntil(context, '/home', (route) => false);
    } catch (e) {
      if (!mounted) {
        return;
      }
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('No se pudo enviar la calificacion: $e')),
      );
    } finally {
      if (mounted) {
        setState(() => _submitting = false);
      }
    }
  }

  int _asInt(dynamic value) {
    if (value is int) return value;
    return int.tryParse('$value') ?? 0;
  }

  Widget _questionBlock({
    required String title,
    required int value,
    required ValueChanged<int> onChange,
  }) {
    return Container(
      margin: const EdgeInsets.only(bottom: 20),
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: AppThemeColors.surface,
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: AppThemeColors.line),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.w700,
              color: AppThemeColors.text,
            ),
          ),
          const SizedBox(height: 12),
          _buildStarRow(value, onChange),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppThemeColors.bg,
      appBar: AppBar(
        title: Text('Queremos saber tu opinion'),
        backgroundColor: AppThemeColors.surface,
        foregroundColor: AppThemeColors.text,
        elevation: 0,
      ),
      body: SafeArea(
        child: _cargandoPedido
            ? const Center(
                child: CircularProgressIndicator(
                  color: _brandRed,
                ),
              )
            : SingleChildScrollView(
                padding: const EdgeInsets.all(20),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
              Text(
                'Califica tu experiencia en Santa Juana',
                style: TextStyle(
                  fontSize: 28,
                  fontWeight: FontWeight.w800,
                  color: AppThemeColors.text,
                ),
              ),
              const SizedBox(height: 10),
              Text(
                'Tu opinion se guarda en BonGusto Django y ayuda a medir comida, servicio y ambiente del restaurante.',
                style: TextStyle(
                  fontSize: 15,
                  height: 1.6,
                  color: AppThemeColors.muted,
                ),
              ),
              const SizedBox(height: 24),
              if (_pedidoIdCalificacion == null)
                Container(
                  width: double.infinity,
                  margin: const EdgeInsets.only(bottom: 20),
                  padding: const EdgeInsets.all(18),
                  decoration: BoxDecoration(
                    color: AppThemeColors.surface,
                    borderRadius: BorderRadius.circular(24),
                    border: Border.all(color: AppThemeColors.line),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Esperando confirmacion del pedido',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w700,
                          color: AppThemeColors.text,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        'La calificacion se habilitara cuando el pedido quede finalizado y pendiente de calificar.',
                        style: TextStyle(
                          fontSize: 14,
                          height: 1.5,
                          color: AppThemeColors.muted,
                        ),
                      ),
                      const SizedBox(height: 12),
                      ElevatedButton(
                        onPressed: () => _cargarPedidoCalificable(),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: _brandRed,
                          foregroundColor: Colors.white,
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(16),
                          ),
                        ),
                        child: const Text('Reintentar'),
                      ),
                    ],
                  ),
                ),
              _questionBlock(
                title: 'Como calificarias la calidad de la comida?',
                value: comida,
                onChange: (val) => comida = val,
              ),
              _questionBlock(
                title: 'Que tan satisfecho estas con la atencion del personal?',
                value: servicio,
                onChange: (val) => servicio = val,
              ),
              _questionBlock(
                title:
                    'Como valorarias el ambiente y la comodidad del restaurante?',
                value: ambiente,
                onChange: (val) => ambiente = val,
              ),
              Container(
                padding: const EdgeInsets.all(18),
                decoration: BoxDecoration(
                  color: AppThemeColors.surface,
                  borderRadius: BorderRadius.circular(24),
                  border: Border.all(color: AppThemeColors.line),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Observaciones',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w700,
                        color: AppThemeColors.text,
                      ),
                    ),
                    const SizedBox(height: 12),
                    TextField(
                      controller: observacionesController,
                      maxLines: 4,
                      decoration: InputDecoration(
                        hintText: 'Escribe aqui tus comentarios...',
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(18),
                          borderSide: BorderSide(color: AppThemeColors.line),
                        ),
                        enabledBorder: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(18),
                          borderSide: BorderSide(color: AppThemeColors.line),
                        ),
                        focusedBorder: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(18),
                          borderSide: BorderSide(color: _brandRed),
                        ),
                        filled: true,
                        fillColor: AppThemeColors.surfaceAlt,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 28),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: _brandRed,
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(18),
                    ),
                  ),
                  onPressed: (_submitting || _pedidoIdCalificacion == null)
                      ? null
                      : enviarCalificacion,
                  child: _submitting
                      ? const SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                            color: Colors.white,
                          ),
                        )
                      : Text(
                          'Enviar calificacion',
                          style: TextStyle(
                            fontSize: 17,
                            fontWeight: FontWeight.w700,
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
