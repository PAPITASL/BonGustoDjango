// ===== Pantalla `interaccion_screen.dart` | Gestiona el chat en tiempo real entre el mesero y administracion. =====
import 'dart:async';
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:web_socket_channel/io.dart';

import '../api_config.dart';
import '../services/bongusto_api.dart';
import '../services/session_service.dart';

// ===== Clase `InteraccionScreen` | Representa la vista principal del modulo de conversacion operativa. =====
class InteraccionScreen extends StatefulWidget {
  const InteraccionScreen({super.key});

  @override
  State<InteraccionScreen> createState() => _InteraccionScreenState();
}

// ===== Estado `_InteraccionScreenState` | Controla historial, socket, mensajes y estado de conexion. =====
class _InteraccionScreenState extends State<InteraccionScreen> {
  static const _bg = Color(0xFFF2F1F4);
  static const _card = Color(0xFFFFFFFF);
  static const _ink = Color(0xFF181818);
  static const _muted = Color(0xFF73727A);
  static const _accent = Color(0xFFD90416);
  static const _line = Color(0xFFE8E6EB);

  final TextEditingController _controller = TextEditingController();
  final TextEditingController _destinatarioCtrl = TextEditingController(
    text: 'administrador',
  );
  final List<Map<String, String>> _mensajes = <Map<String, String>>[];
  final ScrollController _scrollController = ScrollController();
  Timer? _historialTimer;
  IOWebSocketChannel? _channel;
  String _estado = 'Conectando...';
  String _destinatario = 'administrador';
  bool _socketConectado = false;

  String get _participante => 'mesero';

  @override
  void initState() {
    super.initState();
    _conectar();
    _cargarHistorial();
    _iniciarSincronizacion();
  }

  @override
  void dispose() {
    _historialTimer?.cancel();
    _channel?.sink.close();
    _controller.dispose();
    _destinatarioCtrl.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  Future<void> _cargarHistorial() async {
    if (!SessionService.estaAutenticado) {
      if (!mounted) return;
      setState(() {
        _estado = 'Sesion requerida';
        _mensajes.clear();
      });
      return;
    }

    try {
      final List<Map<String, dynamic>> data =
          await BongustoApi.obtenerHistorialChat(
        participante: _participante,
        con: _destinatario,
      );
      if (!mounted) return;
      setState(() {
        _mensajes
          ..clear()
          ..addAll(
            data.map<Map<String, String>>(
              (Map<String, dynamic> item) => <String, String>{
                'remitente': (item['remitente'] ?? '').toString(),
                'mensaje': (item['mensaje'] ?? '').toString(),
              },
            ),
          );
      });
      _scrollToBottom();
    } catch (error) {
      if (!mounted) return;
      final textoError = error.toString().toLowerCase();
      if (textoError.contains('token') ||
          textoError.contains('sesion') ||
          textoError.contains('autenticacion') ||
          textoError.contains('401')) {
        setState(() => _estado = 'Sesion expirada');
        return;
      }
      if (!_socketConectado) {
        setState(() => _estado = 'Sin conexion');
      }
    }
  }

  void _iniciarSincronizacion() {
    _historialTimer?.cancel();
    _historialTimer = Timer.periodic(const Duration(seconds: 2), (_) {
      if (!mounted || !SessionService.estaAutenticado) return;
      _cargarHistorial();
    });
  }

  void _conectar() {
    if (!SessionService.estaAutenticado || SessionService.apiToken.isEmpty) {
      if (mounted) {
        setState(() => _estado = 'Sesion requerida');
      }
      return;
    }

    final wsScheme = ApiConfig.baseUrl.startsWith('https') ? 'wss' : 'ws';
    final Map<String, String> query = <String, String>{};
    query['token'] = SessionService.apiToken;
    final uri = Uri(
      scheme: wsScheme,
      host: ApiConfig.host,
      port: int.parse(ApiConfig.port),
      path: '/ws/chat/$_participante/',
      queryParameters: query.isEmpty ? null : query,
    );
    final IOWebSocketChannel channel = IOWebSocketChannel.connect(uri);
    _channel = channel;
    if (mounted) {
      setState(() {
        _socketConectado = true;
        _estado = 'Conectado';
      });
    }
    channel.stream.listen(
      (dynamic event) {
        final Map<String, dynamic> data =
            jsonDecode(event.toString()) as Map<String, dynamic>;
        final String remitente = (data['remitente'] ?? '').toString();
        final String destinatario = (data['destinatario'] ?? '').toString();
        final String mensaje = (data['mensaje'] ?? '').toString();
        final bool conversaConSeleccion =
            remitente == _destinatario || destinatario == _destinatario;
        if (!conversaConSeleccion) return;
        if (remitente != _participante) {
          _destinatario = remitente;
          _destinatarioCtrl.text = remitente;
        }
        setState(() {
          _mensajes.add(<String, String>{
            'remitente': remitente,
            'mensaje': mensaje,
          });
        });
        _scrollToBottom();
      },
      onError: (_) {
        if (mounted) {
          setState(() {
            _socketConectado = false;
            _estado = 'Sincronizando';
          });
        }
      },
      onDone: () {
        if (mounted) {
          setState(() {
            _socketConectado = false;
            _estado = 'Sincronizando';
          });
        }
      },
    );
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!_scrollController.hasClients) return;
      _scrollController.animateTo(
        _scrollController.position.maxScrollExtent,
        duration: const Duration(milliseconds: 250),
        curve: Curves.easeOut,
      );
    });
  }

  Future<void> _enviar() async {
    final texto = _controller.text.trim();
    if (texto.isEmpty || !SessionService.estaAutenticado) {
      return;
    }
    try {
      if (_channel != null && _socketConectado) {
        _channel!.sink.add(
          jsonEncode({
            'tipo': 'mensaje',
            'remitente': _participante,
            'destinatario': _destinatario,
            'mensaje': texto,
          }),
        );
      } else {
        await BongustoApi.enviarMensajeChat(
          participante: _participante,
          destinatario: _destinatario,
          mensaje: texto,
        );
        await _cargarHistorial();
      }
      _controller.clear();
    } catch (error) {
      try {
        await BongustoApi.enviarMensajeChat(
          participante: _participante,
          destinatario: _destinatario,
          mensaje: texto,
        );
        await _cargarHistorial();
        _controller.clear();
        if (mounted) {
          setState(() {
            _socketConectado = false;
            _estado = 'Sincronizando';
          });
        }
      } catch (fallbackError) {
        if (mounted) {
          final textoError =
              '$error ${fallbackError.toString()}'.toLowerCase();
          if (textoError.contains('token') ||
              textoError.contains('sesion') ||
              textoError.contains('autenticacion') ||
              textoError.contains('401')) {
            setState(() => _estado = 'Sesion expirada');
          } else {
            setState(() => _estado = 'Error al enviar');
          }
        }
      }
    }
  }

  Widget _hero() {
    return Container(
      margin: const EdgeInsets.fromLTRB(20, 8, 20, 16),
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
            'CHAT',
            style: TextStyle(
              color: _accent,
              fontSize: 12,
              letterSpacing: 3,
              fontWeight: FontWeight.w800,
            ),
          ),
          SizedBox(height: 8),
          Text(
            'Mensajeria en tiempo real',
            style: TextStyle(
              color: _ink,
              fontSize: 30,
              height: 1.06,
              fontWeight: FontWeight.w900,
            ),
          ),
          SizedBox(height: 10),
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
        title: Text('Chat ($_estado)', style: const TextStyle(fontWeight: FontWeight.w800)),
      ),
      body: Column(
        children: [
          _hero(),
          Padding(
            padding: const EdgeInsets.fromLTRB(20, 0, 20, 12),
            child: Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: _card,
                borderRadius: BorderRadius.circular(22),
                border: Border.all(color: _line),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Destino actual',
                    style: TextStyle(
                      color: _muted,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                  const SizedBox(height: 8),
                  TextField(
                    controller: _destinatarioCtrl,
                    onSubmitted: (value) {
                      setState(() {
                        _destinatario = value.trim().isEmpty
                            ? 'administrador'
                            : value.trim();
                      });
                      _cargarHistorial();
                    },
                    decoration: const InputDecoration(
                      hintText: 'administrador o cliente_5',
                    ),
                  ),
                ],
              ),
            ),
          ),
          Expanded(
            child: ListView.builder(
              controller: _scrollController,
              padding: const EdgeInsets.fromLTRB(20, 0, 20, 16),
              itemCount: _mensajes.length,
              itemBuilder: (_, i) {
                final m = _mensajes[i];
                final mio = m['remitente'] == _participante;
                return Align(
                  alignment:
                      mio ? Alignment.centerRight : Alignment.centerLeft,
                  child: Container(
                    margin: const EdgeInsets.only(bottom: 10),
                    padding: const EdgeInsets.all(14),
                    constraints: const BoxConstraints(maxWidth: 320),
                    decoration: BoxDecoration(
                      color: mio ? _accent : _card,
                      borderRadius: BorderRadius.circular(20),
                      border: mio ? null : Border.all(color: _line),
                    ),
                    child: Text(
                      m['mensaje'] ?? '',
                      style: TextStyle(
                        color: mio ? Colors.white : _ink,
                        height: 1.4,
                      ),
                    ),
                  ),
                );
              },
            ),
          ),
          SafeArea(
            top: false,
            child: Padding(
              padding: const EdgeInsets.fromLTRB(20, 0, 20, 14),
              child: Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: _controller,
                      decoration: const InputDecoration(
                        hintText: 'Escribe tu mensaje...',
                      ),
                      onSubmitted: (_) => _enviar(),
                    ),
                  ),
                  const SizedBox(width: 10),
                  Container(
                    decoration: BoxDecoration(
                      color: _accent,
                      borderRadius: BorderRadius.circular(16),
                    ),
                    child: IconButton(
                      icon: const Icon(Icons.send, color: Colors.white),
                      onPressed: _enviar,
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
}
