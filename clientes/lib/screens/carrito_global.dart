// Estructura global que mantiene los productos agregados al carrito.
import '../services/bongusto_api.dart';
import '../services/session_service.dart';
import 'producto_global.dart';

// Clase estatica para compartir el carrito entre varias pantallas.
class CarritoGlobal {
  static final List<Producto> _productos = [];
  static bool _syncInFlight = false;
  static bool _syncPendiente = false;
  static int _revision = 0;
  static bool _ultimaSyncTeniaItems = false;

  static List<Producto> get productos => List.unmodifiable(_productos);

  static void agregarProducto(Producto producto) {
    final index = _productos.indexWhere(
      (item) => item.idProducto == producto.idProducto,
    );
    if (index >= 0) {
      _productos[index].cantidad += producto.cantidad;
      _marcarCambio();
      return;
    }
    _productos.add(producto.copia());
    _marcarCambio();
  }

  static void eliminarProductoEn(int index) {
    _productos.removeAt(index);
    _marcarCambio();
  }

  static void cambiarCantidadEn(int index, int nuevaCantidad) {
    if (index < 0 || index >= _productos.length) {
      return;
    }

    if (nuevaCantidad <= 0) {
      eliminarProductoEn(index);
      return;
    }

    _productos[index].cantidad = nuevaCantidad;
    _marcarCambio();
  }

  static double calcularTotal() {
    return _productos.fold(
      0,
      (suma, item) => suma + (item.precio * item.cantidad),
    );
  }

  static int totalItems() {
    return _productos.fold(0, (suma, item) => suma + item.cantidad);
  }

  static void vaciarCarrito() {
    _productos.clear();
    _marcarCambio();
  }

  static Future<void> sincronizarConBackend() async {
    final tipoPedido = SessionService.tipoPedido;
    if (tipoPedido == 'para_llevar') {
      return;
    }

    final idUsuario = SessionService.idUsuario;
    final mesaId = SessionService.mesaId;
    if (!SessionService.estaAutenticado || idUsuario == null || mesaId == null) {
      return;
    }

    final tieneItems = _productos.isNotEmpty;
    if (!tieneItems && !_ultimaSyncTeniaItems) {
      return;
    }

    if (_syncInFlight) {
      _syncPendiente = true;
      return;
    }

    _syncInFlight = true;
    final revisionObjetivo = _revision;

    try {
      await BongustoApi.crearPedido(
        idUsuario: idUsuario,
        totalPedido: calcularTotal(),
        items: _productos.map((p) => p.toPedidoItem()).toList(),
        tipoPedido: tipoPedido,
        mesaId: mesaId,
      );
      _ultimaSyncTeniaItems = tieneItems;
    } finally {
      _syncInFlight = false;
      if (_syncPendiente || revisionObjetivo != _revision) {
        _syncPendiente = false;
        await sincronizarConBackend();
      }
    }
  }

  static void _marcarCambio() {
    _revision += 1;
    if (_productos.isNotEmpty) {
      _ultimaSyncTeniaItems = true;
    }
  }

  static Future<Map<String, dynamic>?> confirmarPedidoActual() async {
    final idUsuario = SessionService.idUsuario;
    if (!SessionService.estaAutenticado || idUsuario == null) {
      return null;
    }

    final tipoPedido = SessionService.tipoPedido;
    final mesaId = tipoPedido == 'para_llevar' ? null : SessionService.mesaId;
    if (tipoPedido == 'restaurante' && mesaId == null) {
      throw Exception('Debes seleccionar una mesa valida antes de pedir');
    }
    if (_productos.isEmpty) {
      throw Exception('El pedido debe incluir items');
    }

    final pedido = await BongustoApi.crearPedido(
      idUsuario: idUsuario,
      totalPedido: calcularTotal(),
      items: _productos.map((p) => p.toPedidoItem()).toList(),
      tipoPedido: tipoPedido,
      mesaId: mesaId,
    );
    return pedido;
  }
}
