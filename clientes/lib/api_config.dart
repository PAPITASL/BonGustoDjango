// Archivo de configuracion global para construir la URL base de la API.
import 'package:flutter/foundation.dart';
import 'dart:io' show Platform;

// Clase utilitaria que resuelve host, puerto y esquema segun el entorno.
class ApiConfig {
  static const String _defaultLocalHost = '127.0.0.1';
  static const String _defaultRemoteHost = '192.168.10.12';
  static const String _androidEmulatorHost = '10.0.2.2';
  static const String _defaultPort = '8001';
  static const String _schemeFromEnv = String.fromEnvironment(
    'API_SCHEME',
    defaultValue: 'http',
  );
  static const String _hostFromEnv = String.fromEnvironment('API_HOST');
  static const String _portFromEnv = String.fromEnvironment('API_PORT');

  static bool get isSecureTransport => scheme == 'https';

  static String get scheme => _schemeFromEnv.trim().isEmpty
      ? 'http'
      : _schemeFromEnv.trim().toLowerCase();

  static String get host {
    if (_hostFromEnv.trim().isNotEmpty) {
      return _hostFromEnv.trim();
    }

    if (kIsWeb ||
        defaultTargetPlatform == TargetPlatform.windows ||
        defaultTargetPlatform == TargetPlatform.linux ||
        defaultTargetPlatform == TargetPlatform.macOS) {
      return _defaultLocalHost;
    }
    if (!kIsWeb && Platform.isAndroid) {
      return _defaultLocalHost;
    }
    return _defaultRemoteHost;
  }

  static String get port =>
      _portFromEnv.trim().isEmpty ? _defaultPort : _portFromEnv.trim();

  static String get baseUrl => '$scheme://$host:$port';

  static String baseUrlForHost(String host) => '$scheme://$host:$port';

  static List<String> get candidateHosts {
    final preferredHost = host;
    final hosts = <String>[
      preferredHost,
      if (_hostFromEnv.trim().isNotEmpty) _hostFromEnv.trim(),
      _defaultLocalHost,
      _androidEmulatorHost,
      _defaultRemoteHost,
    ];
    return hosts.toSet().toList();
  }
}
