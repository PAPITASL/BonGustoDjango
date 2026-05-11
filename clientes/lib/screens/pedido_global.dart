// Modelo de datos que representa un pedido consumido desde la API.
import 'producto_global.dart';

// Clase de dominio para trabajar pedidos dentro de la app cliente.
class Pedido {
  final int id;
  final List<Producto> productos;
  final double total;
  final String estado;
  final String mesaLabel;
  final String fechaPedido;

  Pedido({
    required this.id,
    required this.productos,
    required this.total,
    required this.estado,
    required this.mesaLabel,
    required this.fechaPedido,
  });

  factory Pedido.fromApi(Map<String, dynamic> json) {
    final items = (json['items'] as List<dynamic>? ?? [])
        .map(
          (item) => Producto(
            idProducto: _asInt(item['id_producto']) ?? 0,
            nombre:
                (item['nombre_producto'] ?? 'Producto #${item['id_producto']}')
                    .toString(),
            imagen: 'assets/bandeja.png',
            precio: _asDouble(item['precio']),
            descripcion: (item['descripcion_producto'] ?? '').toString(),
            cantidad: _asInt(item['cantidad']) ?? 1,
          ),
        )
        .toList();

    return Pedido(
      id: _asInt(json['id_pedido']) ?? 0,
      productos: items,
      total: _asDouble(json['total_pedido']),
      estado: (json['estado'] ?? 'Registrado').toString(),
      mesaLabel: (json['mesa_label'] ?? '').toString(),
      fechaPedido: (json['fecha_pedido'] ?? '').toString(),
    );
  }

  static int? _asInt(dynamic value) {
    if (value is int) {
      return value;
    }
    return int.tryParse('$value');
  }

  static double _asDouble(dynamic value) {
    if (value is num) {
      return value.toDouble();
    }
    return double.tryParse('$value') ?? 0;
  }
}
