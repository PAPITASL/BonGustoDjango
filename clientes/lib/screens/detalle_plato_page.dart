// Pantalla de detalle para mostrar la informacion completa de un plato.
import 'package:flutter/material.dart';

import 'home_screen.dart';
import 'mapa_screen.dart';
import 'pedidos_screen.dart';
import 'perfil_screen.dart';

// Widget que recibe los datos del plato y los pinta en una vista detallada.
class DetallePlatoPage extends StatelessWidget {
  // ====== Datos del plato (recibidos desde la lista) ======
  final String nombre;
  final String descripcion;
  final String precio;
  final String imagen;

  const DetallePlatoPage({
    super.key,
    required this.nombre,
    required this.descripcion,
    required this.precio,
    required this.imagen,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Column(
        children: [
          // ===== Imagen superior con gradiente y botones =====
          Stack(
            children: [
              // Imagen grande del plato
              Container(
                width: double.infinity,
                height: 320,
                decoration: BoxDecoration(
                  image: DecorationImage(
                    image: AssetImage(imagen),
                    fit: BoxFit.cover,
                  ),
                ),
              ),

              // Gradiente que difumina la parte inferior de la imagen hacia blanco
              Positioned(
                bottom: 0,
                left: 0,
                right: 0,
                child: Container(
                  height: 140,
                  decoration: const BoxDecoration(
                    gradient: LinearGradient(
                      begin: Alignment.topCenter,
                      end: Alignment.bottomCenter,
                      colors: [Colors.transparent, Colors.white],
                    ),
                  ),
                ),
              ),

              // Botón volver (arriba izquierda)
              Positioned(
                top: 40,
                left: 16,
                child: CircleAvatar(
                  backgroundColor: Colors.white.withValues(alpha: 0.9),
                  radius: 20,
                  child: IconButton(
                    padding: EdgeInsets.zero,
                    icon: const Icon(Icons.arrow_back, color: Colors.red),
                    onPressed: () => Navigator.pop(context),
                  ),
                ),
              ),

              // Botón carrito (arriba derecha)
              Positioned(
                top: 40,
                right: 16,
                child: CircleAvatar(
                  backgroundColor: const Color(0xFFB2281D), // color de marca
                  radius: 20,
                  child: IconButton(
                    padding: EdgeInsets.zero,
                    icon: const Icon(Icons.shopping_cart, color: Colors.white),
                    onPressed: () {
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(content: Text("Carrito (demo)")),
                      );
                    },
                  ),
                ),
              ),
            ],
          ),

          // ===== Contenido (nombre, descripción, precio, botón) =====
          Expanded(
            child: SingleChildScrollView(
              padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 12),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Título
                  Text(
                    nombre,
                    style: const TextStyle(
                      fontSize: 22,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 10),

                  // Descripción (parrafo)
                  Text(
                    descripcion,
                    style: const TextStyle(fontSize: 15, color: Colors.black87),
                  ),
                  const SizedBox(height: 20),

                  // Precio
                  Text(
                    precio,
                    style: const TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                      color: Colors.redAccent,
                    ),
                  ),
                  const SizedBox(height: 30),

                  // Botón grande centrado "Agregar al carrito"
                  Center(
                    child: SizedBox(
                      width: double.infinity,
                      child: ElevatedButton(
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFFB2281D),
                          padding: const EdgeInsets.symmetric(vertical: 14),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12),
                          ),
                        ),
                        onPressed: () {
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(
                              content: Text("Agregado al carrito (demo)"),
                            ),
                          );
                        },
                        child: const Text(
                          "Agregar al carrito",
                          style: TextStyle(fontSize: 16),
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(height: 24),
                ],
              ),
            ),
          ),
        ],
      ),

      // Barra inferior (igual estilo que en otras pantallas)
      bottomNavigationBar: BottomNavigationBar(
        type: BottomNavigationBarType.fixed,
        selectedItemColor: const Color(0xFFB2281D),
        unselectedItemColor: Colors.black38,
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.home_outlined),
            label: 'Inicio',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.list_alt_outlined),
            label: 'Pedidos',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.map_outlined),
            label: 'Mapa',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.person_outline),
            label: 'Perfil',
          ),
        ],
        currentIndex: 0,
        onTap: (i) {
          if (i == 0) {
            Navigator.pushReplacement(
              context,
              MaterialPageRoute(builder: (_) => const HomeScreen()),
            );
          } else if (i == 1) {
            Navigator.push(
              context,
              MaterialPageRoute(builder: (_) => const PedidosScreen()),
            );
          } else if (i == 2) {
            Navigator.push(
              context,
              MaterialPageRoute(builder: (_) => const MapScreen()),
            );
          } else if (i == 3) {
            Navigator.push(
              context,
              MaterialPageRoute(builder: (_) => const PerfilScreen()),
            );
          }
        },
      ),
    );
  }
}
