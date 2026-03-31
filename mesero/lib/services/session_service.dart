// ===== Servicio `session_service.dart` | Este archivo administra la sesion del mesero y su persistencia local. =====
import 'dart:convert';

import 'package:flutter_secure_storage/flutter_secure_storage.dart';

// ===== Clase `SessionService` | Expone utilidades estaticas para leer, guardar y limpiar la sesion actual. =====
class SessionService {
  static const FlutterSecureStorage _storage = FlutterSecureStorage();
  static const String _sessionKey = 'bongusto_mesero_session';
  static Map<String, dynamic>? _usuarioActual;

  static Map<String, dynamic>? get usuarioActual => _usuarioActual;

  static bool get estaAutenticado => _usuarioActual != null;

  static int? get idUsuario => _asInt(_usuarioActual?['id_usuario']);

  static String get nombreCompleto =>
      (_usuarioActual?['nombre_completo'] ?? '').toString();

  static String get correo => (_usuarioActual?['correo'] ?? '').toString();

  static String get apiToken => (_usuarioActual?['api_token'] ?? '').toString();

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

  static Future<void> iniciarSesion(Map<String, dynamic> usuario) async {
    _usuarioActual = _sessionSegura(usuario);
    await _storage.write(
      key: _sessionKey,
      value: jsonEncode(_usuarioActual),
    );
  }

  static Future<void> cerrarSesion() async {
    _usuarioActual = null;
    await _storage.delete(key: _sessionKey);
  }

  static Future<void> actualizarSesion(Map<String, dynamic> usuario) async {
    final actual = Map<String, dynamic>.from(_usuarioActual ?? const <String, dynamic>{});
    actual.addAll(_sessionSegura({...actual, ...usuario}));
    _usuarioActual = actual;
    await _storage.write(
      key: _sessionKey,
      value: jsonEncode(_usuarioActual),
    );
  }

  static int? _asInt(dynamic value) {
    if (value is int) {
      return value;
    }
    return int.tryParse('$value');
  }

  static Map<String, dynamic> _sessionSegura(Map<String, dynamic> usuario) {
    return <String, dynamic>{
      'id_usuario': _asInt(usuario['id_usuario']),
      'nombre_completo': (usuario['nombre_completo'] ?? usuario['nombre'] ?? '')
          .toString(),
      'correo': (usuario['correo'] ?? '').toString(),
      'tipo_usuario': (usuario['tipo_usuario'] ?? 'mesero').toString(),
      'api_token': (usuario['api_token'] ?? '').toString(),
    };
  }
}
