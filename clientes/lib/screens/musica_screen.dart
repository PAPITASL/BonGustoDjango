import 'dart:async';
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:web_socket_channel/io.dart';

import '../api_config.dart';
import '../app_theme.dart';
import '../services/bongusto_api.dart';
import '../services/session_service.dart';
import 'custom_app_bar.dart';
import 'home_screen.dart';
import 'mapa_screen.dart';
import 'pedidos_screen.dart';
import 'perfil_screen.dart';

class MusicaScreen extends StatefulWidget {
  const MusicaScreen({super.key});

  @override
  State<MusicaScreen> createState() => _MusicaScreenState();
}

class _MusicaScreenState extends State<MusicaScreen> {
  static Color get _bg => AppThemeColors.bg;
  static Color get _card => AppThemeColors.surface;
  static Color get _ink => AppThemeColors.text;
  static Color get _muted => AppThemeColors.muted;
  static const _accent = Color(0xFFD90416);
  static Color get _accentSoft => AppThemeColors.accentSoft;
  static Color get _line => AppThemeColors.line;

  int _currentIndex = 0;
  bool _loading = true;
  bool _sending = false;
  bool _socketConnected = false;
  String? _error;
  List<_ColaCancionData> _playlist = <_ColaCancionData>[];
  List<_CatalogoCancionData> _catalog = <_CatalogoCancionData>[];
  _ColaCancionData? _currentSong;
  IOWebSocketChannel? _musicChannel;
  Timer? _refreshTimer;
  Timer? _reconnectTimer;

  @override
  void initState() {
    super.initState();
    _cargarMusica();
    _conectarMusicaLive();
    _refreshTimer = Timer.periodic(
      const Duration(seconds: 20),
      (_) => _cargarMusica(silent: true),
    );
  }

  @override
  void dispose() {
    _refreshTimer?.cancel();
    _reconnectTimer?.cancel();
    _musicChannel?.sink.close();
    super.dispose();
  }

  Future<void> _cargarMusica({bool silent = false}) async {
    if (!silent) {
      setState(() {
        _loading = true;
        _error = null;
      });
    }

    try {
      final results = await Future.wait<dynamic>([
        BongustoApi.obtenerSnapshotMusica(),
        BongustoApi.obtenerMusicas(),
      ]);
      final snapshot = Map<String, dynamic>.from(results[0] as Map);
      final catalog = (results[1] as List<dynamic>)
          .map((item) => _CatalogoCancionData.fromMap(Map<String, dynamic>.from(item as Map)))
          .toList();
      if (!mounted) return;
      _sincronizarDesdeSnapshot(snapshot, catalog: catalog, silent: silent);
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _error = '$e';
        _loading = false;
      });
    }
  }

  void _sincronizarDesdeSnapshot(
    Map<String, dynamic> snapshot, {
    required List<_CatalogoCancionData> catalog,
    required bool silent,
  }) {
    final cola = (snapshot['cola'] as List<dynamic>? ?? const <dynamic>[])
        .map((item) => _ColaCancionData.fromMap(Map<String, dynamic>.from(item as Map)))
        .toList()
      ..sort((a, b) => a.posicion.compareTo(b.posicion));
    final actualMap = snapshot['actual'];
    final actual = actualMap is Map
        ? _ColaCancionData.fromMap(Map<String, dynamic>.from(actualMap))
        : null;

    setState(() {
      _playlist = cola;
      _catalog = catalog;
      _currentSong = actual ?? (cola.isNotEmpty ? cola.first : null);
      _loading = false;
      _error = null;
    });
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
      channel.stream.listen(
        (dynamic event) {
          _socketConnected = true;
          _procesarEventoSocket(event);
        },
        onDone: _programarReconexion,
        onError: (_) => _programarReconexion(),
      );
      if (mounted) {
        setState(() {
          _socketConnected = true;
        });
      }
    } catch (_) {
      _programarReconexion();
    }
  }

  void _procesarEventoSocket(dynamic event) {
    try {
      final decoded = jsonDecode(event.toString());
      if (decoded is! Map) {
        _cargarMusica(silent: true);
        return;
      }
      final data = Map<String, dynamic>.from(decoded);
      final type = (data['type'] ?? '').toString();
      if (type == 'snapshot' && data['data'] is Map) {
        if (!mounted) return;
        _sincronizarDesdeSnapshot(
          Map<String, dynamic>.from(data['data'] as Map),
          catalog: _catalog,
          silent: true,
        );
        return;
      }
      _cargarMusica(silent: true);
    } catch (_) {
      _cargarMusica(silent: true);
    }
  }

  void _programarReconexion() {
    _socketConnected = false;
    if (!mounted) return;
    _reconnectTimer?.cancel();
    _reconnectTimer = Timer(const Duration(seconds: 10), () {
      _cargarMusica(silent: true);
      _conectarMusicaLive();
    });
  }

  void _showNotice(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          message,
          style: TextStyle(color: _ink, fontWeight: FontWeight.w600),
        ),
        behavior: SnackBarBehavior.floating,
        backgroundColor: _card,
        elevation: 10,
        margin: const EdgeInsets.fromLTRB(16, 0, 16, 92),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      ),
    );
  }

  Future<void> _mostrarSolicitudManual() async {
    final tituloController = TextEditingController();
    final artistaController = TextEditingController();
    final formKey = GlobalKey<FormState>();

    await showDialog<void>(
      context: context,
      builder: (dialogContext) {
        return AlertDialog(
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(24),
          ),
          title: const Text(
            'Solicitar cancion',
            style: TextStyle(fontWeight: FontWeight.w800),
          ),
          content: Form(
            key: formKey,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                TextFormField(
                  controller: tituloController,
                  decoration: const InputDecoration(
                    labelText: 'Nombre de la cancion',
                    hintText: 'Ej. Hound Dog',
                  ),
                  validator: (value) {
                    if (value == null || value.trim().isEmpty) {
                      return 'Escribe el nombre de la cancion';
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller: artistaController,
                  decoration: const InputDecoration(
                    labelText: 'Artista',
                    hintText: 'Ej. Elvis Presley',
                  ),
                  validator: (value) {
                    if (value == null || value.trim().isEmpty) {
                      return 'Escribe el artista';
                    }
                    return null;
                  },
                ),
              ],
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(dialogContext),
              child: const Text('Cancelar'),
            ),
            ElevatedButton(
              onPressed: () async {
                if (!formKey.currentState!.validate()) {
                  return;
                }

                final idUsuario = SessionService.idUsuario;
                if (idUsuario == null) {
                  Navigator.pop(dialogContext);
                  _showNotice('Debes iniciar sesion para pedir musica.');
                  return;
                }

                Navigator.pop(dialogContext);
                setState(() => _sending = true);
                try {
                  await BongustoApi.solicitarMusica(
                    idUsuario: idUsuario,
                    nombreMusica: tituloController.text.trim(),
                    artistaMusica: artistaController.text.trim(),
                  );
                  if (!mounted) return;
                  await _cargarMusica(silent: true);
                  _showNotice('Solicitud enviada correctamente.');
                } catch (e) {
                  if (!mounted) return;
                  _showNotice('No se pudo enviar la solicitud: $e');
                } finally {
                  if (mounted) {
                    setState(() => _sending = false);
                  }
                }
              },
              child: const Text('Enviar'),
            ),
          ],
        );
      },
    );
  }

  void _abrirSeccion(int index) {
    setState(() => _currentIndex = index);
    if (index == 0) {
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (_) => const HomeScreen()),
      );
      return;
    }
    if (index == 1) {
      Navigator.push(
        context,
        MaterialPageRoute(builder: (_) => const PedidosScreen()),
      );
      return;
    }
    if (index == 2) {
      Navigator.push(
        context,
        MaterialPageRoute(builder: (_) => const MapScreen()),
      );
      return;
    }
    if (index == 3) {
      Navigator.push(
        context,
        MaterialPageRoute(builder: (_) => const PerfilScreen()),
      );
    }
  }

  Widget _bottomBar() {
    return BottomNavigationBar(
      currentIndex: _currentIndex,
      onTap: _abrirSeccion,
      type: BottomNavigationBarType.fixed,
      selectedItemColor: _accent,
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

  void _mostrarColaReproduccion() {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) {
        return DraggableScrollableSheet(
          initialChildSize: 0.72,
          minChildSize: 0.5,
          maxChildSize: 0.92,
          builder: (_, controller) {
            return Container(
              padding: const EdgeInsets.fromLTRB(18, 18, 18, 22),
              decoration: BoxDecoration(
                color: _card,
                borderRadius: const BorderRadius.vertical(top: Radius.circular(28)),
              ),
              child: Column(
                children: [
                  Container(
                    width: 44,
                    height: 5,
                    decoration: BoxDecoration(
                      color: _line,
                      borderRadius: BorderRadius.circular(999),
                    ),
                  ),
                  const SizedBox(height: 18),
                  Text(
                    'Cola de reproduccion',
                    style: TextStyle(
                      color: _ink,
                      fontSize: 22,
                      fontWeight: FontWeight.w900,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'El orden se actualiza automaticamente para todos los perfiles.',
                    textAlign: TextAlign.center,
                    style: TextStyle(color: _muted, fontSize: 13, height: 1.45),
                  ),
                  const SizedBox(height: 16),
                  Expanded(
                    child: ListView.separated(
                      controller: controller,
                      itemCount: _playlist.length,
                      separatorBuilder: (_, __) => const SizedBox(height: 10),
                      itemBuilder: (context, index) {
                        final cancion = _playlist[index];
                        final selected =
                            _currentSong?.idSolicitud == cancion.idSolicitud;
                        return Container(
                          padding: const EdgeInsets.all(16),
                          decoration: BoxDecoration(
                            color: selected ? _accentSoft : const Color(0xFFF8F8FA),
                            borderRadius: BorderRadius.circular(20),
                            border: Border.all(
                              color: selected ? _accent : _line,
                            ),
                          ),
                          child: Row(
                            children: [
                              Container(
                                width: 48,
                                height: 48,
                                decoration: BoxDecoration(
                                  color: Colors.white,
                                  borderRadius: BorderRadius.circular(16),
                                ),
                                child: Icon(
                                  selected
                                      ? Icons.play_arrow_rounded
                                      : Icons.queue_music_rounded,
                                  color: _accent,
                                ),
                              ),
                              const SizedBox(width: 14),
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      cancion.estadoLabel,
                                      style: TextStyle(
                                        color: selected ? _accent : _muted,
                                        fontSize: 12,
                                        fontWeight: FontWeight.w800,
                                        letterSpacing: 0.4,
                                      ),
                                    ),
                                    const SizedBox(height: 4),
                                    Text(
                                      cancion.nombre,
                                      style: TextStyle(
                                        color: _ink,
                                        fontSize: 16,
                                        fontWeight: FontWeight.w800,
                                      ),
                                    ),
                                    const SizedBox(height: 4),
                                    Text(
                                      '${cancion.artista} · ${cancion.mesaLabel}',
                                      style: TextStyle(
                                        color: _muted,
                                        fontSize: 13,
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                              Text(
                                selected ? 'Ahora' : 'Turno ${cancion.posicion}',
                                style: TextStyle(
                                  color: selected ? _accent : _muted,
                                  fontWeight: FontWeight.w700,
                                ),
                              ),
                            ],
                          ),
                        );
                      },
                    ),
                  ),
                  const SizedBox(height: 14),
                  SizedBox(
                    width: double.infinity,
                    height: 52,
                    child: ElevatedButton(
                      onPressed: () {
                        Navigator.pop(context);
                        _mostrarSolicitudManual();
                      },
                      child: const Text('Pedir cancion'),
                    ),
                  ),
                ],
              ),
            );
          },
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    final cancionActual = _currentSong;
    final siguienteCancion = _playlist.length > 1 ? _playlist[1] : null;

    return Scaffold(
      backgroundColor: _bg,
      bottomNavigationBar: _bottomBar(),
      body: Stack(
        children: [
          SafeArea(
            child: RefreshIndicator(
              color: _accent,
              onRefresh: _cargarMusica,
              child: ListView(
                padding: const EdgeInsets.fromLTRB(20, 82, 20, 28),
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
                        Text(
                          'ROCOLA BON GUSTO',
                          style: TextStyle(
                            color: _accent,
                            fontSize: 12,
                            letterSpacing: 3,
                            fontWeight: FontWeight.w800,
                          ),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          'Pide la cancion para tu mesa',
                          style: TextStyle(
                            color: _ink,
                            fontSize: 28,
                            height: 1.1,
                            fontWeight: FontWeight.w900,
                          ),
                        ),
                        const SizedBox(height: 10),
                        Text(
                          'La cola musical se sincroniza en tiempo real con administracion y meseros.',
                          style: TextStyle(
                            color: _muted,
                            fontSize: 14,
                            height: 1.5,
                          ),
                        ),
                        const SizedBox(height: 18),
                        SizedBox(
                          width: double.infinity,
                          height: 54,
                          child: ElevatedButton(
                            onPressed: _sending
                                ? null
                                : _mostrarSolicitudManual,
                            child: Text(
                              _sending
                                  ? 'Enviando solicitud...'
                                  : 'Pedir cancion',
                            ),
                          ),
                        ),
                        const SizedBox(height: 22),
                        if (_loading)
                          const Padding(
                            padding: EdgeInsets.all(32),
                            child: Center(child: CircularProgressIndicator()),
                          )
                        else if (_error != null)
                          _stateCard(
                            icon: Icons.cloud_off_outlined,
                            text: 'No se pudo cargar la cola musical.\n$_error',
                          )
                        else if (cancionActual == null)
                          _stateCard(
                            icon: Icons.music_off_rounded,
                            text: 'Todavia no hay canciones en la cola de reproduccion.',
                          )
                        else ...[
                          Container(
                            width: double.infinity,
                            padding: const EdgeInsets.all(24),
                            decoration: BoxDecoration(
                              color: const Color(0xFFFFF7F2),
                              borderRadius: BorderRadius.circular(28),
                              border: Border.all(color: _line),
                            ),
                            child: Column(
                              children: [
                                Container(
                                  width: 128,
                                  height: 128,
                                  decoration: BoxDecoration(
                                    color: _accentSoft,
                                    borderRadius: BorderRadius.circular(28),
                                  ),
                                  child: const Icon(
                                    Icons.music_note_rounded,
                                    size: 64,
                                    color: _accent,
                                  ),
                                ),
                                const SizedBox(height: 18),
                                Text(
                                  cancionActual.nombre,
                                  textAlign: TextAlign.center,
                                  style: TextStyle(
                                    color: _ink,
                                    fontSize: 24,
                                    height: 1.1,
                                    fontWeight: FontWeight.w900,
                                  ),
                                ),
                                const SizedBox(height: 8),
                                Text(
                                  cancionActual.artista,
                                  textAlign: TextAlign.center,
                                  style: TextStyle(color: _muted, fontSize: 15),
                                ),
                                const SizedBox(height: 12),
                                Text(
                                  cancionActual.estadoLabel,
                                  style: const TextStyle(
                                    color: _accent,
                                    fontSize: 13,
                                    fontWeight: FontWeight.w800,
                                  ),
                                ),
                                if (cancionActual.segundosRestantes != null) ...[
                                  const SizedBox(height: 6),
                                  Text(
                                    'Tiempo restante aproximado: ${cancionActual.segundosRestantes}s',
                                    style: TextStyle(
                                      color: _muted,
                                      fontSize: 13,
                                      fontWeight: FontWeight.w700,
                                    ),
                                  ),
                                ],
                                if (siguienteCancion != null) ...[
                                  const SizedBox(height: 10),
                                  Text(
                                    'Despues sigue: ${siguienteCancion.nombre} · ${siguienteCancion.artista}',
                                    textAlign: TextAlign.center,
                                    style: TextStyle(
                                      color: _muted,
                                      fontSize: 13,
                                      height: 1.4,
                                    ),
                                  ),
                                ],
                              ],
                            ),
                          ),
                          const SizedBox(height: 18),
                          SizedBox(
                            width: double.infinity,
                            height: 54,
                            child: ElevatedButton(
                              onPressed: _playlist.isEmpty
                                  ? null
                                  : _mostrarColaReproduccion,
                              child: const Text('Cola de reproduccion'),
                            ),
                          ),
                        ],
                        const SizedBox(height: 18),
                        if (_catalog.isEmpty)
                          _stateCard(
                            icon: Icons.library_music_outlined,
                            text: 'No hay canciones registradas.',
                          )
                        else
                          ..._catalog.map(_catalogCard),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
          const CustomFloatingAppBar(showBack: true, showCart: true),
        ],
      ),
    );
  }

  Widget _stateCard({required IconData icon, required String text}) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: const Color(0xFFF8F8FA),
        borderRadius: BorderRadius.circular(22),
        border: Border.all(color: _line),
      ),
      child: Column(
        children: [
          Icon(icon, color: _accent, size: 32),
          const SizedBox(height: 12),
          Text(
            text,
            textAlign: TextAlign.center,
            style: TextStyle(color: _muted, fontSize: 14, height: 1.5),
          ),
        ],
      ),
    );
  }

  Widget _catalogCard(_CatalogoCancionData song) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFFF8F8FA),
        borderRadius: BorderRadius.circular(22),
        border: Border.all(color: _line),
      ),
      child: Row(
        children: [
          Container(
            width: 52,
            height: 52,
            decoration: BoxDecoration(
              color: _accentSoft,
              borderRadius: BorderRadius.circular(16),
            ),
            child: const Icon(Icons.music_note_rounded, color: _accent),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  song.nombre,
                  style: TextStyle(
                    color: _ink,
                    fontSize: 16,
                    fontWeight: FontWeight.w800,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  song.artista,
                  style: TextStyle(color: _muted, fontSize: 13),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _ColaCancionData {
  final int idSolicitud;
  final int idMusica;
  final String nombre;
  final String artista;
  final String estado;
  final String clienteNombre;
  final String mesaLabel;
  final int posicion;
  final int? segundosRestantes;

  const _ColaCancionData({
    required this.idSolicitud,
    required this.idMusica,
    required this.nombre,
    required this.artista,
    required this.estado,
    required this.clienteNombre,
    required this.mesaLabel,
    required this.posicion,
    required this.segundosRestantes,
  });

  String get estadoLabel {
    if (estado == 'reproduciendo') return 'Sonando ahora';
    return 'Turno $posicion';
  }

  factory _ColaCancionData.fromMap(Map<String, dynamic> json) {
    final musica = Map<String, dynamic>.from(
      json['musica'] as Map? ?? const {},
    );
    return _ColaCancionData(
      idSolicitud: int.tryParse('${json['id_solicitud']}') ?? 0,
      idMusica: int.tryParse('${json['id_musica'] ?? musica['id_musica']}') ?? 0,
      nombre: (json['cancion'] ?? musica['nombre_musica'] ?? 'Cancion').toString(),
      artista: (json['artista'] ?? musica['artista_musica'] ?? 'Artista no definido').toString(),
      estado: (json['estado_solicitud'] ?? 'pendiente').toString(),
      clienteNombre: (json['cliente_nombre'] ?? 'Cliente').toString(),
      mesaLabel: (json['mesa_label'] ?? 'Sin mesa').toString(),
      posicion: int.tryParse('${json['posicion_orden']}') ?? 0,
      segundosRestantes: int.tryParse('${json['segundos_restantes']}'),
    );
  }
}

class _CatalogoCancionData {
  final int idMusica;
  final String nombre;
  final String artista;

  const _CatalogoCancionData({
    required this.idMusica,
    required this.nombre,
    required this.artista,
  });

  factory _CatalogoCancionData.fromMap(Map<String, dynamic> json) {
    return _CatalogoCancionData(
      idMusica: int.tryParse('${json['id_musica']}') ?? 0,
      nombre: (json['nombre_musica'] ?? 'Cancion').toString(),
      artista: (json['artista_musica'] ?? 'Artista').toString(),
    );
  }
}
