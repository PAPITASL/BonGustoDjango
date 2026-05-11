// Pantalla donde el cliente informa como desea pagar; BonGusto no procesa dinero.
import 'package:flutter/material.dart';

import '../app_theme.dart';
import '../services/bongusto_api.dart';
import '../services/session_service.dart';
import 'calificacion_screen.dart';
import 'carrito_global.dart';

class MetodoPagoPage extends StatefulWidget {
  const MetodoPagoPage({super.key});

  @override
  State<MetodoPagoPage> createState() => _MetodoPagoPageState();
}

class _MetodoPagoPageState extends State<MetodoPagoPage> {
  bool _submitting = false;
  String _metodoSeleccionado = '';

  static Color get _pageBg => AppThemeColors.bg;
  static Color get _card => AppThemeColors.surface;
  static Color get _ink => AppThemeColors.text;
  static Color get _muted => AppThemeColors.muted;
  static Color get _line => AppThemeColors.line;
  static const _accent = Color(0xFFD90416);

  Future<void> _solicitarPago(String metodo) async {
    final idUsuario = SessionService.idUsuario;
    final tipoPedido = SessionService.tipoPedido.trim().toLowerCase();

    if (idUsuario == null) {
      _notice('Debes iniciar sesion para solicitar el pago.');
      return;
    }

    if (tipoPedido != 'para_llevar' && SessionService.mesaId == null) {
      _notice('Primero debes tener una mesa asignada.');
      return;
    }

    final mesaEstado = SessionService.mesaEstado.trim().toLowerCase();
    if (mesaEstado == 'bloqueada') {
      _notice('Tu mesa ya no esta disponible. Confirma una mesa valida antes de pedir la cuenta.');
      return;
    }

    if (CarritoGlobal.productos.isEmpty) {
      _notice('Agrega productos antes de solicitar la cuenta.');
      return;
    }

    setState(() {
      _submitting = true;
      _metodoSeleccionado = metodo;
    });

    try {
      final pedidoId = await _obtenerOCrearPedido(idUsuario);
      await BongustoApi.solicitarPago(
        metodoPago: metodo,
        idPedido: pedidoId == 0 ? null : pedidoId,
        mesaId: tipoPedido == 'para_llevar' ? null : SessionService.mesaId,
      );

      if (!mounted) return;
      CarritoGlobal.vaciarCarrito();
      await _mostrarConfirmacion(metodo, pedidoId);
    } catch (e) {
      if (!mounted) return;
      _notice('No se pudo enviar la solicitud de pago: $e');
    } finally {
      if (mounted) {
        setState(() => _submitting = false);
      }
    }
  }

  Future<int> _obtenerOCrearPedido(int idUsuario) async {
    final pedidos = await BongustoApi.obtenerPedidosUsuario(idUsuario);
    final tipoPedido = SessionService.tipoPedido.trim().toLowerCase();
    final mesaActual = SessionService.mesaId;
    if (tipoPedido == 'para_llevar') {
      final pedidoLlevar = pedidos.firstWhere(
        (pedido) {
          final estado = (pedido['estado'] ?? '').toString().trim().toLowerCase();
          final tipo = (pedido['tipo_pedido'] ?? '').toString().trim().toLowerCase();
          final mesaIdPedido = _asInt(pedido['mesa_id']);
          return tipo == 'para_llevar' && estado != 'finalizado' && mesaIdPedido == 0;
        },
        orElse: () => const <String, dynamic>{},
      );
      final pedidoIdActual = _asInt(pedidoLlevar['id_pedido']);
      if (pedidoIdActual > 0) {
        return pedidoIdActual;
      }
      final total = CarritoGlobal.calcularTotal();
      final pedido = await BongustoApi.crearPedido(
        idUsuario: idUsuario,
        totalPedido: total,
        items: CarritoGlobal.productos.map((p) => p.toPedidoItem()).toList(),
        tipoPedido: 'para_llevar',
        mesaId: null,
      );
      return _asInt(pedido['id_pedido']);
    }

    final pedidoMesaActual = pedidos.firstWhere(
      (pedido) {
        final estado = (pedido['estado'] ?? '').toString().trim().toLowerCase();
        final mesaIdPedido = _asInt(pedido['mesa_id']);
        final tipo = (pedido['tipo_pedido'] ?? '').toString().trim().toLowerCase();
        return mesaIdPedido == mesaActual && estado != 'finalizado' && tipo != 'para_llevar';
      },
      orElse: () => const <String, dynamic>{},
    );
    final pedidoIdActual = _asInt(pedidoMesaActual['id_pedido']);
    if (pedidoIdActual > 0) {
      return pedidoIdActual;
    }

    final total = CarritoGlobal.calcularTotal();
    final pedido = await BongustoApi.crearPedido(
      idUsuario: idUsuario,
      totalPedido: total,
      items: CarritoGlobal.productos.map((p) => p.toPedidoItem()).toList(),
      tipoPedido: 'restaurante',
      mesaId: mesaActual,
    );
    return _asInt(pedido['id_pedido']);
  }

  int _asInt(dynamic value) {
    if (value is int) return value;
    return int.tryParse('$value') ?? 0;
  }

  void _notice(String text) {
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(text)));
  }

  Future<void> _mostrarConfirmacion(String metodo, int pedidoId) async {
    await showDialog<void>(
      context: context,
      barrierDismissible: false,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(24)),
        title: const Text('Solicitud enviada'),
        content: Text(
          _mensajeConfirmacion(metodo),
          style: const TextStyle(height: 1.45),
        ),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              Navigator.pushReplacement(
                context,
                MaterialPageRoute(
                builder: (_) => CalificacionScreen(
                    idPedido: pedidoId == 0 ? null : pedidoId,
                  ),
                ),
              );
            },
            child: const Text('Entendido'),
          ),
        ],
      ),
    );
  }

  String _mensajeConfirmacion(String metodo) {
    if (metodo == 'tarjeta_datafono') {
      return 'Tu solicitud de pago fue enviada al mesero. Se acercara a tu mesa con el datafono y la factura.';
    }
    if (metodo == 'efectivo') {
      return 'Tu solicitud de pago fue enviada al mesero. Se acercara con la factura para recibir el pago en efectivo.';
    }
    return 'Tu solicitud de pago fue enviada al mesero. Se acercara para confirmar el metodo de pago y cerrar la cuenta.';
  }

  @override
  Widget build(BuildContext context) {
    final total = CarritoGlobal.calcularTotal();
    final tipoPedido = SessionService.tipoPedido.trim().toLowerCase();
    final mesaLabel = tipoPedido == 'para_llevar'
        ? 'Pedido para llevar'
        : (SessionService.mesaLabel.trim().isEmpty
              ? 'Mesa ${SessionService.mesaNumero ?? SessionService.mesaId ?? '-'}'
              : SessionService.mesaLabel);

    return Scaffold(
      backgroundColor: _pageBg,
      appBar: AppBar(
        backgroundColor: _pageBg,
        foregroundColor: _ink,
        title: const Text(
          'Solicitar cuenta',
          style: TextStyle(fontWeight: FontWeight.w800),
        ),
      ),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.fromLTRB(20, 8, 20, 28),
          children: [
            Container(
              padding: const EdgeInsets.all(22),
              decoration: BoxDecoration(
                color: _card,
                borderRadius: BorderRadius.circular(28),
                border: Border.all(color: _line),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'CUENTA',
                    style: TextStyle(
                      color: _accent,
                      fontSize: 12,
                      letterSpacing: 3,
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Elige como quieres pagar',
                    style: TextStyle(
                      color: _ink,
                      fontSize: 32,
                      height: 1.05,
                      fontWeight: FontWeight.w900,
                    ),
                  ),
                  const SizedBox(height: 12),
                  Text(
                    tipoPedido == 'para_llevar'
                        ? 'BonGusto no procesa pagos en la app. Solo avisamos al mesero tu metodo preferido para agilizar la entrega del pedido.'
                        : 'BonGusto no procesa pagos en la app. Solo avisamos al mesero tu metodo preferido para agilizar la atencion en mesa.',
                    style: TextStyle(color: _muted, fontSize: 14, height: 1.5),
                  ),
                  const SizedBox(height: 18),
                  Row(
                    children: [
                      Expanded(child: _summary('Mesa', mesaLabel)),
                      const SizedBox(width: 10),
                      Expanded(
                        child: _summary(
                          'Total',
                          '\$${total.toStringAsFixed(0)}',
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            const SizedBox(height: 18),
            _methodButton(
              value: 'tarjeta_datafono',
              title: 'Tarjeta / datafono',
              subtitle: 'El mesero llega con el datafono a tu mesa.',
              icon: Icons.credit_card_rounded,
            ),
            const SizedBox(height: 12),
            _methodButton(
              value: 'efectivo',
              title: 'Efectivo',
              subtitle: 'El mesero lleva la factura para recibir efectivo.',
              icon: Icons.payments_rounded,
            ),
            const SizedBox(height: 12),
            _methodButton(
              value: 'otro_metodo',
              title: 'Otro metodo de pago',
              subtitle: 'El mesero confirma contigo como cerrar la cuenta.',
              icon: Icons.more_horiz_rounded,
            ),
          ],
        ),
      ),
    );
  }

  Widget _summary(String label, String value) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: const Color(0xFFF8F8FA),
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: _line),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(label, style: TextStyle(color: _muted, fontSize: 12)),
          const SizedBox(height: 4),
          Text(
            value,
            style: TextStyle(color: _ink, fontWeight: FontWeight.w900),
          ),
        ],
      ),
    );
  }

  Widget _methodButton({
    required String value,
    required String title,
    required String subtitle,
    required IconData icon,
  }) {
    final active = _metodoSeleccionado == value && _submitting;
    return InkWell(
      onTap: _submitting ? null : () => _solicitarPago(value),
      borderRadius: BorderRadius.circular(24),
      child: Container(
        padding: const EdgeInsets.all(18),
        decoration: BoxDecoration(
          color: _card,
          borderRadius: BorderRadius.circular(24),
          border: Border.all(color: active ? _accent : _line, width: 1.4),
        ),
        child: Row(
          children: [
            Container(
              width: 58,
              height: 58,
              decoration: BoxDecoration(
                color: const Color(0xFFFFECEE),
                borderRadius: BorderRadius.circular(18),
              ),
              child: active
                  ? const Padding(
                      padding: EdgeInsets.all(16),
                      child: CircularProgressIndicator(
                        strokeWidth: 2.4,
                        color: _accent,
                      ),
                    )
                  : Icon(icon, color: _accent, size: 30),
            ),
            const SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: TextStyle(
                      color: _ink,
                      fontSize: 18,
                      fontWeight: FontWeight.w900,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    subtitle,
                    style: TextStyle(color: _muted, height: 1.35),
                  ),
                ],
              ),
            ),
            Icon(Icons.arrow_forward_rounded, color: _ink),
          ],
        ),
      ),
    );
  }
}
