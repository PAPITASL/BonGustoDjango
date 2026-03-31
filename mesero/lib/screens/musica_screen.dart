// ===== Pantalla `musica_screen.dart` | Muestra la cola actual de solicitudes musicales enviadas por los clientes. =====
import 'dart:async';

import 'package:flutter/material.dart';

import '../services/bongusto_api.dart';

// ===== Clase `MusicaScreen` | Define la vista principal del modulo de musica. =====
class MusicaScreen extends StatefulWidget {
  const MusicaScreen({super.key});

  @override
  State<MusicaScreen> createState() => _MusicaScreenState();
}

// ===== Estado `_MusicaScreenState` | Administra la consulta de canciones y la presentacion del listado. =====
class _MusicaScreenState extends State<MusicaScreen> {
  static const _bg = Color(0xFFF2F1F4);
  static const _card = Color(0xFFFFFFFF);
  static const _ink = Color(0xFF181818);
  static const _muted = Color(0xFF73727A);
  static const _accent = Color(0xFFD90416);
  static const _line = Color(0xFFE8E6EB);

  int _currentIndex = 0;
  bool _loading = true;
  String _error = '';
  List<_SolicitudMusicaData> _cola = [];
  Timer? _refreshTimer;

  @override
  void initState() {
    super.initState();
    _cargarCola();
    _refreshTimer = Timer.periodic(const Duration(seconds: 4), (_) {
      _cargarCola(silent: true);
    });
  }

  @override
  void dispose() {
    _refreshTimer?.cancel();
    super.dispose();
  }

  Future<void> _cargarCola({bool silent = false}) async {
    if (!silent) {
      setState(() {
        _loading = true;
        _error = '';
      });
    }
    try {
      final cola = await BongustoApi.obtenerColaMusica();
      if (!mounted) return;
      setState(() {
        _cola = cola.map(_SolicitudMusicaData.fromMap).toList();
        _loading = false;
        _error = '';
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _error = '$e';
        _loading = false;
      });
    }
  }

  Widget _hero() {
    return Container(
      padding: const EdgeInsets.all(22),
      decoration: BoxDecoration(
        color: _card,
        borderRadius: BorderRadius.circular(30),
        border: Border.all(color: _line),
      ),
      child: const Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'MUSICA',
            style: TextStyle(
              color: _accent,
              fontSize: 12,
              letterSpacing: 3,
              fontWeight: FontWeight.w800,
            ),
          ),
          SizedBox(height: 8),
          Text(
            'Musica clientes',
            style: TextStyle(
              color: _ink,
              fontSize: 30,
              height: 1.06,
              fontWeight: FontWeight.w900,
            ),
          ),
          SizedBox(height: 10),
          Text(
            'La cola musical muestra canciones solicitadas por los clientes.',
            style: TextStyle(
              color: _muted,
              fontSize: 14,
              height: 1.5,
            ),
          ),
        ],
      ),
    );
  }

  Widget _stateCard({required IconData icon, required String text, bool retry = false}) {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: _card,
        borderRadius: BorderRadius.circular(28),
        border: Border.all(color: _line),
      ),
      child: Column(
        children: [
          Icon(icon, size: 48, color: _accent),
          const SizedBox(height: 12),
          Text(text, textAlign: TextAlign.center),
          if (retry) ...[
            const SizedBox(height: 16),
            ElevatedButton(onPressed: _cargarCola, child: const Text('Reintentar')),
          ],
        ],
      ),
    );
  }

  Widget _songCard(_SolicitudMusicaData item) {
    return Container(
      margin: const EdgeInsets.only(bottom: 14),
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: _card,
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: _line),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 54,
            height: 54,
            decoration: BoxDecoration(
              color: const Color(0xFFFFF6EC),
              borderRadius: BorderRadius.circular(18),
            ),
            child: const Icon(Icons.queue_music_rounded, color: _accent),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  item.titulo,
                  style: const TextStyle(
                    color: _ink,
                    fontWeight: FontWeight.w900,
                    fontSize: 18,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  item.artista,
                  style: const TextStyle(color: _muted),
                ),
                const SizedBox(height: 10),
                Text(
                  'Solicitado por: ${item.cliente}',
                  style: const TextStyle(
                    color: _ink,
                    fontWeight: FontWeight.w700,
                  ),
                ),
                if (item.mesaLabel.isNotEmpty) ...[
                  const SizedBox(height: 4),
                  Text(
                    item.mesaLabel,
                    style: const TextStyle(
                      color: _accent,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ],
              ],
            ),
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
            decoration: BoxDecoration(
              color: const Color(0xFFFFECEE),
              borderRadius: BorderRadius.circular(999),
            ),
            child: Text(
              item.estado,
              style: const TextStyle(
                color: _accent,
                fontWeight: FontWeight.w700,
              ),
            ),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: _bg,
      appBar: AppBar(
        backgroundColor: _bg,
        foregroundColor: _ink,
        title: const Text(
          'Musica',
          style: TextStyle(fontWeight: FontWeight.w800),
        ),
      ),
      body: RefreshIndicator(
        color: _accent,
        onRefresh: _cargarCola,
        child: ListView(
          padding: const EdgeInsets.fromLTRB(20, 8, 20, 28),
          children: [
            _hero(),
            const SizedBox(height: 18),
            if (_loading)
              const Padding(
                padding: EdgeInsets.all(32),
                child: Center(child: CircularProgressIndicator()),
              )
            else if (_error.isNotEmpty)
              _stateCard(
                icon: Icons.error_outline,
                text: 'No se pudo cargar la cola musical.\n$_error',
                retry: true,
              )
            else if (_cola.isEmpty)
              _stateCard(
                icon: Icons.music_off_rounded,
                text: 'No hay solicitudes de musica.',
              )
            else
              ..._cola.map(_songCard),
          ],
        ),
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (i) {
          setState(() => _currentIndex = i);
          if (i == 0) {
            Navigator.pushNamedAndRemoveUntil(context, '/home', (_) => false);
          } else if (i == 1) {
            Navigator.pushNamed(context, '/perfil');
          }
        },
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.home_outlined), label: 'Inicio'),
          BottomNavigationBarItem(icon: Icon(Icons.person_outline), label: 'Perfil'),
        ],
      ),
    );
  }
}

class _SolicitudMusicaData {
  final String titulo;
  final String artista;
  final String cliente;
  final String mesaLabel;
  final String estado;

  const _SolicitudMusicaData({
    required this.titulo,
    required this.artista,
    required this.cliente,
    required this.mesaLabel,
    required this.estado,
  });

  factory _SolicitudMusicaData.fromMap(Map<String, dynamic> json) {
    final musica = Map<String, dynamic>.from(json['musica'] as Map? ?? const {});
    final estado = (json['estado_solicitud'] ?? '').toString().trim();
    return _SolicitudMusicaData(
      titulo: (musica['nombre_musica'] ?? 'Sin cancion').toString(),
      artista: (musica['artista_musica'] ?? 'Sin artista').toString(),
      cliente: (json['cliente_nombre'] ?? 'Cliente').toString(),
      mesaLabel: (json['mesa_label'] ?? '').toString(),
      estado: estado.isEmpty ? 'pendiente' : estado,
    );
  }
}
