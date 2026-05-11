import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class LanguageController {
  static const _storage = FlutterSecureStorage();
  static const _key = 'bongusto_language';
  static final ValueNotifier<String> language = ValueNotifier<String>('es');
  static const Map<String, String> _esToEn = {
    'Inicio': 'Home',
    'Pedidos': 'Orders',
    'Mis pedidos': 'My orders',
    'Pedido': 'Order',
    'Mapa': 'Map',
    'Perfil': 'Profile',
    'Menu': 'Menu',
    'Menú': 'Menu',
    'Menus': 'Menus',
    'Menús': 'Menus',
    'Productos': 'Products',
    'Producto': 'Product',
    'Restaurante': 'Restaurant',
    'Notificaciones': 'Notifications',
    'Música': 'Music',
    'Musica': 'Music',
    'Cola de reproducción': 'Playback queue',
    'Pedir canción': 'Request song',
    'Pedir cancion': 'Request song',
    'Entrar al restaurante': 'Enter restaurant',
    'Pedir para llevar': 'Order takeout',
    'Reservar por WhatsApp': 'Reserve by WhatsApp',
    'Desde aqui entras al restaurante o haces un pedido para llevar.':
        'From here you can enter the restaurant or place a takeout order.',
    'EXPERIENCIA DESTACADA': 'FEATURED EXPERIENCE',
    'Platos listos para pedir': 'Dishes ready to order',
    'Todavia no hay platos destacados para mostrar en Santa Juana.':
        'There are no featured dishes to show yet.',
    'Disponible ahora en la carta de Santa Juana.':
        'Available now on the BonGusto menu.',
    'Pedir': 'Order',
    'Pagar': 'Pay',
    'Carrito': 'Cart',
    'Volver al carrito': 'Back to cart',
    'Reintentar': 'Retry',
    'Buscar': 'Search',
    'Filtrar': 'Filter',
    'Todos': 'All',
    'Todas': 'All',
    'Categoría': 'Category',
    'Categoria': 'Category',
    'Categorías': 'Categories',
    'Categorias': 'Categories',
    'Destacados del menu': 'Menu highlights',
    'Explorar por categoria': 'Browse by category',
    'Buscar platos, categorías o antojos...':
        'Search dishes, categories or cravings...',
    'Buscar menú, brunch, bebidas, postres...':
        'Search menu, brunch, drinks, desserts...',
    'Guardar': 'Save',
    'Enviar': 'Send',
    'Cancelar': 'Cancel',
    'Confirmar': 'Confirm',
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
    'Volver al inicio de sesión': 'Back to sign in',
    'Volver al inicio de sesion': 'Back to sign in',
    'Iniciar sesión': 'Sign in',
    'Iniciar sesion': 'Sign in',
    'Regístrate': 'Sign up',
    'Registrate': 'Sign up',
    'No tengo una cuenta, ': "I don't have an account, ",
    'Queremos saber tu opinion': 'We want your opinion',
    'Debes iniciar sesion para calificar.': 'You must sign in to rate.',
    'Por favor completa todas las calificaciones.':
        'Please complete all ratings.',
    'Gracias por tu calificacion.': 'Thanks for your rating.',
    'Pendiente': 'Pending',
    'Completado': 'Completed',
    'Completada': 'Completed',
    'Cancelado': 'Canceled',
    'Cancelada': 'Canceled',
    'Pagado': 'Paid',
    'Pagada': 'Paid',
    'Activo': 'Active',
    'Activa': 'Active',
    'Inactivo': 'Inactive',
    'Inactiva': 'Inactive',
    'Leído': 'Read',
    'Leido': 'Read',
    'No leído': 'Unread',
    'No leido': 'Unread',
    'Feliz cumpleaños': 'Happy birthday',
    'Descuento': 'Discount',
    'Promoción': 'Promotion',
    'Promocion': 'Promotion',
    'Evento especial': 'Special event',
    'Invitación': 'Invitation',
    'Invitacion': 'Invitation',
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
