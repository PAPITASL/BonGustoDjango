// Servicio encargado de guardar y recuperar la sesion del cliente.
import 'dart:convert';

import 'package:flutter_secure_storage/flutter_secure_storage.dart';

// Clase estatica que centraliza token, usuario actual y cierre de sesion.
class SessionService {
  static const FlutterSecureStorage _storage = FlutterSecureStorage();
  static const String _sessionKey = 'bongusto_cliente_session';

  static Map<String, dynamic>? _usuarioActual;

  static Map<String, dynamic>? get usuarioActual => _usuarioActual;

  static bool get estaAutenticado => _usuarioActual != null;

  static int? get idUsuario => _asInt(_usuarioActual?['id_usuario']);

  static String get nombreCompleto =>
      (_usuarioActual?['nombre_completo'] ?? '').toString();

  static String get correo =>
      (_usuarioActual?['correo'] ?? '').toString();

  static String get apiToken =>
      _sanitizeToken(_usuarioActual?['api_token']);

  static int? get mesaId =>
      _asInt(_usuarioActual?['mesa_id']);

  static int? get mesaNumero =>
      _asInt(_usuarioActual?['mesa_numero']);

  static String get tipoPedido =>
      (_usuarioActual?['tipo_pedido'] ?? 'restaurante').toString();

  static String get mesaLabel =>
      (_usuarioActual?['mesa_label'] ?? '').toString();

  static String get mesaEstado =>
      (_usuarioActual?['mesa_estado'] ?? '').toString();

  // Inicializa la sesion desde almacenamiento seguro.
  static Future<void> init() async {
    final rawSession = await _storage.read(key: _sessionKey);

    if (rawSession == null || rawSession.trim().isEmpty) {
      _usuarioActual = null;
      return;
    }

    try {
      final decoded = jsonDecode(rawSession);

      if (decoded is Map<String, dynamic>) {
        _usuarioActual = Map<String, dynamic>.from(decoded);
        return;
      }
    } catch (_) {}

    _usuarioActual = null;

    await _storage.delete(key: _sessionKey);
  }

  // Guarda la sesion cuando el usuario inicia sesion.
  static Future<void> iniciarSesion(
    Map<String, dynamic> usuario,
  ) async {
    _usuarioActual = _sessionSegura(usuario);

    await _storage.write(
      key: _sessionKey,
      value: jsonEncode(_usuarioActual),
    );
  }

  // Cierra sesion y limpia almacenamiento.
  static Future<void> cerrarSesion() async {
    _usuarioActual = null;

    await _storage.delete(key: _sessionKey);
  }

  // Guarda informacion de la mesa actual.
  static Future<void> guardarMesa(
    Map<String, dynamic> mesa,
  ) async {
    _usuarioActual ??= <String, dynamic>{};

    final int? idMesa = _asInt(mesa['id']);
    final int? numeroMesa = _asInt(mesa['numero_mesa']);

    final String etiqueta =
        (mesa['etiqueta'] ?? '').toString().trim();

    final String mesaLabelBackend =
        (mesa['mesa_label'] ?? '').toString().trim();

    String labelFinal = '';

    if (etiqueta.isNotEmpty) {
      labelFinal = etiqueta;
    } else if (mesaLabelBackend.isNotEmpty) {
      labelFinal = mesaLabelBackend;
    } else if (numeroMesa != null) {
      labelFinal = 'Mesa $numeroMesa';
    } else if (idMesa != null) {
      labelFinal = 'Mesa $idMesa';
    }

    _usuarioActual!['mesa_id'] = idMesa;
    _usuarioActual!['mesa_numero'] = numeroMesa;
    _usuarioActual!['mesa_label'] = labelFinal;
    _usuarioActual!['mesa_estado'] =
        (mesa['estado'] ?? '').toString();
    _usuarioActual!['tipo_pedido'] =
        (mesa['tipo_pedido'] ?? 'restaurante').toString();

    await _storage.write(
      key: _sessionKey,
      value: jsonEncode(_usuarioActual),
    );
  }

  // Actualiza parcialmente la sesion.
  static Future<void> actualizarSesion(
    Map<String, dynamic> usuario,
  ) async {
    final actual = Map<String, dynamic>.from(
      _usuarioActual ?? const <String, dynamic>{},
    );

    actual.addAll(
      _sessionSegura({
        ...actual,
        ...usuario,
      }),
    );

    _usuarioActual = actual;

    await _storage.write(
      key: _sessionKey,
      value: jsonEncode(_usuarioActual),
    );
  }

  // Convierte cualquier valor a int seguro.
  static int? _asInt(dynamic value) {
    if (value is int) {
      return value;
    }

    return int.tryParse('$value');
  }

  // Limpia y organiza la informacion segura de sesion.
  static Map<String, dynamic> _sessionSegura(
    Map<String, dynamic> usuario,
  ) {
    return <String, dynamic>{
      'id_usuario': _asInt(usuario['id_usuario']),
      'nombre_completo':
          (usuario['nombre_completo'] ?? '').toString(),
      'correo':
          (usuario['correo'] ?? '').toString(),
      'tipo_usuario':
          (usuario['tipo_usuario'] ?? 'cliente').toString(),
      'api_token':
          _sanitizeToken(usuario['api_token']),
      'mesa_id':
          _asInt(usuario['mesa_id']),
      'mesa_numero':
          _asInt(usuario['mesa_numero']),
      'mesa_label':
          (usuario['mesa_label'] ?? '').toString(),
      'mesa_estado':
          (usuario['mesa_estado'] ?? '').toString(),
      'tipo_pedido':
          (usuario['tipo_pedido'] ?? 'restaurante').toString(),
    };
  }

  // Limpia caracteres raros del token.
  static String _sanitizeToken(dynamic token) {
    final value = (token ?? '').toString().trim();
    final cleaned = value.replaceAll(' ', '').replaceAll('#', '');
    return cleaned.replaceAll('"', '').replaceAll("'", '');
  }
}
