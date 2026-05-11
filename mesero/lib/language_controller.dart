import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class LanguageController {
  static const _storage = FlutterSecureStorage();
  static const _key = 'bongusto_language';
  static final ValueNotifier<String> language = ValueNotifier<String>('es');
  static const Map<String, String> _esToEn = {
    'Inicio': 'Home',
    'Perfil': 'Profile',
    'Pedidos': 'Orders',
    'Pedido': 'Order',
    'Llamados': 'Calls',
    'Chat': 'Chat',
    'Menu': 'Menu',
    'Menú': 'Menu',
    'Musica': 'Music',
    'Música': 'Music',
    'Mesas': 'Tables',
    'Mesa': 'Table',
    'OPERACION MESEROS': 'WAITER OPERATIONS',
    'Todo el piso en un solo panel.': 'The whole floor in one panel.',
    'Accesos del turno': 'Shift shortcuts',
    'Abrir': 'Open',
    'Pedidos creados por clientes.': 'Orders created by customers.',
    'Clientes que pidieron mesero desde la app.':
        'Customers who requested a waiter from the app.',
    'Aqui puedes hablar con el administrador.':
        'Here you can talk to the administrator.',
    'Vista del menu y precios.': 'Menu and prices view.',
    'Cola actual de solicitudes musicales de clientes.':
        'Current queue of customer music requests.',
    'Mesas con cliente y productos asignados por pedido.':
        'Tables with customer and products assigned by order.',
    'Reintentar': 'Retry',
    'Buscar': 'Search',
    'Filtrar': 'Filter',
    'Guardar': 'Save',
    'Enviar': 'Send',
    'Cancelar': 'Cancel',
    'Confirmar': 'Confirm',
    'Marcar atendido': 'Mark as handled',
    'Llamado marcado como atendido.': 'Call marked as handled.',
    'No se pudo actualizar': 'Could not update',
    'Pagada': 'Paid',
    'Pagado': 'Paid',
    'Liberar': 'Release',
    'Actualizando': 'Updating',
    'Disponible': 'Available',
    'Ocupada': 'Occupied',
    'Ocupado': 'Occupied',
    'Pendiente': 'Pending',
    'Completado': 'Completed',
    'Completada': 'Completed',
    'Cancelado': 'Canceled',
    'Cancelada': 'Canceled',
    'Activo': 'Active',
    'Activa': 'Active',
    'Inactivo': 'Inactive',
    'Inactiva': 'Inactive',
    'Cola de reproducción': 'Playback queue',
    'Cola de reproduccion': 'Playback queue',
    'Contraseña cambiada': 'Password changed',
    'Contrasena cambiada': 'Password changed',
    'Tu contraseña ha sido cambiada exitosamente.':
        'Your password has been changed successfully.',
    'Tu contrasena ha sido cambiada exitosamente.':
        'Your password has been changed successfully.',
    'Volver al inicio de sesión': 'Back to sign in',
    'Volver al inicio de sesion': 'Back to sign in',
    'Iniciar sesión': 'Sign in',
    'Iniciar sesion': 'Sign in',
    'Código enviado': 'Code sent',
    'Codigo enviado': 'Code sent',
    'Enviar código': 'Send code',
    'Enviar codigo': 'Send code',
    'Enviando...': 'Sending...',
    'Ingresa los 6 dígitos': 'Enter the 6 digits',
    'Ingresa los 6 digitos': 'Enter the 6 digits',
    'Primero solicita el código por correo': 'First request the code by email',
    'Primero solicita el codigo por correo': 'First request the code by email',
    'Nueva contraseña': 'New password',
    'Nueva contrasena': 'New password',
    'Confirmar contraseña': 'Confirm password',
    'Confirmar contrasena': 'Confirm password',
    'Contraseña actualizada': 'Password updated',
    'Contrasena actualizada': 'Password updated',
    'Las contraseñas no coinciden': 'Passwords do not match',
    'Las contrasenas no coinciden': 'Passwords do not match',
    'El flujo de recuperación no es válido': 'The recovery flow is not valid',
    'El flujo de recuperacion no es valido': 'The recovery flow is not valid',
  };

  static Future<void> init() async {
    final value = await _storage.read(key: _key);
    language.value = value == 'en' ? 'en' : 'es';
  }

  static Future<String> toggle() async {
    final next = language.value == 'en' ? 'es' : 'en';
    language.value = next;
    await _storage.write(key: _key, value: next);
    return next;
  }

  static String t(String es, String en) => language.value == 'en' ? en : es;

  static String tr(String value) {
    if (language.value != 'en') return value;
    return _esToEn[value.trim()] ?? value;
  }
}
