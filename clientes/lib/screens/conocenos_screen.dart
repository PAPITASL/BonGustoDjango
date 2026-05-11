// Pantalla informativa para presentar el restaurante y su navegacion inferior.
import 'package:flutter/material.dart';

import 'home_screen.dart';
import 'mapa_screen.dart';
import 'pedidos_screen.dart';
import 'perfil_screen.dart';

// Widget principal de la seccion Conocenos.
class ConocenosPage extends StatefulWidget {
  const ConocenosPage({super.key});

  @override
  State<ConocenosPage> createState() => _ConocenosPageState();
}

// Estado que controla la barra inferior y la navegacion entre secciones.
class _ConocenosPageState extends State<ConocenosPage> {
  int _currentIndex = 0;

  Widget _bottomBar(BuildContext context) {
    return BottomNavigationBar(
      currentIndex: _currentIndex,
      onTap: (i) {
        setState(() => _currentIndex = i);

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
      type: BottomNavigationBarType.fixed,
      selectedItemColor: Colors.red,
      unselectedItemColor: Colors.black38,
      showUnselectedLabels: true,
      items: const [
        BottomNavigationBarItem(
          icon: Icon(Icons.home_outlined),
          label: 'Inicio',
        ),
        BottomNavigationBarItem(
          icon: Icon(Icons.list_alt_outlined),
          label: 'Pedidos',
        ),
        BottomNavigationBarItem(icon: Icon(Icons.map_outlined), label: 'Mapa'),
        BottomNavigationBarItem(
          icon: Icon(Icons.person_outline),
          label: 'Perfil',
        ),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Column(
        children: [
          Stack(
            children: [
              Container(
                width: double.infinity,
                height: 300,
                decoration: const BoxDecoration(
                  image: DecorationImage(
                    image: AssetImage('assets/rapidoyrico.png'),
                    fit: BoxFit.cover,
                  ),
                ),
              ),
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
              Positioned(
                top: 40,
                left: 20,
                child: CircleAvatar(
                  backgroundColor: Colors.white.withValues(alpha: 0.8),
                  child: IconButton(
                    icon: const Icon(Icons.arrow_back, color: Colors.red),
                    onPressed: () => Navigator.pop(context),
                  ),
                ),
              ),
            ],
          ),
          Expanded(
            child: SingleChildScrollView(
              padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 12),
              child: const Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Conocenos',
                    style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
                  ),
                  SizedBox(height: 12),
                  Text(
                    'Santa Juana es un espacio donde el arte y la gastronomia se encuentran '
                    'para crear experiencias unicas. Ubicados en una casa patrimonial en '
                    'Quinta Camacho, Bogota, reinventamos el concepto de gastrobar a traves '
                    'de nuestra esencia "Artronomia", fusionando sabores, creatividad y '
                    'expresion artistica.\n\n'
                    'Nuestro menu, en constante evolucion, mezcla influencias latinas, '
                    'italianas y asiaticas, acompanado de cocteleria de autor y una '
                    'atmosfera vibrante con musica en vivo y experiencias sensoriales. '
                    'Mas que un restaurante, somos un escenario donde cada visita se '
                    'convierte en un momento especial.\n\n'
                    'Ademas, creemos en el impacto social y la inclusion, construyendo '
                    'un equipo diverso que aporta autenticidad a cada detalle. En Santa '
                    'Juana, cada plato, cada espacio y cada experiencia cuentan una historia.',
                    style: TextStyle(
                      fontSize: 15,
                      color: Colors.black87,
                      height: 1.4,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
      bottomNavigationBar: _bottomBar(context),
    );
  }
}
