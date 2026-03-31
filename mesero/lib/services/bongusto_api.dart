// ===== Servicio `bongusto_api.dart` | Reune todas las peticiones HTTP que la app Flutter envia al backend Django. =====
import 'dart:convert';
import 'dart:async';

import 'package:http/http.dart' as http;

import '../api_config.dart';
import 'session_service.dart';

// ===== Clase `BongustoApi` | Encapsula endpoints, headers, manejo de errores y transformacion de respuestas. =====
class BongustoApi {
  static const Duration _requestTimeout = Duration(seconds: 15);

  static Map<String, String> _headers({bool authenticated = false}) {
    final headers = <String, String>{'Content-Type': 'application/json'};
    final token = SessionService.apiToken;
    if (authenticated) {
      if (token.isEmpty) {
        throw Exception('La sesion expiro. Inicia sesion nuevamente.');
      }
      headers['Authorization'] = 'Bearer $token';
    }
    return headers;
  }

  static Uri _buildUri(String path, {Map<String, String?> query = const {}}) {
    return _buildUriFromBase(
      ApiConfig.baseUrl,
      path,
      query: query,
    );
  }

  static Uri _buildUriFromBase(
    String baseUrl,
    String path, {
    Map<String, String?> query = const {},
  }) {
    final filteredQuery = <String, String>{};
    for (final entry in query.entries) {
      final value = entry.value;
      if (value != null && value.isNotEmpty) {
        filteredQuery[entry.key] = value;
      }
    }

    return Uri.parse(
      '$baseUrl$path',
    ).replace(queryParameters: filteredQuery.isEmpty ? null : filteredQuery);
  }

  static List<Uri> _candidateUris(
    String path, {
    Map<String, String?> query = const {},
  }) {
    return ApiConfig.candidateHosts
        .map((host) => _buildUriFromBase(ApiConfig.baseUrlForHost(host), path, query: query))
        .toList();
  }

  static Future<dynamic> _decodeResponse(http.Response response) async {
    final dynamic data = response.body.isEmpty
        ? null
        : jsonDecode(utf8.decode(response.bodyBytes));
    if (response.statusCode >= 200 && response.statusCode < 300) {
      return data;
    }

    if (data is Map<String, dynamic> && data['error'] != null) {
      throw Exception(data['error']);
    }

    throw Exception('Error ${response.statusCode}');
  }

  static Future<http.Response> _get(
    Uri uri, {
    Map<String, String>? headers,
  }) async {
    try {
      return await http.get(uri, headers: headers).timeout(_requestTimeout);
    } on TimeoutException {
      throw Exception('Tiempo de espera agotado al conectar con el servidor.');
    } on http.ClientException {
      throw Exception('No fue posible conectar con el servidor.');
    }
  }

  static Future<http.Response> _post(
    Uri uri, {
    Map<String, String>? headers,
    Object? body,
  }) async {
    try {
      return await http
          .post(uri, headers: headers, body: body)
          .timeout(_requestTimeout);
    } on TimeoutException {
      throw Exception('Tiempo de espera agotado al conectar con el servidor.');
    } on http.ClientException {
      throw Exception('No fue posible conectar con el servidor.');
    }
  }

  static Future<Map<String, dynamic>> loginMesero({
    required String correo,
    required String clave,
  }) async {
    final response = await _post(
      _buildUri('/api/meseros/login'),
      headers: _headers(),
      body: jsonEncode({'correo': correo, 'clave': clave}),
    );
    final data = await _decodeResponse(response);
    return Map<String, dynamic>.from(data as Map);
  }

  static Future<Map<String, dynamic>> refrescarSesionActual() async {
    Object? lastError;

    for (final uri in _candidateUris('/api/session/refresh')) {
      for (final headers in _headerOptions(authenticated: true)) {
        try {
          final response = await _get(uri, headers: headers);
          final data = await _decodeResponse(response);
          return Map<String, dynamic>.from(data as Map);
        } catch (error) {
          lastError = error;
        }
      }
    }

    throw lastError ?? Exception('No fue posible refrescar la sesion.');
  }

  static List<Map<String, String>> _headerOptions({bool authenticated = false}) {
    if (!authenticated) {
      return <Map<String, String>>[_headers()];
    }

    final options = <Map<String, String>>[];
    try {
      options.add(_headers(authenticated: true));
    } catch (_) {}
    options.add(_headers());
    return options;
  }

  static Future<List<Map<String, dynamic>>> obtenerPedidos() async {
    Object? lastError;

    for (final uri in _candidateUris('/api/pedidos')) {
      for (final headers in _headerOptions(authenticated: true)) {
        try {
          final response = await _get(uri, headers: headers);
          final data = await _decodeResponse(response) as List<dynamic>;
          return data
              .map((item) => Map<String, dynamic>.from(item as Map))
              .toList();
        } catch (error) {
          lastError = error;
        }
      }
    }

    throw lastError ?? Exception('No fue posible obtener los pedidos.');
  }

  static Future<List<Map<String, dynamic>>> obtenerLlamadosMesero({
    String? estado,
  }) async {
    Object? lastError;
    final meseroId = SessionService.idUsuario;

    for (final uri in _candidateUris(
      '/api/mesero/llamados',
      query: {
        'estado': estado,
        'id_usuario': meseroId?.toString(),
      },
    )) {
      for (final headers in _headerOptions(authenticated: true)) {
        try {
          final response = await _get(uri, headers: headers);
          final data = await _decodeResponse(response) as List<dynamic>;
          return data
              .map((item) => Map<String, dynamic>.from(item as Map))
              .toList();
        } catch (error) {
          lastError = error;
        }
      }
    }

    throw lastError ?? Exception('No fue posible obtener los llamados.');
  }

  static Future<List<Map<String, dynamic>>> obtenerMesas() async {
    Object? lastError;
    final meseroId = SessionService.idUsuario;

    for (final uri in _candidateUris(
      '/api/mesas',
      query: {'id_usuario': meseroId?.toString()},
    )) {
      for (final headers in _headerOptions(authenticated: true)) {
        try {
          final response = await _get(uri, headers: headers);
          final data = await _decodeResponse(response) as List<dynamic>;
          return data
              .map((item) => Map<String, dynamic>.from(item as Map))
              .toList();
        } catch (error) {
          lastError = error;
        }
      }
    }

    throw lastError ?? Exception('No fue posible obtener las mesas.');
  }

  static Future<Map<String, dynamic>> atenderLlamadoMesero(int id) async {
    Object? lastError;
    final meseroId = SessionService.idUsuario;

    for (final uri in _candidateUris(
      '/api/mesero/llamados/$id/atender',
      query: {'id_usuario': meseroId?.toString()},
    )) {
      for (final headers in _headerOptions(authenticated: true)) {
        try {
          final response = await _post(uri, headers: headers);
          final data = await _decodeResponse(response);
          return Map<String, dynamic>.from(data as Map);
        } catch (error) {
          lastError = error;
        }
      }
    }

    throw lastError ?? Exception('No fue posible atender el llamado.');
  }

  static Future<Map<String, dynamic>> actualizarEstadoMesa({
    required int mesaId,
    required String estado,
  }) async {
    Object? lastError;
    final meseroId = SessionService.idUsuario;
    final payload = jsonEncode({
      'estado': estado,
      'id_usuario': meseroId,
    });

    for (final uri in _candidateUris(
      '/api/mesas/$mesaId/estado',
      query: {'id_usuario': meseroId?.toString()},
    )) {
      for (final headers in _headerOptions(authenticated: true)) {
        try {
          final response = await _post(uri, headers: headers, body: payload);
          final data = await _decodeResponse(response);
          return Map<String, dynamic>.from(data as Map);
        } catch (error) {
          lastError = error;
        }
      }
    }

    throw lastError ?? Exception('No fue posible actualizar la mesa.');
  }

  static Future<List<Map<String, dynamic>>> obtenerHistorialChat({
    required String participante,
    String? con,
  }) async {
    Object? lastError;
    for (final uri in _candidateUris(
      '/api/chat/historial',
      query: {
        'participante': participante,
        'con': con,
      },
    )) {
      try {
        final response = await _get(
          uri,
          headers: _headers(authenticated: true),
        );
        final data = await _decodeResponse(response) as List<dynamic>;
        return data.map((item) => Map<String, dynamic>.from(item as Map)).toList();
      } catch (error) {
        lastError = error;
      }
    }
    throw lastError ?? Exception('No fue posible obtener el historial del chat.');
  }

  static Future<List<Map<String, dynamic>>> obtenerMenus() async {
    final response = await _get(_buildUri('/api/menus'));
    final data = await _decodeResponse(response) as List<dynamic>;
    return data.map((item) => Map<String, dynamic>.from(item as Map)).toList();
  }

  static Future<List<Map<String, dynamic>>> obtenerProductos({
    int? menuId,
  }) async {
    final response = await _get(
      _buildUri(
        '/api/productos',
        query: {'menu_id': menuId?.toString()},
      ),
    );
    final data = await _decodeResponse(response) as List<dynamic>;
    return data.map((item) => Map<String, dynamic>.from(item as Map)).toList();
  }

  static Future<List<Map<String, dynamic>>> obtenerColaMusica() async {
    Object? lastError;

    for (final uri in _candidateUris('/api/musicas/cola')) {
      for (final headers in _headerOptions(authenticated: true)) {
        try {
          final response = await _get(uri, headers: headers);
          final data = await _decodeResponse(response) as List<dynamic>;
          return data
              .map((item) => Map<String, dynamic>.from(item as Map))
              .toList();
        } catch (error) {
          lastError = error;
        }
      }
    }

    throw lastError ?? Exception('No fue posible obtener la cola musical.');
  }

  static Future<Map<String, dynamic>> enviarMensajeChat({
    required String participante,
    required String destinatario,
    required String mensaje,
  }) async {
    Object? lastError;
    final payload = jsonEncode({
      'participante': participante,
      'destinatario': destinatario,
      'mensaje': mensaje,
    });
    for (final uri in _candidateUris('/api/chat/enviar')) {
      try {
        final response = await _post(
          uri,
          headers: _headers(authenticated: true),
          body: payload,
        );
        final data = await _decodeResponse(response);
        return Map<String, dynamic>.from(data as Map);
      } catch (error) {
        lastError = error;
      }
    }
    throw lastError ?? Exception('No fue posible enviar el mensaje.');
  }
}
