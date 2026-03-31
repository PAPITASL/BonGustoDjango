// ===== Modelo `mesa_model.dart` | Este archivo define la estructura de datos que describe cada mesa y sus pedidos asociados. =====
import 'package:flutter/material.dart';

// ===== Enum `TableStatus` | Enumera los estados operativos posibles de una mesa. =====
enum TableStatus {
  disponible,
  noPagado,
  pagado,
}

// ===== Clase `Mesa` | Agrupa la informacion visual y operativa que se muestra dentro del modulo de mesas. =====
class Mesa {
  int id;
  TableStatus status;
  int? idUsuario;
  String? asignadoEn;
  DateTime? fecha;
  TimeOfDay? hora;
  Map<String, int> pendientes;
  List<Map<String, dynamic>> pedidos;
  List<String> clientes;

  Mesa({
    required this.id,
    this.status = TableStatus.disponible,
    this.idUsuario,
    this.asignadoEn,
    this.fecha,
    this.hora,
    Map<String, int>? pendientes,
    List<Map<String, dynamic>>? pedidos,
    List<String>? clientes,
  }) : pendientes = pendientes ?? <String, int>{},
       pedidos = pedidos ?? <Map<String, dynamic>>[],
       clientes = clientes ?? <String>[];

  int get totalPedidos => pedidos.length;

  int get totalItems => pendientes.values.fold(0, (sum, qty) => sum + qty);

  String get clientesLabel {
    if (clientes.isEmpty) {
      return 'Sin clientes';
    }
    if (clientes.length == 1) {
      return clientes.first;
    }
    return '${clientes.first} +${clientes.length - 1}';
  }

  Mesa clone() => Mesa(
    id: id,
    status: status,
    idUsuario: idUsuario,
    asignadoEn: asignadoEn,
    fecha: fecha != null
        ? DateTime.fromMillisecondsSinceEpoch(fecha!.millisecondsSinceEpoch)
        : null,
    hora: hora != null ? TimeOfDay(hour: hora!.hour, minute: hora!.minute) : null,
    pendientes: Map<String, int>.from(pendientes),
    pedidos: pedidos
        .map((pedido) => Map<String, dynamic>.from(pedido))
        .toList(growable: false),
    clientes: List<String>.from(clientes),
  );
}
