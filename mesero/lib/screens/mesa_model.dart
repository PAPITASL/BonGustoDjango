// ===== Modelo `mesa_model.dart` | Este archivo define la estructura de datos que describe cada mesa y sus pedidos asociados. =====
import 'package:flutter/material.dart';

// ===== Enum `TableStatus` | Enumera los estados operativos posibles de una mesa. =====
enum TableStatus {
  libre,
  ocupada,
  esperandoPago,
  pagada,
  enLimpieza,
  bloqueada,
}

// ===== Clase `Mesa` | Agrupa la informacion visual y operativa que se muestra dentro del modulo de mesas. =====
class Mesa {
  int id;
  int numeroMesa;
  String etiqueta;
  int capacidad;
  bool activa;
  TableStatus status;
  int? idUsuario;
  String? asignadoEn;
  DateTime? fecha;
  TimeOfDay? hora;
  Map<String, int> pendientes;
  List<Map<String, dynamic>> pedidos;
  Map<String, dynamic>? pago;
  Map<String, dynamic>? reserva;
  List<String> clientes;

  Mesa({
    required this.id,
    int? numeroMesa,
    String? etiqueta,
    this.capacidad = 0,
    this.activa = true,
    this.status = TableStatus.libre,
    this.idUsuario,
    this.asignadoEn,
    this.fecha,
    this.hora,
    Map<String, int>? pendientes,
    List<Map<String, dynamic>>? pedidos,
    this.pago,
    this.reserva,
    List<String>? clientes,
  }) : numeroMesa = numeroMesa ?? id,
       etiqueta = etiqueta ?? 'Mesa ${numeroMesa ?? id}',
       pendientes = pendientes ?? <String, int>{},
       pedidos = pedidos ?? <Map<String, dynamic>>[],
       clientes = clientes ?? <String>[];

  int get totalPedidos => pedidos.length;

  int get totalItems => pendientes.values.fold(0, (sum, qty) => sum + qty);

  double get totalPendiente {
    if (pedidos.isEmpty) {
      return 0;
    }
    final pedidoActual = pedidos.first;
    final total = pedidoActual['total_pedido'];
    if (total is num) {
      return total.toDouble();
    }
    return double.tryParse('$total') ?? 0;
  }

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
    numeroMesa: numeroMesa,
    etiqueta: etiqueta,
    capacidad: capacidad,
    activa: activa,
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
    pago: pago == null ? null : Map<String, dynamic>.from(pago!),
    reserva: reserva == null ? null : Map<String, dynamic>.from(reserva!),
    clientes: List<String>.from(clientes),
  );
}
