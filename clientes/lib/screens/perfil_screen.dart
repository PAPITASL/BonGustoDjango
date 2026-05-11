// Pantalla donde el cliente consulta y edita informacion basica de su perfil.
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';

import '../app_theme.dart';
import '../language_controller.dart';
import '../services/bongusto_api.dart';
import '../services/session_service.dart';
import 'app_settings_controls.dart';
import 'home_screen.dart';
import 'login_screen.dart';
import 'mapa_screen.dart';
import 'pedidos_screen.dart';

// Widget principal del perfil del cliente.
class PerfilScreen extends StatefulWidget {
  const PerfilScreen({super.key});

  @override
  State<PerfilScreen> createState() => _PerfilScreenState();
}

// Estado que maneja datos del usuario, foto y cierre de sesion.
class _PerfilScreenState extends State<PerfilScreen> {
  static Color get _card => AppThemeColors.surface;
  static Color get _ink => AppThemeColors.text;
  static Color get _muted => AppThemeColors.muted;
  static const _accent = Color(0xFFD90416);
  static Color get _line => AppThemeColors.line;
  bool _isDark(BuildContext context) =>
      Theme.of(context).brightness == Brightness.dark;

  File? _imagen;
  int _currentIndex = 3;

  Future<void> _seleccionarImagen() async {
    final picker = ImagePicker();
    final imagen = await picker.pickImage(source: ImageSource.gallery);

    if (imagen != null) {
      setState(() {
        _imagen = File(imagen.path);
      });
    }
  }

  Future<void> _editarPerfil() async {
    final rootContext = context;
    final usuario = SessionService.usuarioActual ?? const <String, dynamic>{};
    final nombreCtrl = TextEditingController(
      text: (SessionService.nombreCompleto.isEmpty
              ? usuario['nombre_completo']
              : SessionService.nombreCompleto)
          .toString(),
    );
    final correoCtrl = TextEditingController(text: SessionService.correo);
    final telefonoCtrl = TextEditingController(
      text: (usuario['telefono'] ?? '').toString(),
    );

    final result = await showModalBottomSheet<bool>(
      context: context,
      isScrollControlled: true,
      useSafeArea: true,
      backgroundColor: Colors.transparent,
      builder: (sheetContext) {
        bool loading = false;
        final formKey = GlobalKey<FormState>();

        return StatefulBuilder(
          builder: (context, setModalState) {
            Future<void> guardar() async {
              if (!(formKey.currentState?.validate() ?? false)) return;
              setModalState(() => loading = true);
              try {
                final respuesta = await BongustoApi.actualizarPerfil(
                  nombreCompleto: nombreCtrl.text.trim(),
                  correo: correoCtrl.text.trim(),
                  telefono: telefonoCtrl.text.trim(),
                );
                final usuarioActualizado = Map<String, dynamic>.from(
                  respuesta['usuario'] as Map,
                );
                await SessionService.actualizarSesion(usuarioActualizado);
                if (!mounted) return;
                if (Navigator.of(sheetContext).canPop()) {
                  Navigator.of(sheetContext).pop(true);
                }
              } catch (e) {
                setModalState(() => loading = false);
                if (!mounted) return;
                ScaffoldMessenger.of(rootContext).showSnackBar(
                  SnackBar(content: Text('$e')),
                );
              }
            }

            return Padding(
              padding: EdgeInsets.only(
                bottom: MediaQuery.of(context).viewInsets.bottom,
              ),
              child: Container(
                decoration: BoxDecoration(
                  color: _card,
                  borderRadius: const BorderRadius.vertical(top: Radius.circular(28)),
                  border: Border(top: BorderSide(color: _line)),
                ),
                child: SafeArea(
                  top: false,
                  child: Padding(
                    padding: const EdgeInsets.all(20),
                    child: Form(
                      key: formKey,
                      child: ListView(
                        shrinkWrap: true,
                        keyboardDismissBehavior: ScrollViewKeyboardDismissBehavior.manual,
                        children: [
                          const Text(
                            'Editar perfil',
                            style: TextStyle(fontSize: 22, fontWeight: FontWeight.w900),
                          ),
                          const SizedBox(height: 16),
                          TextFormField(
                            controller: nombreCtrl,
                            decoration: const InputDecoration(labelText: 'Nombre completo'),
                            textInputAction: TextInputAction.next,
                            validator: (value) =>
                                (value == null || value.trim().isEmpty) ? 'El nombre es obligatorio.' : null,
                          ),
                          const SizedBox(height: 12),
                          TextFormField(
                            controller: correoCtrl,
                            decoration: const InputDecoration(labelText: 'Correo'),
                            keyboardType: TextInputType.emailAddress,
                            textInputAction: TextInputAction.next,
                            validator: (value) {
                              final text = (value ?? '').trim();
                              if (text.isEmpty) return 'El correo es obligatorio.';
                              if (!RegExp(r'^[^@\s]+@[^@\s]+\.[^@\s]+$').hasMatch(text)) {
                                return 'Ingresa un correo valido.';
                              }
                              return null;
                            },
                          ),
                          const SizedBox(height: 12),
                          TextFormField(
                            controller: telefonoCtrl,
                            decoration: const InputDecoration(labelText: 'Telefono'),
                            keyboardType: TextInputType.phone,
                            textInputAction: TextInputAction.done,
                          ),
                          const SizedBox(height: 18),
                          ElevatedButton(
                            onPressed: loading ? null : guardar,
                            style: ElevatedButton.styleFrom(
                              backgroundColor: _accent,
                              foregroundColor: Colors.white,
                              padding: const EdgeInsets.symmetric(vertical: 14),
                            ),
                            child: loading
                                ? const SizedBox(
                                    height: 20,
                                    width: 20,
                                    child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                                  )
                                : const Text('Guardar cambios'),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              ),
            );
          },
        );
      },
    );

    nombreCtrl.dispose();
    correoCtrl.dispose();
    telefonoCtrl.dispose();
    if (result == true) {
      setState(() {});
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Perfil actualizado correctamente.')),
      );
    }
  }

  Future<void> _cambiarContrasena() async {
    final rootContext = context;
    final actualCtrl = TextEditingController();
    final nuevaCtrl = TextEditingController();
    final confirmarCtrl = TextEditingController();

    final result = await showModalBottomSheet<bool>(
      context: context,
      isScrollControlled: true,
      useSafeArea: true,
      backgroundColor: Colors.transparent,
      builder: (sheetContext) {
        bool loading = false;
        final formKey = GlobalKey<FormState>();

        return StatefulBuilder(
          builder: (context, setModalState) {
            Future<void> guardar() async {
              if (!(formKey.currentState?.validate() ?? false)) return;
              setModalState(() => loading = true);
              try {
                await BongustoApi.cambiarContrasenaPerfil(
                  contrasenaActual: actualCtrl.text.trim(),
                  nuevaContrasena: nuevaCtrl.text.trim(),
                  confirmarContrasena: confirmarCtrl.text.trim(),
                );
                if (!mounted) return;
                if (Navigator.of(sheetContext).canPop()) {
                  Navigator.of(sheetContext).pop(true);
                }
              } catch (e) {
                setModalState(() => loading = false);
                if (!mounted) return;
                ScaffoldMessenger.of(rootContext).showSnackBar(
                  SnackBar(content: Text('$e')),
                );
              }
            }

            return Padding(
              padding: EdgeInsets.only(
                bottom: MediaQuery.of(context).viewInsets.bottom,
              ),
              child: Container(
                decoration: BoxDecoration(
                  color: _card,
                  borderRadius: const BorderRadius.vertical(top: Radius.circular(28)),
                  border: Border(top: BorderSide(color: _line)),
                ),
                child: SafeArea(
                  top: false,
                  child: Padding(
                    padding: const EdgeInsets.all(20),
                    child: Form(
                      key: formKey,
                      child: ListView(
                        shrinkWrap: true,
                        keyboardDismissBehavior: ScrollViewKeyboardDismissBehavior.manual,
                        children: [
                          const Text(
                            'Cambiar contraseÃƒÂ±a',
                            style: TextStyle(fontSize: 22, fontWeight: FontWeight.w900),
                          ),
                          const SizedBox(height: 16),
                          TextFormField(
                            controller: actualCtrl,
                            obscureText: true,
                            decoration: const InputDecoration(labelText: 'Contraseña actual'),
                            textInputAction: TextInputAction.next,
                            validator: (value) =>
                                (value == null || value.trim().isEmpty) ? 'Ingresa tu contraseÃƒÂ±a actual.' : null,
                          ),
                          const SizedBox(height: 12),
                          TextFormField(
                            controller: nuevaCtrl,
                            obscureText: true,
                            decoration: const InputDecoration(labelText: 'Nueva contraseÃƒÂ±a'),
                            textInputAction: TextInputAction.next,
                            validator: (value) =>
                                (value == null || value.trim().isEmpty) ? 'La nueva contraseÃƒÂ±a es obligatoria.' : null,
                          ),
                          const SizedBox(height: 12),
                          TextFormField(
                            controller: confirmarCtrl,
                            obscureText: true,
                            decoration: const InputDecoration(labelText: 'Confirmar contraseÃƒÂ±a'),
                            textInputAction: TextInputAction.done,
                            validator: (value) {
                              if (value == null || value.trim().isEmpty) {
                                return 'Confirma la nueva contraseÃƒÂ±a.';
                              }
                              if (value.trim() != nuevaCtrl.text.trim()) {
                                return 'Las contraseÃƒÂ±as no coinciden.';
                              }
                              return null;
                            },
                          ),
                          const SizedBox(height: 18),
                          ElevatedButton(
                            onPressed: loading ? null : guardar,
                            style: ElevatedButton.styleFrom(
                              backgroundColor: _accent,
                              foregroundColor: Colors.white,
                              padding: const EdgeInsets.symmetric(vertical: 14),
                            ),
                            child: loading
                                ? const SizedBox(
                                    height: 20,
                                    width: 20,
                                    child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                                  )
                                : const Text('Actualizar contraseÃƒÂ±a'),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              ),
            );
          },
        );
      },
    );

    actualCtrl.dispose();
    nuevaCtrl.dispose();
    confirmarCtrl.dispose();
    if (result == true) {
      setState(() {});
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Contraseña actualizada correctamente.')),
      );
    }
  }

  Future<void> _cerrarSesion() async {
    await SessionService.cerrarSesion();
    Navigator.pushAndRemoveUntil(
      context,
      MaterialPageRoute(builder: (_) => const LoginScreen()),
      (route) => false,
    );
  }

  void _onTabTapped(int index) {
    if (index == _currentIndex) return;
    setState(() => _currentIndex = index);

    if (index == 0) {
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (_) => const HomeScreen()),
      );
    } else if (index == 1) {
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (_) => const PedidosScreen()),
      );
    } else if (index == 2) {
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (_) => const MapScreen()),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final usuario = SessionService.usuarioActual;
    final nombre = SessionService.nombreCompleto.isEmpty
        ? 'Invitado'
        : SessionService.nombreCompleto;
    final idUsuario = SessionService.idUsuario?.toString() ?? 'Sin sesion';
    final correo = SessionService.correo;

    return Scaffold(
      backgroundColor: theme.scaffoldBackgroundColor,
      appBar: AppBar(
        title: Text(
          LanguageController.tr('Perfil'),
          style: TextStyle(fontSize: 28, fontWeight: FontWeight.w900),
        ),
        backgroundColor: theme.scaffoldBackgroundColor,
        foregroundColor: theme.colorScheme.onSurface,
        actions: [
          Padding(
            padding: EdgeInsets.only(right: 12),
            child: AppSettingsControls(),
          ),
        ],
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: _onTabTapped,
        type: BottomNavigationBarType.fixed,
        backgroundColor: theme.colorScheme.surface,
        selectedItemColor: _accent,
        unselectedItemColor: theme.colorScheme.onSurface.withValues(
          alpha: 0.58,
        ),
        showUnselectedLabels: true,
        items: [
          BottomNavigationBarItem(
            icon: Icon(Icons.home_outlined),
            label: LanguageController.tr('Inicio'),
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.list_alt_outlined),
            label: LanguageController.tr('Pedidos'),
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.map_outlined),
            label: LanguageController.tr('Mapa'),
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.person_outline),
            label: LanguageController.tr('Perfil'),
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.fromLTRB(20, 8, 20, 100),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              padding: const EdgeInsets.all(22),
              decoration: BoxDecoration(
                color: _card,
                borderRadius: BorderRadius.circular(28),
                border: Border.all(color: _line),
              ),
              child: Row(
                children: [
                  Stack(
                    children: [
                      CircleAvatar(
                        radius: 42,
                        backgroundColor: const Color(0xFFFFECEE),
                        backgroundImage: _imagen != null
                            ? FileImage(_imagen!)
                            : const AssetImage('assets/logooficial.png')
                                  as ImageProvider,
                      ),
                      Positioned(
                        bottom: 0,
                        right: 0,
                        child: GestureDetector(
                          onTap: _seleccionarImagen,
                          child: Container(
                            padding: const EdgeInsets.all(6),
                            decoration: BoxDecoration(
                              color: _accent,
                              shape: BoxShape.circle,
                            ),
                            child: Icon(
                              Icons.edit_outlined,
                              color: Colors.white,
                              size: 16,
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          nombre,
                          style: TextStyle(
                            color: _ink,
                            fontSize: 24,
                            fontWeight: FontWeight.w900,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          correo.isEmpty ? 'Sin correo registrado' : correo,
                          style: TextStyle(
                            color: _muted,
                            fontSize: 14,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                        const SizedBox(height: 10),
                        Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 12,
                            vertical: 8,
                          ),
                          decoration: BoxDecoration(
                            color: _isDark(context)
                                ? const Color(0xFF232737)
                                : const Color(0xFFF4F4F7),
                            borderRadius: BorderRadius.circular(999),
                            border: Border.all(color: _line),
                          ),
                          child: Text(
                            'ID usuario: $idUsuario',
                            style: TextStyle(
                              color: _isDark(context)
                                  ? const Color(0xFFF4F5F9)
                                  : const Color(0xFF181818),
                              fontWeight: FontWeight.w700,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 18),
            Row(
              children: [
                Expanded(
                  child: _profileMetric(
                    context: context,
                    title: 'Rol',
                    value: (usuario?['tipo_usuario'] ?? 'cliente').toString(),
                    icon: Icons.badge_outlined,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _profileMetric(
                    context: context,
                    title: 'Estado',
                    value: 'Activo',
                    icon: Icons.verified_user_outlined,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 18),
            Container(
              decoration: BoxDecoration(
                color: _card,
                borderRadius: BorderRadius.circular(28),
                border: Border.all(color: _line),
              ),
              child: Column(
                children: [
                  _profileAction(
                    context: context,
                    icon: Icons.edit_outlined,
                    title: 'Editar perfil',
                    subtitle: 'Actualiza tu nombre, correo y telefono.',
                    onTap: _editarPerfil,
                  ),
                  Divider(height: 1, color: _line),
                  _profileAction(
                    context: context,
                    icon: Icons.lock_outline,
                    title: 'Cambiar contraseÃƒÂ±a',
                    subtitle: 'Actualiza tu clave actual sin cerrar sesion.',
                    onTap: _cambiarContrasena,
                  ),
                  Divider(height: 1, color: _line),
                  _profileAction(
                    context: context,
                    icon: Icons.list_alt_outlined,
                    title: 'Ver mis pedidos',
                    subtitle: 'Revisa tu historial y el estado de cada compra.',
                    onTap: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (_) => const PedidosScreen(),
                        ),
                      );
                    },
                  ),
                  Divider(height: 1, color: _line),
                  _profileAction(
                    context: context,
                    icon: Icons.photo_library_outlined,
                    title: 'Cambiar foto',
                    subtitle: 'Selecciona una imagen desde tu galeria.',
                    onTap: _seleccionarImagen,
                  ),
                  Divider(height: 1, color: _line),
                  _profileAction(
                    context: context,
                    icon: Icons.logout_rounded,
                    title: 'Cerrar sesion',
                    subtitle: 'Salir de tu cuenta y volver al acceso.',
                    onTap: () {
                      _cerrarSesion();
                    },
                    accent: true,
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _profileMetric({
    required BuildContext context,
    required String title,
    required String value,
    required IconData icon,
  }) {
    final dark = _isDark(context);
    final labelColor = dark ? const Color(0xFFC8CEDB) : const Color(0xFF62636D);
    final valueColor = dark ? const Color(0xFFF4F5F9) : const Color(0xFF111217);

    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: _card,
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: _line),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, color: _accent),
          const SizedBox(height: 12),
          Text(
            title,
            style: TextStyle(
              color: labelColor,
              fontSize: 12,
              letterSpacing: 1.2,
              fontWeight: FontWeight.w700,
            ),
          ),
          const SizedBox(height: 6),
          Text(
            value,
            style: TextStyle(
              color: valueColor,
              fontSize: 18,
              fontWeight: FontWeight.w900,
            ),
          ),
        ],
      ),
    );
  }

  Widget _profileAction({
    required BuildContext context,
    required IconData icon,
    required String title,
    required String subtitle,
    required VoidCallback onTap,
    bool accent = false,
  }) {
    final dark = _isDark(context);
    final iconBg = accent
        ? AppThemeColors.accentSoft
        : (dark ? const Color(0xFF232737) : const Color(0xFFF4F4F7));
    final iconColor = accent
        ? _accent
        : (dark ? const Color(0xFFF4F5F9) : const Color(0xFF181818));

    return ListTile(
      contentPadding: const EdgeInsets.symmetric(horizontal: 18, vertical: 8),
      leading: Container(
        width: 44,
        height: 44,
        decoration: BoxDecoration(
          color: iconBg,
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: _line),
        ),
        child: Icon(icon, color: iconColor),
      ),
      title: Text(
        title,
        style: TextStyle(
          color: accent ? _accent : _ink,
          fontWeight: FontWeight.w800,
        ),
      ),
      subtitle: Text(subtitle, style: TextStyle(color: _muted, height: 1.4)),
      trailing: Icon(Icons.chevron_right_rounded, color: _muted),
      onTap: onTap,
    );
  }
}



