// Pantalla que muestra el carrito actual y permite continuar al pedido.
import 'dart:async';

import 'package:flutter/material.dart';

import '../app_theme.dart';
import 'carrito_global.dart';
import 'opciones_pedido_screen.dart';
import '../services/session_service.dart';

// Widget principal de la vista del carrito.
class CarritoPage extends StatefulWidget {
  const CarritoPage({super.key});

  @override
  State<CarritoPage> createState() => _CarritoPageState();
}

// Estado que controla cantidades, eliminacion y total visual del carrito.
class _CarritoPageState extends State<CarritoPage> {
  static Color get _bg => AppThemeColors.bg;
  static Color get _card => AppThemeColors.surface;
  static Color get _ink => AppThemeColors.text;
  static Color get _muted => AppThemeColors.muted;
  static const _accent = Color(0xFFD90416);
  static Color get _line => AppThemeColors.line;

  void _showNotice(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        behavior: SnackBarBehavior.floating,
        backgroundColor: _card,
        elevation: 10,
        margin: const EdgeInsets.fromLTRB(16, 0, 16, 100),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final productos = CarritoGlobal.productos;
    final total = CarritoGlobal.calcularTotal();

    return Scaffold(
      backgroundColor: _bg,
      appBar: AppBar(
        title: Text('Carrito', style: TextStyle(fontWeight: FontWeight.w800)),
        backgroundColor: _bg,
        foregroundColor: _ink,
        elevation: 0,
      ),
      body: productos.isEmpty
          ? Center(
              child: Text(
                'Tu carrito esta vacio',
                style: TextStyle(fontSize: 18),
              ),
            )
          : Column(
              children: [
                Expanded(
                  child: ListView.builder(
                    padding: const EdgeInsets.fromLTRB(16, 8, 16, 12),
                    itemCount: productos.length,
                    itemBuilder: (context, index) {
                      final p = productos[index];
                      return Container(
                        margin: const EdgeInsets.only(bottom: 12),
                        padding: const EdgeInsets.all(14),
                        decoration: BoxDecoration(
                          color: _card,
                          borderRadius: BorderRadius.circular(22),
                          border: Border.all(color: _line),
                        ),
                        child: Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            ClipRRect(
                              borderRadius: BorderRadius.circular(16),
                              child: Image.asset(
                                p.imagen,
                                width: 78,
                                height: 78,
                                fit: BoxFit.cover,
                                errorBuilder: (context, error, stackTrace) =>
                                    const SizedBox(
                                      width: 78,
                                      height: 78,
                                      child: Icon(Icons.image_not_supported),
                                    ),
                              ),
                            ),
                            const SizedBox(width: 14),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    p.nombre,
                                    style: TextStyle(
                                      color: _ink,
                                      fontSize: 18,
                                      fontWeight: FontWeight.w800,
                                    ),
                                  ),
                                  const SizedBox(height: 6),
                                  Text(
                                    '\$${p.precio.toStringAsFixed(0)}',
                                    style: TextStyle(
                                      color: _ink,
                                      fontSize: 16,
                                      fontWeight: FontWeight.w700,
                                    ),
                                  ),
                                  const SizedBox(height: 4),
                                  Text(
                                    'Cantidad: ${p.cantidad}',
                                    style: TextStyle(
                                      color: _muted,
                                      fontSize: 14,
                                    ),
                                  ),
                                  const SizedBox(height: 12),
                                  Row(
                                    children: [
                                      _qtyButton(
                                        icon: Icons.remove,
                                        onTap: () {
                                          setState(() {
                                            if (p.cantidad > 1) {
                                              CarritoGlobal.cambiarCantidadEn(
                                                index,
                                                p.cantidad - 1,
                                              );
                                            } else {
                                              CarritoGlobal.eliminarProductoEn(
                                                index,
                                              );
                                            }
                                          });
                                          unawaited(CarritoGlobal.sincronizarConBackend());
                                        },
                                      ),
                                      Padding(
                                        padding: const EdgeInsets.symmetric(
                                          horizontal: 10,
                                        ),
                                        child: Text(
                                          '${p.cantidad}',
                                          style: TextStyle(
                                            color: _ink,
                                            fontWeight: FontWeight.w800,
                                          ),
                                        ),
                                      ),
                                      _qtyButton(
                                        icon: Icons.add,
                                        onTap: () {
                                          setState(() {
                                            CarritoGlobal.cambiarCantidadEn(
                                              index,
                                              p.cantidad + 1,
                                            );
                                          });
                                          unawaited(CarritoGlobal.sincronizarConBackend());
                                        },
                                      ),
                                      const Spacer(),
                                      IconButton(
                                        icon: Icon(
                                          Icons.delete_outline,
                                          color: _accent,
                                        ),
                                        onPressed: () {
                                          final nombre = p.nombre;
                                          setState(() {
                                            CarritoGlobal.eliminarProductoEn(
                                              index,
                                            );
                                          });
                                          unawaited(CarritoGlobal.sincronizarConBackend());
                                          _showNotice(
                                            '$nombre eliminado del pedido',
                                          );
                                        },
                                      ),
                                    ],
                                  ),
                                ],
                              ),
                            ),
                          ],
                        ),
                      );
                    },
                  ),
                ),
                SafeArea(
                  top: false,
                  child: Container(
                    margin: const EdgeInsets.fromLTRB(16, 0, 16, 16),
                    padding: const EdgeInsets.all(18),
                    decoration: BoxDecoration(
                      color: _card,
                      borderRadius: BorderRadius.circular(24),
                      border: Border.all(color: _line),
                      boxShadow: [
                        BoxShadow(
                          color: Colors.black.withValues(alpha: 0.05),
                          blurRadius: 18,
                          offset: const Offset(0, 6),
                        ),
                      ],
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        Text(
                          'Total: \$${total.toStringAsFixed(0)}',
                          style: TextStyle(
                            color: _ink,
                            fontSize: 24,
                            fontWeight: FontWeight.w900,
                          ),
                          textAlign: TextAlign.right,
                        ),
                        const SizedBox(height: 14),
                        SizedBox(
                          height: 56,
                          child: ElevatedButton(
                            style: ElevatedButton.styleFrom(
                              backgroundColor: _accent,
                              foregroundColor: Colors.white,
                              elevation: 0,
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(18),
                              ),
                            ),
                            onPressed: () async {
                              try {
                                if (SessionService.tipoPedido == 'para_llevar') {
                                  await CarritoGlobal.confirmarPedidoActual();
                                }
                              } catch (e) {
                                if (!mounted) return;
                                _showNotice('$e');
                                return;
                              }
                              await Navigator.push(
                                context,
                                MaterialPageRoute(
                                  builder: (context) =>
                                      const OpcionesPedidoScreen(),
                                ),
                              );
                              if (mounted) {
                                setState(() {});
                              }
                            },
                            child: Text('Pedir'),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            ),
    );
  }

  Widget _qtyButton({required IconData icon, required VoidCallback onTap}) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(12),
      child: Container(
        width: 34,
        height: 34,
        decoration: BoxDecoration(
          color: const Color(0xFFF8F8FA),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: _line),
        ),
        child: Icon(icon, size: 18, color: _ink),
      ),
    );
  }
}
