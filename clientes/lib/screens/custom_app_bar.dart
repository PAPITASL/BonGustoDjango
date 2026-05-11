// Barra flotante reutilizable con acceso atras y al carrito.
// lib/widgets/custom_floating_app_bar.dart
import 'package:flutter/material.dart';
import '../app_theme.dart';
import '../screens/carrito_screen.dart';

// Widget reutilizable para mostrar acciones rapidas en varias pantallas.
class CustomFloatingAppBar extends StatelessWidget {
  final bool showBack;
  final bool showCart;
  final Color backColor;
  final Color cartColor;

  const CustomFloatingAppBar({
    super.key,
    this.showBack = true,
    this.showCart = true,
    this.backColor = Colors.red,
    this.cartColor = const Color(0xFFB2281D),
  });

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        if (showBack)
          Positioned(
            top: 40,
            left: 16,
            child: CircleAvatar(
              backgroundColor: AppThemeColors.surface.withValues(alpha: 0.92),
              radius: 20,
              child: IconButton(
                padding: EdgeInsets.zero,
                icon: Icon(Icons.arrow_back, color: backColor),
                onPressed: () => Navigator.pop(context),
              ),
            ),
          ),
        if (showCart)
          Positioned(
            top: 40,
            right: 16,
            child: Material(
              color: Colors.transparent,
              child: InkWell(
                borderRadius: BorderRadius.circular(18),
                onTap: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (context) => const CarritoPage(),
                    ),
                  );
                },
                child: Container(
                  width: 48,
                  height: 48,
                  decoration: BoxDecoration(
                    color: AppThemeColors.surface,
                    borderRadius: BorderRadius.circular(18),
                    border: Border.all(color: AppThemeColors.line),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withValues(alpha: 0.06),
                        blurRadius: 12,
                        offset: const Offset(0, 6),
                      ),
                    ],
                  ),
                  child: Icon(Icons.shopping_bag_outlined, color: cartColor),
                ),
              ),
            ),
          ),
      ],
    );
  }
}
