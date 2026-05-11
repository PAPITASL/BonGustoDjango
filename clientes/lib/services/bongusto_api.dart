// Servicio HTTP central para consumir la API del backend BonGusto.
import 'dart:convert';
import 'dart:async';

import 'package:http/http.dart' as http;

import '../api_config.dart';
import 'session_service.dart';

// Clase utilitaria con metodos estaticos para cada endpoint principal.
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
    final filteredQuery = <String, String>{};
    for (final entry in query.entries) {
      final value = entry.value;
      if (value != null && value.isNotEmpty) {
        filteredQuery[entry.key] = value;
      }
    }

    return Uri.parse(
      '${ApiConfig.baseUrl}$path',
    ).replace(queryParameters: filteredQuery.isEmpty ? null : filteredQuery);
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

  static Future<Map<String, dynamic>> login({
    required String correo,
    required String clave,
  }) async {
    final response = await _post(
      _buildUri('/api/clientes/login'),
      headers: _headers(),
      body: jsonEncode({'correo': correo, 'clave': clave}),
    );
    final data = await _decodeResponse(response);
    return Map<String, dynamic>.from(data as Map);
  }

  static Future<Map<String, dynamic>> refrescarSesionActual() async {
    final response = await _get(
      _buildUri('/api/session/refresh'),
      headers: _headers(authenticated: true),
    );
    final data = await _decodeResponse(response);
    return Map<String, dynamic>.from(data as Map);
  }

  static Future<Map<String, dynamic>> actualizarPerfil({
    required String nombreCompleto,
    required String correo,
    String telefono = '',
  }) async {
    final response = await _post(
      _buildUri('/api/perfil/actualizar'),
      headers: _headers(authenticated: true),
      body: jsonEncode({
        'nombre_completo': nombreCompleto,
        'correo': correo,
        'telefono': telefono,
      }),
    );
    final data = await _decodeResponse(response);
    return Map<String, dynamic>.from(data as Map);
  }

  static Future<Map<String, dynamic>> cambiarContrasenaPerfil({
    required String contrasenaActual,
    required String nuevaContrasena,
    required String confirmarContrasena,
  }) async {
    final response = await _post(
      _buildUri('/api/perfil/cambiar-contrasena'),
      headers: _headers(authenticated: true),
      body: jsonEncode({
        'contrasena_actual': contrasenaActual,
        'nueva_contrasena': nuevaContrasena,
        'confirmar_contrasena': confirmarContrasena,
      }),
    );
    final data = await _decodeResponse(response);
    return Map<String, dynamic>.from(data as Map);
  }

  static Future<Map<String, dynamic>> cambiarIdioma(String language) async {
    final response = await _post(
      _buildUri('/api/language'),
      headers: _headers(),
      body: jsonEncode({'language': language}),
    );
    final data = await _decodeResponse(response);
    return Map<String, dynamic>.from(data as Map);
  }

  static Future<Map<String, dynamic>> traducirTextos({
    required String language,
    required List<String> texts,
  }) async {
    final response = await _post(
      _buildUri('/api/translate'),
      headers: _headers(),
      body: jsonEncode({'language': language, 'texts': texts}),
    );
    final data = await _decodeResponse(response);
    return Map<String, dynamic>.from(data as Map);
  }

  static Future<Map<String, dynamic>> registrarCliente({
    required String nombre,
    required String correo,
    required String clave,
    String telefono = '',
  }) async {
    final response = await _post(
      _buildUri('/api/clientes/register'),
      headers: _headers(),
      body: jsonEncode({
        'nombre': nombre,
        'correo': correo,
        'clave': clave,
        'telefono': telefono,
      }),
    );
    final data = await _decodeResponse(response);
    return Map<String, dynamic>.from(data as Map);
  }

  static Future<Map<String, dynamic>> solicitarCodigoRecuperacion({
    required String correo,
  }) async {
    final response = await _post(
      _buildUri('/api/password/request-code'),
      headers: _headers(),
      body: jsonEncode({'correo': correo}),
    );
    final data = await _decodeResponse(response);
    return Map<String, dynamic>.from(data as Map);
  }

  static Future<Map<String, dynamic>> solicitarEnlaceRecuperacion({
    required String correo,
  }) async {
    final response = await _post(
      _buildUri('/api/auth/forgot-password'),
      headers: _headers(),
      body: jsonEncode({'correo': correo}),
    );
    final data = await _decodeResponse(response);
    return Map<String, dynamic>.from(data as Map);
  }

  static Future<Map<String, dynamic>> restablecerContrasena({
    required String correo,
    required String codigo,
    required String password,
    required String passwordConfirm,
  }) async {
    final response = await _post(
      _buildUri('/api/password/reset'),
      headers: _headers(),
      body: jsonEncode({
        'correo': correo,
        'codigo': codigo,
        'password': password,
        'password_confirm': passwordConfirm,
      }),
    );
    final data = await _decodeResponse(response);
    return Map<String, dynamic>.from(data as Map);
  }

  static Future<Map<String, dynamic>> restablecerContrasenaConToken({
    required String token,
    required String password,
    required String passwordConfirm,
  }) async {
    final response = await _post(
      _buildUri('/api/auth/reset-password'),
      headers: _headers(),
      body: jsonEncode({
        'token': token,
        'nueva_password': password,
        'password_confirm': passwordConfirm,
      }),
    );
    final data = await _decodeResponse(response);
    return Map<String, dynamic>.from(data as Map);
  }

  static Future<List<Map<String, dynamic>>> obtenerMenus() async {
    final response = await _get(_buildUri('/api/menus'));
    final data = await _decodeResponse(response) as List<dynamic>;
    return data.map((item) => Map<String, dynamic>.from(item as Map)).toList();
  }

  static Future<List<Map<String, dynamic>>> obtenerCategorias() async {
    final response = await _get(_buildUri('/api/categorias'));
    final data = await _decodeResponse(response) as List<dynamic>;
    return data.map((item) => Map<String, dynamic>.from(item as Map)).toList();
  }

  static Future<List<Map<String, dynamic>>> obtenerProductos({
    int? categoriaId,
    int? menuId,
    bool destacados = false,
  }) async {
    final response = await _get(
      _buildUri(
        '/api/productos',
        query: {
          'categoria_id': categoriaId?.toString(),
          'menu_id': menuId?.toString(),
          'destacados': destacados ? '1' : null,
        },
      ),
    );
    final data = await _decodeResponse(response) as List<dynamic>;
    return data.map((item) => Map<String, dynamic>.from(item as Map)).toList();
  }

  static Future<Map<String, dynamic>> crearPedido({
    required int idUsuario,
    required double totalPedido,
    required List<Map<String, dynamic>> items,
    String tipoPedido = 'restaurante',
    int? mesaId,
  }) async {
    final body = <String, dynamic>{
      'id_usuario': idUsuario,
      'id_restaurante': 1,
      'fecha_pedido': DateTime.now().toIso8601String().split('T').first,
      'total_pedido': totalPedido,
      'items': items,
      'tipo_pedido': tipoPedido,
    };
    if (mesaId != null) {
      body['mesa_id'] = mesaId;
    }
    final response = await _post(
      _buildUri('/api/pedidos'),
      headers: _headers(authenticated: true),
      body: jsonEncode(body),
    );
    final data = await _decodeResponse(response);
    return Map<String, dynamic>.from(data as Map);
  }

  static Future<List<Map<String, dynamic>>> obtenerPedidosUsuario(
    int idUsuario,
  ) async {
    final response = await _get(
      _buildUri('/api/pedidos', query: {'id_usuario': idUsuario.toString()}),
      headers: _headers(authenticated: true),
    );
    final data = await _decodeResponse(response) as List<dynamic>;
    return data.map((item) => Map<String, dynamic>.from(item as Map)).toList();
  }

  static Future<List<Map<String, dynamic>>> obtenerMusicas() async {
    final response = await _get(_buildUri('/api/musicas'));
    final data = await _decodeResponse(response) as List<dynamic>;
    return data.map((item) => Map<String, dynamic>.from(item as Map)).toList();
  }

  static Future<List<Map<String, dynamic>>> obtenerColaMusical() async {
    final response = await _get(
      _buildUri('/api/musica/cola'),
      headers: _headers(authenticated: true),
    );
    final data = await _decodeResponse(response) as List<dynamic>;
    return data.map((item) => Map<String, dynamic>.from(item as Map)).toList();
  }

  static Future<Map<String, dynamic>> obtenerSnapshotMusica() async {
    final response = await _get(
      _buildUri('/api/musica/snapshot'),
      headers: _headers(authenticated: true),
    );
    final data = await _decodeResponse(response);
    return Map<String, dynamic>.from(data as Map);
  }

  static Future<Map<String, dynamic>> solicitarMusica({
    required int idUsuario,
    int? idMusica,
    String? nombreMusica,
    String? artistaMusica,
    int? idReserva,
  }) async {
    final response = await _post(
      _buildUri('/api/musica/solicitar'),
      headers: _headers(authenticated: true),
      body: jsonEncode({
        'id_usuario': idUsuario,
        'id_musica': idMusica,
        'nombre_musica': nombreMusica,
        'artista_musica': artistaMusica,
        'id_res': idReserva,
        'mesa_id': SessionService.mesaId,
      }),
    );
    final data = await _decodeResponse(response);
    return Map<String, dynamic>.from(data as Map);
  }

  static Future<Map<String, dynamic>> enviarCalificacion({
    required int idUsuario,
    int? idPedido,
    required int calificacionComida,
    required int calificacionServicio,
    required int calificacionAmbiente,
    String observaciones = '',
  }) async {
    final response = await _post(
      _buildUri('/api/calificaciones'),
      headers: _headers(authenticated: true),
      body: jsonEncode({
        'id_usuario': idUsuario,
        'id_pedido': idPedido,
        'calificacion_comida': calificacionComida,
        'calificacion_servicio': calificacionServicio,
        'calificacion_ambiente': calificacionAmbiente,
        'observaciones': observaciones,
      }),
    );
    final data = await _decodeResponse(response);
    return Map<String, dynamic>.from(data as Map);
  }

  static Future<Map<String, dynamic>> obtenerPedidoPendienteCalificacion({
    required int idUsuario,
  }) async {
    final response = await _get(
      _buildUri('/api/calificaciones/pendiente', query: {
        'id_usuario': idUsuario.toString(),
      }),
      headers: _headers(authenticated: true),
    );
    final data = await _decodeResponse(response);
    return Map<String, dynamic>.from(data as Map);
  }

  static Future<Map<String, dynamic>> llamarMesero({
    required int idUsuario,
    String mensaje = 'Cliente solicita mesero',
  }) async {
    final response = await _post(
      _buildUri('/api/mesero/llamados'),
      headers: _headers(authenticated: true),
      body: jsonEncode({
        'id_usuario': idUsuario,
        'mesa_id': SessionService.mesaId,
        'mensaje': mensaje,
      }),
    );
    final data = await _decodeResponse(response);
    return Map<String, dynamic>.from(data as Map);
  }

  static Future<Map<String, dynamic>> solicitarPago({
    required String metodoPago,
    int? idPedido,
    int? mesaId,
  }) async {
    final body = <String, dynamic>{
      'metodo_pago': metodoPago,
      'id_pedido': idPedido,
    };
    if (mesaId != null) {
      body['mesa_id'] = mesaId;
    }
    final response = await _post(
      _buildUri('/api/pagos/solicitudes'),
      headers: _headers(authenticated: true),
      body: jsonEncode(body),
    );
    final data = await _decodeResponse(response);
    return Map<String, dynamic>.from(data as Map);
  }

  static Future<Map<String, dynamic>> asignarMesa({
    required int idUsuario,
    int? mesaId,
    int? numeroMesa,
    String? codigoMesa,
  }) async {
    final response = await _post(
      _buildUri('/api/mesas/seleccionar'),
      headers: _headers(authenticated: true),
      body: jsonEncode({
        'id_usuario': idUsuario,
        'mesa_id': mesaId,
        'numero_mesa': numeroMesa,
        'codigo_mesa': codigoMesa,
      }),
    );
    final data = await _decodeResponse(response);
    return Map<String, dynamic>.from(data as Map);
  }

  static Future<List<Map<String, dynamic>>> obtenerMesas() async {
    final response = await _get(
      _buildUri('/api/mesas'),
      headers: _headers(authenticated: true),
    );
    final data = await _decodeResponse(response) as List<dynamic>;
    return data.map((item) => Map<String, dynamic>.from(item as Map)).toList();
  }

  static Future<Map<String, dynamic>> obtenerMiMesa() async {
    final response = await _get(
      _buildUri('/api/mi-mesa'),
      headers: _headers(authenticated: true),
    );
    final data = await _decodeResponse(response);
    return Map<String, dynamic>.from(data as Map);
  }

  static Future<Map<String, dynamic>> obtenerNotificaciones() async {
    final response = await _get(
      _buildUri('/api/notificaciones'),
      headers: _headers(authenticated: true),
    );
    final data = await _decodeResponse(response);
    return Map<String, dynamic>.from(data as Map);
  }

  static Future<Map<String, dynamic>> marcarNotificacionLeida(
    int idNotificacion,
  ) async {
    final response = await _post(
      _buildUri('/api/notificaciones/$idNotificacion/leer'),
      headers: _headers(authenticated: true),
    );
    final data = await _decodeResponse(response);
    return Map<String, dynamic>.from(data as Map);
  }

  static Future<Map<String, dynamic>> marcarTodasLasNotificacionesLeidas() async {
    final response = await _post(
      _buildUri('/api/notificaciones/leer-todas'),
      headers: _headers(authenticated: true),
    );
    final data = await _decodeResponse(response);
    return Map<String, dynamic>.from(data as Map);
  }

  static Future<Map<String, dynamic>> obtenerSnapshotOperacion() async {
    final response = await _get(
      _buildUri('/api/operacion/snapshot'),
      headers: _headers(authenticated: true),
    );
    final data = await _decodeResponse(response);
    return Map<String, dynamic>.from(data as Map);
  }
}
