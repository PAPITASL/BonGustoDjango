import 'dart:async';
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:web_socket_channel/io.dart';

import '../api_config.dart';
import '../services/bongusto_api.dart';
import '../services/session_service.dart';

class MusicaScreen extends StatefulWidget {
  const MusicaScreen({super.key});

  @override
  State<MusicaScreen> createState() => _MusicaScreenState();
}

class _MusicaScreenState extends State<MusicaScreen> {
  static const _bgLight = Color(0xFFF2F1F4);
  static const _bgDark = Color(0xFF101218);
  static const _card = Color(0xFFFFFFFF);
  static const _ink = Color(0xFF181818);
  static const _muted = Color(0xFF73727A);
  static const _accent = Color(0xFFD90416);
  static const _line = Color(0xFFE8E6EB);

  int _currentIndex = 0;
  bool _loading = true;
  bool _socketConnected = false;
  String _error = '';
  String _liveStatus = 'Sincronizando...';
  List<_SolicitudMusicaData> _cola = <_SolicitudMusicaData>[];
  List<_CatalogoCancionData> _catalogo = <_CatalogoCancionData>[];
  IOWebSocketChannel? _musicChannel;
  Timer? _refreshTimer;
  Timer? _reconnectTimer;

  bool get _isDark => Theme.of(context).brightness == Brightness.dark;
  Color get _bg => _isDark ? _bgDark : _bgLight;

  @override
  void initState() {
    super.initState();
    _cargarCola();
    _conectarMusicaLive();
    _refreshTimer = Timer.periodic(
      const Duration(seconds: 20),
      (_) => _cargarCola(silent: true),
    );
  }

  @override
  void dispose() {
    _refreshTimer?.cancel();
    _reconnectTimer?.cancel();
    _musicChannel?.sink.close();
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
      final results = await Future.wait<dynamic>([
        BongustoApi.obtenerSnapshotMusica(),
        BongustoApi.obtenerMusicas(),
      ]);
      final snapshot = Map<String, dynamic>.from(results[0] as Map);
      final catalogo = (results[1] as List<dynamic>)
          .map((item) => _CatalogoCancionData.fromMap(Map<String, dynamic>.from(item as Map)))
          .toList();
      if (!mounted) return;
      final cola = (snapshot['cola'] as List<dynamic>? ?? const <dynamic>[])
          .map((item) => _SolicitudMusicaData.fromMap(Map<String, dynamic>.from(item as Map)))
          .toList()
        ..sort((a, b) => a.posicion.compareTo(b.posicion));
      setState(() {
        _cola = cola;
        _catalogo = catalogo;
        _loading = false;
        _error = '';
        _liveStatus = _socketConnected ? 'En vivo' : 'Sincronizado';
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _error = '$e';
        _loading = false;
      });
    }
  }

  void _conectarMusicaLive() {
    _reconnectTimer?.cancel();
    _musicChannel?.sink.close();

    if (!SessionService.estaAutenticado || SessionService.apiToken.isEmpty) {
      return;
    }

    try {
      final wsScheme = ApiConfig.baseUrl.startsWith('https') ? 'wss' : 'ws';
      final wsPort = int.tryParse(ApiConfig.port);
      if (wsPort == null) {
        throw Exception('Puerto WS invalido');
      }

      final uri = Uri(
        scheme: wsScheme,
        host: ApiConfig.host,
        port: wsPort,
        path: '/ws/musica/cola/',
        queryParameters: <String, String>{'token': SessionService.apiToken},
      );

      final channel = IOWebSocketChannel.connect(uri);
      _musicChannel = channel;
      _socketConnected = true;
      if (mounted) {
        setState(() => _liveStatus = 'En vivo');
      }

      channel.stream.listen(
        (dynamic event) {
          _socketConnected = true;
          _procesarEventoSocket(event);
        },
        onDone: _programarReconexion,
        onError: (_) => _programarReconexion(),
      );
    } catch (_) {
      _programarReconexion();
    }
  }

  void _procesarEventoSocket(dynamic event) {
    try {
      final decoded = jsonDecode(event.toString());
      if (decoded is Map &&
          decoded['type'] == 'snapshot' &&
          decoded['data'] is Map) {
        final snapshot = Map<String, dynamic>.from(decoded['data'] as Map);
        final cola = (snapshot['cola'] as List<dynamic>? ?? const <dynamic>[])
            .map((item) => _SolicitudMusicaData.fromMap(Map<String, dynamic>.from(item as Map)))
            .toList()
          ..sort((a, b) => a.posicion.compareTo(b.posicion));
        if (!mounted) return;
        setState(() {
          _cola = cola;
          _catalogo = _catalogo;
          _loading = false;
          _error = '';
          _liveStatus = 'En vivo';
        });
        return;
      }
    } catch (_) {}
    _cargarCola(silent: true);
  }

  void _programarReconexion() {
    _socketConnected = false;
    if (!mounted) return;
    setState(() => _liveStatus = 'Reconectando...');
    _reconnectTimer?.cancel();
    _reconnectTimer = Timer(const Duration(seconds: 2), () {
      _cargarCola(silent: true);
      _conectarMusicaLive();
    });
  }

  Widget _hero() {
    return Container(
      padding: const EdgeInsets.all(22),
      decoration: BoxDecoration(
        color: _card,
        borderRadius: BorderRadius.circular(30),
        border: Border.all(color: _line),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'MUSICA',
            style: TextStyle(
              color: _accent,
              fontSize: 12,
              letterSpacing: 3,
              fontWeight: FontWeight.w800,
            ),
          ),
          const SizedBox(height: 8),
          const Text(
            'Rocola en tiempo real',
            style: TextStyle(
              color: _ink,
              fontSize: 30,
              height: 1.06,
              fontWeight: FontWeight.w900,
            ),
          ),
          const SizedBox(height: 10),
          const Text(
            'Visualiza la cancion actual, la cola activa y la mesa que hizo cada solicitud.',
            style: TextStyle(
              color: _muted,
              fontSize: 14,
              height: 1.5,
            ),
          ),
          const SizedBox(height: 16),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
            decoration: BoxDecoration(
              color: const Color(0xFFF8F8FA),
              borderRadius: BorderRadius.circular(18),
            ),
            child: Row(
              children: [
                Icon(
                  _socketConnected ? Icons.wifi : Icons.sync_problem,
                  color: _accent,
                  size: 18,
                ),
                const SizedBox(width: 8),
                Text(
                  _liveStatus,
                  style: const TextStyle(
                    color: _ink,
                    fontWeight: FontWeight.w700,
                  ),
                ),
              ],
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
          Text(
            text,
            textAlign: TextAlign.center,
            style: const TextStyle(color: _ink),
          ),
          if (retry) ...[
            const SizedBox(height: 16),
            ElevatedButton(onPressed: _cargarCola, child: const Text('Reintentar')),
          ],
        ],
      ),
    );
  }

  Widget _songCard(_SolicitudMusicaData item) {
    final current = item.estado == 'reproduciendo';
    return Container(
      margin: const EdgeInsets.only(bottom: 14),
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: _card,
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: current ? _accent : _line),
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
            child: Icon(
              current ? Icons.play_arrow_rounded : Icons.queue_music_rounded,
              color: _accent,
            ),
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
                const SizedBox(height: 4),
                Text(
                  item.mesaLabel,
                  style: const TextStyle(
                    color: _accent,
                    fontWeight: FontWeight.w700,
                  ),
                ),
                if (item.segundosRestantes != null) ...[
                  const SizedBox(height: 4),
                  Text(
                    'Restan ${item.segundosRestantes}s',
                    style: const TextStyle(
                      color: _muted,
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
              current ? 'Ahora' : 'Turno ${item.posicion}',
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

  Widget _catalogCard(_CatalogoCancionData item) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: _card,
        borderRadius: BorderRadius.circular(22),
        border: Border.all(color: _line),
      ),
      child: Row(
        children: [
          Container(
            width: 52,
            height: 52,
            decoration: BoxDecoration(
              color: const Color(0xFFFFF6EC),
              borderRadius: BorderRadius.circular(16),
            ),
            child: const Icon(Icons.library_music_rounded, color: _accent),
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
                    fontSize: 16,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  item.artista,
                  style: const TextStyle(color: _muted),
                ),
              ],
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
        foregroundColor: _isDark ? Colors.white : _ink,
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
                text: 'No hay solicitudes de musica activas.',
              )
            else
              ..._cola.map(_songCard),
            const SizedBox(height: 18),
            const Text(
              'Canciones disponibles',
              style: TextStyle(
                color: _ink,
                fontSize: 20,
                fontWeight: FontWeight.w900,
              ),
            ),
            const SizedBox(height: 8),
            const Text(
              'Estas son las canciones que el cliente puede agregar a la rocola.',
              style: TextStyle(
                color: _muted,
                fontSize: 13,
                height: 1.45,
              ),
            ),
            const SizedBox(height: 14),
            if (_catalogo.isEmpty)
              _stateCard(
                icon: Icons.library_music_outlined,
                text: 'No hay canciones registradas.',
              )
            else
              ..._catalogo.map(_catalogCard),
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
  final int posicion;
  final int? segundosRestantes;

  const _SolicitudMusicaData({
    required this.titulo,
    required this.artista,
    required this.cliente,
    required this.mesaLabel,
    required this.estado,
    required this.posicion,
    required this.segundosRestantes,
  });

  factory _SolicitudMusicaData.fromMap(Map<String, dynamic> json) {
    final musica = Map<String, dynamic>.from(json['musica'] as Map? ?? const {});
    return _SolicitudMusicaData(
      titulo: (json['cancion'] ?? musica['nombre_musica'] ?? 'Sin cancion').toString(),
      artista: (json['artista'] ?? musica['artista_musica'] ?? 'Sin artista').toString(),
      cliente: (json['cliente_nombre'] ?? 'Cliente').toString(),
      mesaLabel: (json['mesa_label'] ?? 'Sin mesa').toString(),
      estado: (json['estado_solicitud'] ?? 'pendiente').toString(),
      posicion: int.tryParse('${json['posicion_orden']}') ?? 0,
      segundosRestantes: int.tryParse('${json['segundos_restantes']}'),
    );
  }
}

class _CatalogoCancionData {
  final String titulo;
  final String artista;

  const _CatalogoCancionData({
    required this.titulo,
    required this.artista,
  });

  factory _CatalogoCancionData.fromMap(Map<String, dynamic> json) {
    return _CatalogoCancionData(
      titulo: (json['nombre_musica'] ?? 'Sin cancion').toString(),
      artista: (json['artista_musica'] ?? 'Sin artista').toString(),
    );
  }
}
