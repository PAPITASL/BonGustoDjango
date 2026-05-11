// Modelo de producto compartido entre menu, carrito y pedidos.
class Producto {
  final int idProducto;
  final String nombre;
  final String imagen;
  final double precio;
  final String descripcion;
  final int? idCategoria;
  final String nombreCategoria;
  final String estado;
  int cantidad;

  Producto({
    required this.idProducto,
    required this.nombre,
    required this.imagen,
    required this.precio,
    this.descripcion = '',
    this.idCategoria,
    this.nombreCategoria = '',
    this.estado = '',
    this.cantidad = 1,
  });

  factory Producto.fromApi(Map<String, dynamic> json) {
    return Producto(
      idProducto: _asInt(json['id_producto']) ?? 0,
      nombre: (json['nombre_producto'] ?? '').toString(),
      imagen: _resolverImagen(
        nombre: (json['nombre_producto'] ?? '').toString(),
        categoria: (json['nombre_cate'] ?? '').toString(),
      ),
      precio: _asDouble(json['precio_producto']),
      descripcion: (json['descripcion_producto'] ?? '').toString(),
      idCategoria: _asInt(json['id_cate']),
      nombreCategoria: (json['nombre_cate'] ?? '').toString(),
      estado: (json['estado'] ?? '').toString(),
    );
  }

  bool get disponible {
    final normalized = estado.trim().toLowerCase();
    if (normalized.isEmpty) {
      return true;
    }
    return normalized == 'activo' ||
        normalized == 'activa' ||
        normalized == 'disponible' ||
        normalized == 'en stock';
  }

  Producto copia({int? cantidad}) {
    return Producto(
      idProducto: idProducto,
      nombre: nombre,
      imagen: imagen,
      precio: precio,
      descripcion: descripcion,
      idCategoria: idCategoria,
      nombreCategoria: nombreCategoria,
      estado: estado,
      cantidad: cantidad ?? this.cantidad,
    );
  }

  Map<String, dynamic> toPedidoItem() {
    return {'id_producto': idProducto, 'cantidad': cantidad, 'precio': precio};
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

  static String _resolverImagen({
    required String nombre,
    required String categoria,
  }) {
    final clave = '$nombre $categoria'.toLowerCase();
    if (clave.contains('bebida') ||
        clave.contains('coctel') ||
        clave.contains('cocktail')) {
      return 'assets/bebidas.png';
    }
    if (clave.contains('postre')) {
      return 'assets/postres.png';
    }
    if (clave.contains('pescado') || clave.contains('marisco')) {
      return 'assets/pescado.png';
    }
    if (clave.contains('pollo')) {
      return 'assets/pollo.png';
    }
    if (clave.contains('hamburguesa') || clave.contains('burger')) {
      return 'assets/hamburguesa.png';
    }
    if (clave.contains('carne') || clave.contains('parrilla')) {
      return 'assets/carne.png';
    }
    return 'assets/bandeja.png';
  }
}
