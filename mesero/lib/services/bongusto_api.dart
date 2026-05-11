// ===== Servicio `bongusto_api.dart` | Reune todas las peticiones HTTP que la app Flutter envia al backend Django. =====
import 'dart:convert';
import 'dart:async';

import 'package:http/http.dart' as http;

import '../api_config.dart';
import 'session_service.dart';

// ===== Clase `BongustoApi` | Encapsula endpoints, headers, manejo de errores y transformacion de respuestas. =====
class BongustoApi {
  static const Duration _requestTimeout = Duration(seconds: 6);

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

  static Map<String, dynamic> _asMap(dynamic data, String contexto) {
    if (data is Map) {
      return Map<String, dynamic>.from(data);
    }
    throw Exception('Respuesta invalida en $contexto (se esperaba objeto JSON).');
  }

  static List<Map<String, dynamic>> _asListOfMaps(dynamic data, String contexto) {
    if (data is List) {
      return data
          .where((item) => item is Map)
          .map((item) => Map<String, dynamic>.from(item as Map))
          .toList();
    }
    throw Exception('Respuesta invalida en $contexto (se esperaba lista JSON).');
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
    Object? lastError;
    final payload = jsonEncode({'correo': correo, 'clave': clave});

    for (final uri in _candidateUris('/api/meseros/login')) {
      try {
        final response = await _post(
          uri,
          headers: _headers(),
          body: payload,
        );
        final data = await _decodeResponse(response);
        return _asMap(data, 'login mesero');
      } catch (error) {
        lastError = error;
      }
    }

    throw lastError ?? Exception('No fue posible iniciar sesion con el servidor.');
  }

  static Future<Map<String, dynamic>> solicitarCodigoRecuperacion({
    required String correo,
  }) async {
    Object? lastError;
    final payload = jsonEncode({'correo': correo});

    for (final uri in _candidateUris('/api/password/request-code')) {
      try {
        final response = await _post(
          uri,
          headers: _headers(),
          body: payload,
        );
        final data = await _decodeResponse(response);
        return _asMap(data, 'solicitar codigo de recuperacion');
      } catch (error) {
        lastError = error;
      }
    }

    throw lastError ?? Exception('No fue posible enviar el codigo de recuperacion.');
  }

  static Future<Map<String, dynamic>> solicitarEnlaceRecuperacion({
    required String correo,
  }) async {
    Object? lastError;
    final payload = jsonEncode({'correo': correo});

    for (final uri in _candidateUris('/api/auth/forgot-password')) {
      try {
        final response = await _post(
          uri,
          headers: _headers(),
          body: payload,
        );
        final data = await _decodeResponse(response);
        return _asMap(data, 'solicitar enlace de recuperacion');
      } catch (error) {
        lastError = error;
      }
    }

    throw lastError ?? Exception('No fue posible enviar el enlace de recuperacion.');
  }

  static Future<Map<String, dynamic>> restablecerContrasena({
    required String correo,
    required String codigo,
    required String password,
    required String passwordConfirm,
  }) async {
    Object? lastError;
    final payload = jsonEncode({
      'correo': correo,
      'codigo': codigo,
      'password': password,
      'password_confirm': passwordConfirm,
    });

    for (final uri in _candidateUris('/api/password/reset')) {
      try {
        final response = await _post(
          uri,
          headers: _headers(),
          body: payload,
        );
        final data = await _decodeResponse(response);
        return _asMap(data, 'restablecer contrasena');
      } catch (error) {
        lastError = error;
      }
    }

    throw lastError ?? Exception('No fue posible restablecer la contrasena.');
  }

  static Future<Map<String, dynamic>> restablecerContrasenaConToken({
    required String token,
    required String password,
    required String passwordConfirm,
  }) async {
    Object? lastError;
    final payload = jsonEncode({
      'token': token,
      'nueva_password': password,
      'password_confirm': passwordConfirm,
    });

    for (final uri in _candidateUris('/api/auth/reset-password')) {
      try {
        final response = await _post(
          uri,
          headers: _headers(),
          body: payload,
        );
        final data = await _decodeResponse(response);
        return _asMap(data, 'restablecer contrasena con token');
      } catch (error) {
        lastError = error;
      }
    }

    throw lastError ?? Exception('No fue posible restablecer la contrasena.');
  }

  static Future<Map<String, dynamic>> refrescarSesionActual() async {
    Object? lastError;

    for (final uri in _candidateUris('/api/session/refresh')) {
      for (final headers in _headerOptions(authenticated: true)) {
        try {
          final response = await _get(uri, headers: headers);
          final data = await _decodeResponse(response);
          return _asMap(data, 'refrescar sesion');
        } catch (error) {
          lastError = error;
        }
      }
    }

    throw lastError ?? Exception('No fue posible refrescar la sesion.');
  }

  static Future<Map<String, dynamic>> cambiarIdioma(String language) async {
    Object? lastError;
    final payload = jsonEncode({'language': language});

    for (final uri in _candidateUris('/api/language')) {
      try {
        final response = await _post(
          uri,
          headers: _headers(),
          body: payload,
        );
        final data = await _decodeResponse(response);
        return _asMap(data, 'cambiar idioma');
      } catch (error) {
        lastError = error;
      }
    }

    throw lastError ?? Exception('No fue posible cambiar el idioma.');
  }

  static Future<Map<String, dynamic>> traducirTextos({
    required String language,
    required List<String> texts,
  }) async {
    Object? lastError;
    final payload = jsonEncode({'language': language, 'texts': texts});

    for (final uri in _candidateUris('/api/translate')) {
      try {
        final response = await _post(
          uri,
          headers: _headers(),
          body: payload,
        );
        final data = await _decodeResponse(response);
        return _asMap(data, 'traducir textos');
      } catch (error) {
        lastError = error;
      }
    }

    throw lastError ?? Exception('No fue posible traducir los textos.');
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
          final data = await _decodeResponse(response);
          return _asListOfMaps(data, 'obtener pedidos');
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
          final data = await _decodeResponse(response);
          return _asListOfMaps(data, 'obtener llamados');
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
          final data = await _decodeResponse(response);
          return _asListOfMaps(data, 'obtener mesas');
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
          return _asMap(data, 'atender llamado');
        } catch (error) {
          lastError = error;
        }
      }
    }

    throw lastError ?? Exception('No fue posible atender el llamado.');
  }

  static Future<List<Map<String, dynamic>>> obtenerSolicitudesPago({
    String? estado,
  }) async {
    Object? lastError;
    final meseroId = SessionService.idUsuario;

    for (final uri in _candidateUris(
      '/api/pagos/solicitudes',
      query: {
        'estado': estado,
        'id_usuario': meseroId?.toString(),
      },
    )) {
      for (final headers in _headerOptions(authenticated: true)) {
        try {
          final response = await _get(uri, headers: headers);
          final data = await _decodeResponse(response);
          return _asListOfMaps(data, 'obtener solicitudes de pago');
        } catch (error) {
          lastError = error;
        }
      }
    }

    throw lastError ?? Exception('No fue posible obtener las solicitudes de pago.');
  }

  static Future<Map<String, dynamic>> actualizarSolicitudPago({
    required int idSolicitudPago,
    required String estado,
  }) async {
    Object? lastError;
    final meseroId = SessionService.idUsuario;
    final payload = jsonEncode({
      'estado': estado,
      'id_usuario': meseroId,
    });

    for (final uri in _candidateUris(
      '/api/pagos/solicitudes/$idSolicitudPago/estado',
      query: {'id_usuario': meseroId?.toString()},
    )) {
      for (final headers in _headerOptions(authenticated: true)) {
        try {
          final response = await _post(uri, headers: headers, body: payload);
          final data = await _decodeResponse(response);
          return _asMap(data, 'actualizar solicitud de pago');
        } catch (error) {
          lastError = error;
        }
      }
    }

    throw lastError ?? Exception('No fue posible actualizar la solicitud de pago.');
  }

  static Future<Map<String, dynamic>> actualizarEstadoPedido({
    required int pedidoId,
    required String estado,
  }) async {
    Object? lastError;
    final meseroId = SessionService.idUsuario;
    final payload = jsonEncode({
      'estado': estado,
      'id_usuario': meseroId,
    });

    for (final uri in _candidateUris(
      '/api/pedidos/$pedidoId/estado',
      query: {'id_usuario': meseroId?.toString()},
    )) {
      for (final headers in _headerOptions(authenticated: true)) {
        try {
          final response = await _post(uri, headers: headers, body: payload);
          final data = await _decodeResponse(response);
          return _asMap(data, 'actualizar estado pedido');
        } catch (error) {
          lastError = error;
        }
      }
    }

    throw lastError ?? Exception('No fue posible actualizar el pedido.');
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
          return _asMap(data, 'actualizar estado mesa');
        } catch (error) {
          lastError = error;
        }
      }
    }

    throw lastError ?? Exception('No fue posible actualizar la mesa.');
  }

  static Future<Map<String, dynamic>> confirmarPagoMesa(int mesaId) async {
    Object? lastError;
    final meseroId = SessionService.idUsuario;

    for (final uri in _candidateUris(
      '/api/mesas/$mesaId/confirmar-pago',
      query: {'id_usuario': meseroId?.toString()},
    )) {
      for (final headers in _headerOptions(authenticated: true)) {
        try {
          final response = await _post(uri, headers: headers, body: jsonEncode({'id_usuario': meseroId}));
          final data = await _decodeResponse(response);
          return _asMap(data, 'confirmar pago mesa');
        } catch (error) {
          lastError = error;
        }
      }
    }

    throw lastError ?? Exception('No fue posible confirmar el pago de la mesa.');
  }

  static Future<Map<String, dynamic>> liberarMesa({
    required int mesaId,
    bool forzada = false,
  }) async {
    Object? lastError;
    final meseroId = SessionService.idUsuario;
    final payload = jsonEncode({
      'id_usuario': meseroId,
      'forzada': forzada,
    });

    for (final uri in _candidateUris(
      '/api/mesas/$mesaId/liberar',
      query: {'id_usuario': meseroId?.toString()},
    )) {
      for (final headers in _headerOptions(authenticated: true)) {
        try {
          final response = await _post(uri, headers: headers, body: payload);
          final data = await _decodeResponse(response);
          return _asMap(data, 'liberar mesa');
        } catch (error) {
          lastError = error;
        }
      }
    }

    throw lastError ?? Exception('No fue posible liberar la mesa.');
  }

  static Future<Map<String, dynamic>> marcarMesaEnLimpieza(int mesaId) async {
    return actualizarEstadoMesa(mesaId: mesaId, estado: 'en_limpieza');
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
        final data = await _decodeResponse(response);
        return _asListOfMaps(data, 'obtener historial chat');
      } catch (error) {
        lastError = error;
      }
    }
    throw lastError ?? Exception('No fue posible obtener el historial del chat.');
  }

  static Future<List<Map<String, dynamic>>> obtenerMenus() async {
    Object? lastError;

    for (final uri in _candidateUris('/api/menus')) {
      try {
        final response = await _get(uri);
        final data = await _decodeResponse(response);
        return _asListOfMaps(data, 'obtener menus');
      } catch (error) {
        lastError = error;
      }
    }

    throw lastError ?? Exception('No fue posible obtener los menus.');
  }

  static Future<List<Map<String, dynamic>>> obtenerMusicas() async {
    Object? lastError;

    for (final uri in _candidateUris('/api/musicas')) {
      try {
        final response = await _get(uri);
        final data = await _decodeResponse(response);
        return _asListOfMaps(data, 'obtener musicas');
      } catch (error) {
        lastError = error;
      }
    }

    throw lastError ?? Exception('No fue posible obtener el catalogo musical.');
  }

  static Future<List<Map<String, dynamic>>> obtenerProductos({
    int? menuId,
  }) async {
    Object? lastError;

    for (final uri in _candidateUris(
      '/api/productos',
      query: {'menu_id': menuId?.toString()},
    )) {
      try {
        final response = await _get(uri);
        final data = await _decodeResponse(response);
        return _asListOfMaps(data, 'obtener productos');
      } catch (error) {
        lastError = error;
      }
    }

    throw lastError ?? Exception('No fue posible obtener los productos.');
  }

  static Future<List<Map<String, dynamic>>> obtenerColaMusica() async {
    Object? lastError;

    for (final uri in _candidateUris('/api/musica/cola')) {
      for (final headers in _headerOptions(authenticated: true)) {
        try {
          final response = await _get(uri, headers: headers);
          final data = await _decodeResponse(response);
          return _asListOfMaps(data, 'obtener cola musica');
        } catch (error) {
          lastError = error;
        }
      }
    }

    throw lastError ?? Exception('No fue posible obtener la cola musical.');
  }

  static Future<Map<String, dynamic>> obtenerSnapshotMusica() async {
    Object? lastError;

    for (final uri in _candidateUris('/api/musica/snapshot')) {
      for (final headers in _headerOptions(authenticated: true)) {
        try {
          final response = await _get(uri, headers: headers);
          final data = await _decodeResponse(response);
          return _asMap(data, 'snapshot musica');
        } catch (error) {
          lastError = error;
        }
      }
    }

    throw lastError ?? Exception('No fue posible obtener el estado musical.');
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
        return _asMap(data, 'enviar mensaje chat');
      } catch (error) {
        lastError = error;
      }
    }
    throw lastError ?? Exception('No fue posible enviar el mensaje.');
  }

  static Future<Map<String, dynamic>> obtenerSnapshotOperacion() async {
    Object? lastError;

    for (final uri in _candidateUris('/api/operacion/snapshot')) {
      for (final headers in _headerOptions(authenticated: true)) {
        try {
          final response = await _get(uri, headers: headers);
          final data = await _decodeResponse(response);
          return _asMap(data, 'snapshot operacion');
        } catch (error) {
          lastError = error;
        }
      }
    }

    throw lastError ?? Exception('No fue posible obtener el snapshot operativo.');
  }
}
