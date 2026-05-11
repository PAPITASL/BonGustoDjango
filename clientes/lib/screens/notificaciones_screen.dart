import 'package:flutter/material.dart';

import '../app_theme.dart';
import '../services/bongusto_api.dart';
import 'app_settings_controls.dart';

class NotificacionesScreen extends StatefulWidget {
  const NotificacionesScreen({super.key});

  @override
  State<NotificacionesScreen> createState() => _NotificacionesScreenState();
}

class _NotificacionesScreenState extends State<NotificacionesScreen> {
  bool _loading = true;
  bool _markingAll = false;
  String? _error;
  int _noLeidas = 0;
  List<Map<String, dynamic>> _items = const [];
  bool _isDark(BuildContext context) =>
      Theme.of(context).brightness == Brightness.dark;

  @override
  void initState() {
    super.initState();
    _cargar();
  }

  Future<void> _cargar() async {
    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      final data = await BongustoApi.obtenerNotificaciones();
      final items = List<Map<String, dynamic>>.from(
        (data['items'] as List<dynamic>? ?? const []).map(
          (item) => Map<String, dynamic>.from(item as Map),
        ),
      );
      if (!mounted) return;
      setState(() {
        _items = items;
        _noLeidas = (data['no_leidas'] as num?)?.toInt() ?? 0;
        _loading = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _error = '$e';
        _loading = false;
      });
    }
  }

  Future<void> _marcarLeida(Map<String, dynamic> item) async {
    final id = (item['id_notificacion'] as num?)?.toInt();
    if (id == null || item['leida'] == true) return;

    try {
      final data = await BongustoApi.marcarNotificacionLeida(id);
      if (!mounted) return;
      setState(() {
        item['leida'] = true;
        item['fecha_lectura'] =
            (data['notificacion'] as Map?)?['fecha_lectura'];
        _noLeidas = (data['no_leidas'] as num?)?.toInt() ?? _noLeidas;
      });
    } catch (_) {}
  }

  Future<void> _marcarTodas() async {
    if (_markingAll || _noLeidas == 0) return;
    setState(() => _markingAll = true);
    try {
      final data = await BongustoApi.marcarTodasLasNotificacionesLeidas();
      if (!mounted) return;
      setState(() {
        for (final item in _items) {
          item['leida'] = true;
        }
        _noLeidas = (data['no_leidas'] as num?)?.toInt() ?? 0;
      });
    } catch (_) {
    } finally {
      if (mounted) {
        setState(() => _markingAll = false);
      }
    }
  }

  String _timeAgo(String? iso) {
    if (iso == null || iso.isEmpty) return 'Sin fecha';
    final fecha = DateTime.tryParse(iso)?.toLocal();
    if (fecha == null) return 'Sin fecha';
    final diff = DateTime.now().difference(fecha);
    if (diff.inMinutes < 1) return 'Ahora';
    if (diff.inMinutes < 60) return 'Hace ${diff.inMinutes} min';
    if (diff.inHours < 24) return 'Hace ${diff.inHours} h';
    if (diff.inDays == 1) return 'Ayer';
    if (diff.inDays < 7) return 'Hace ${diff.inDays} dias';
    final dia = fecha.day.toString().padLeft(2, '0');
    final mes = fecha.month.toString().padLeft(2, '0');
    return '$dia/$mes/${fecha.year}';
  }

  IconData _iconForType(String tipo) {
    switch (tipo.toLowerCase()) {
      case 'pedido':
        return Icons.receipt_long_rounded;
      case 'reserva':
        return Icons.event_available_rounded;
      case 'musica':
        return Icons.music_note_rounded;
      default:
        return Icons.notifications_none_rounded;
    }
  }

  Widget _notificationTile(Map<String, dynamic> item) {
    final dark = _isDark(context);
    final leida = item['leida'] == true;
    final tipo = (item['tipo'] ?? 'general').toString();
    final titulo = (item['titulo'] ?? '').toString();
    final mensaje = (item['mensaje'] ?? '').toString();
    final fecha = _timeAgo((item['fecha_envio'] ?? '').toString());

    final tileColor = leida
        ? (dark ? const Color(0xFF1A1D27) : AppThemeColors.surface)
        : (dark ? const Color(0xFF232737) : AppThemeColors.surfaceAlt);
    final titleColor = dark ? const Color(0xFFF4F5F9) : AppThemeColors.text;
    final metaColor = dark ? const Color(0xFFBEC5D4) : AppThemeColors.muted;
    final messageColor = dark
        ? const Color(0xFFD3D8E4)
        : AppThemeColors.muted.withValues(alpha: 0.95);

    return InkWell(
      onTap: () => _marcarLeida(item),
      borderRadius: BorderRadius.circular(16),
      child: Container(
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: tileColor,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: AppThemeColors.line),
        ),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              width: 38,
              height: 38,
              decoration: BoxDecoration(
                color: AppThemeColors.accentSoft,
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(_iconForType(tipo), color: AppThemeColors.accent),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      if (!leida)
                        Container(
                          width: 8,
                          height: 8,
                          margin: const EdgeInsets.only(right: 6),
                          decoration: const BoxDecoration(
                            color: Color(0xFFD90416),
                            shape: BoxShape.circle,
                          ),
                        ),
                      Expanded(
                        child: Text(
                          titulo.isEmpty ? 'Notificacion' : titulo,
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                          style: TextStyle(
                            color: titleColor,
                            fontWeight: FontWeight.w800,
                            fontSize: 15,
                          ),
                        ),
                      ),
                      const SizedBox(width: 8),
                      Text(
                        fecha,
                        style: TextStyle(
                          color: metaColor,
                          fontSize: 12,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 6),
                  Text(
                    mensaje.isEmpty ? 'Sin contenido.' : mensaje,
                    style: TextStyle(
                      color: messageColor,
                      fontSize: 13,
                      height: 1.35,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _errorState() {
    return ListView(
      padding: const EdgeInsets.all(20),
      children: [
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: AppThemeColors.surface,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: AppThemeColors.line),
          ),
          child: Text(
            _error ?? 'No fue posible cargar las notificaciones.',
            style: TextStyle(color: AppThemeColors.text),
          ),
        ),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppThemeColors.bg,
      appBar: AppBar(
        title: const Text('Notificaciones'),
        actions: [
          Padding(
            padding: const EdgeInsets.only(right: 4),
            child: AppSettingsControls(),
          ),
          TextButton(
            onPressed: (_noLeidas == 0 || _markingAll) ? null : _marcarTodas,
            child: Text(
              _markingAll ? 'Marcando...' : 'Marcar todo',
              style: TextStyle(
                fontWeight: FontWeight.w800,
                color: (_noLeidas == 0 || _markingAll)
                    ? AppThemeColors.muted
                    : AppThemeColors.accent,
              ),
            ),
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _cargar,
        child: _loading
            ? const Center(child: CircularProgressIndicator())
            : _error != null
            ? _errorState()
            : _items.isEmpty
            ? ListView(
                padding: const EdgeInsets.all(20),
                children: [
                  Container(
                    padding: const EdgeInsets.all(20),
                    decoration: BoxDecoration(
                      color: AppThemeColors.surface,
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(color: AppThemeColors.line),
                    ),
                    child: Text(
                      'No tienes notificaciones.',
                      textAlign: TextAlign.center,
                      style: TextStyle(
                        color: AppThemeColors.muted,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
                ],
              )
            : ListView.separated(
                padding: const EdgeInsets.fromLTRB(16, 16, 16, 24),
                itemCount: _items.length,
                separatorBuilder: (_, __) => const SizedBox(height: 10),
                itemBuilder: (context, index) => _notificationTile(_items[index]),
              ),
      ),
    );
  }
}
