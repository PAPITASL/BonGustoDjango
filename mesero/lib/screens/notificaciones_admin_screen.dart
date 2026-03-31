// ===== Pantalla `notificaciones_admin_screen.dart` | Gestiona los llamados de clientes que deben ser atendidos por el mesero. =====
import 'dart:async';

import 'package:flutter/material.dart';

import '../services/bongusto_api.dart';

// ===== Clase `NotificacionesAdminScreen` | Define la vista principal del modulo de llamados y notificaciones. =====
class NotificacionesAdminScreen extends StatefulWidget {
  const NotificacionesAdminScreen({super.key});

  @override
  State<NotificacionesAdminScreen> createState() =>
      _NotificacionesAdminScreenState();
}

// ===== Estado `_NotificacionesAdminScreenState` | Controla la carga de llamados y las acciones para atenderlos. =====
class _NotificacionesAdminScreenState
    extends State<NotificacionesAdminScreen> {
  static const _bg = Color(0xFFF2F1F4);
  static const _card = Color(0xFFFFFFFF);
  static const _ink = Color(0xFF181818);
  static const _muted = Color(0xFF73727A);
  static const _accent = Color(0xFFD90416);
  static const _line = Color(0xFFE8E6EB);

  bool _loading = true;
  String _error = '';
  List<Map<String, dynamic>> _llamados = [];
  Timer? _refreshTimer;

  @override
  void initState() {
    super.initState();
    _cargarLlamados();
    _refreshTimer = Timer.periodic(const Duration(seconds: 4), (_) {
      _cargarLlamados(silent: true);
    });
  }

  @override
  void dispose() {
    _refreshTimer?.cancel();
    super.dispose();
  }

  Future<void> _cargarLlamados({bool silent = false}) async {
    if (!silent) {
      setState(() {
        _loading = true;
        _error = '';
      });
    }
    try {
      final llamados = await BongustoApi.obtenerLlamadosMesero(
        estado: 'pendiente',
      );
      if (!mounted) return;
      setState(() {
        _llamados = llamados;
        _loading = false;
        _error = '';
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _error = '$e';
        _loading = false;
      });
    }
  }

  Future<void> _atender(Map<String, dynamic> llamado) async {
    final id = _asInt(llamado['id']);
    if (id == null) return;
    try {
      await BongustoApi.atenderLlamadoMesero(id);
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Llamado marcado como atendido.')),
      );
      await _cargarLlamados();
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('No se pudo actualizar: $e')),
      );
    }
  }

  int? _asInt(dynamic value) {
    if (value is int) return value;
    return int.tryParse('$value');
  }

  Widget _hero() {
    return Container(
      padding: const EdgeInsets.all(22),
      decoration: BoxDecoration(
        color: _card,
        borderRadius: BorderRadius.circular(30),
        border: Border.all(color: _line),
      ),
      child: const Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'LLAMADOS',
            style: TextStyle(
              color: _accent,
              fontSize: 12,
              letterSpacing: 3,
              fontWeight: FontWeight.w800,
            ),
          ),
          SizedBox(height: 8),
          Text(
            'Alertas de clientes',
            style: TextStyle(
              color: _ink,
              fontSize: 30,
              height: 1.06,
              fontWeight: FontWeight.w900,
            ),
          ),
          SizedBox(height: 10),
        ],
      ),
    );
  }

  Widget _stateCard({required IconData icon, required String text, bool retry = false}) {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: _card,
        borderRadius: BorderRadius.circular(28),
        border: Border.all(color: _line),
      ),
      child: Column(
        children: [
          Icon(icon, size: 48, color: _accent),
          const SizedBox(height: 12),
          Text(text, textAlign: TextAlign.center),
          if (retry) ...[
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: _cargarLlamados,
              child: const Text('Reintentar'),
            ),
          ],
        ],
      ),
    );
  }

  Widget _callCard(Map<String, dynamic> llamado) {
    final cliente = (llamado['cliente_nombre'] ?? 'Cliente').toString();
    final mesa = (llamado['mesa_label'] ?? 'Sin mesa').toString();
    final mensaje = (llamado['mensaje'] ?? 'Cliente solicita mesero').toString();
    final fecha = (llamado['fecha'] ?? '').toString();
    return Container(
      margin: const EdgeInsets.only(bottom: 14),
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: _card,
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: _line),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                width: 46,
                height: 46,
                decoration: BoxDecoration(
                  color: const Color(0xFFFFF4EA),
                  borderRadius: BorderRadius.circular(16),
                ),
                child: const Icon(
                  Icons.notifications_active_outlined,
                  color: _accent,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Text(
                  cliente,
                  style: const TextStyle(
                    color: _ink,
                    fontWeight: FontWeight.w900,
                    fontSize: 18,
                  ),
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                decoration: BoxDecoration(
                  color: const Color(0xFFFFECEE),
                  borderRadius: BorderRadius.circular(999),
                ),
                child: const Text(
                  'Pendiente',
                  style: TextStyle(
                    color: _accent,
                    fontWeight: FontWeight.w700,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 14),
          Text(
            mesa,
            style: const TextStyle(
              color: _accent,
              fontWeight: FontWeight.w800,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            mensaje,
            style: const TextStyle(
              color: _ink,
              fontSize: 15,
              height: 1.45,
            ),
          ),
          const SizedBox(height: 10),
          Text(
            fecha,
            style: const TextStyle(color: _muted),
          ),
          const SizedBox(height: 14),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: () => _atender(llamado),
              child: const Text('Marcar atendido'),
            ),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: _bg,
      appBar: AppBar(
        backgroundColor: _bg,
        foregroundColor: _ink,
        title: const Text(
          'Llamados',
          style: TextStyle(fontWeight: FontWeight.w800),
        ),
      ),
      body: RefreshIndicator(
        color: _accent,
        onRefresh: _cargarLlamados,
        child: ListView(
          padding: const EdgeInsets.fromLTRB(20, 8, 20, 28),
          children: [
            _hero(),
            const SizedBox(height: 18),
            if (_loading)
              const Padding(
                padding: EdgeInsets.all(32),
                child: Center(child: CircularProgressIndicator()),
              )
            else if (_error.isNotEmpty)
              _stateCard(
                icon: Icons.error_outline,
                text: 'No se pudieron cargar los llamados.\n$_error',
                retry: true,
              )
            else if (_llamados.isEmpty)
              _stateCard(
                icon: Icons.check_circle_outline,
                text: 'No hay llamados pendientes de clientes.',
              )
            else
              ..._llamados.map(_callCard),
          ],
        ),
      ),
    );
  }
}
