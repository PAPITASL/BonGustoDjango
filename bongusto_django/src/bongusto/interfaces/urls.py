# Aquí importamos "path"
# Es lo que nos permite crear las rutas (URLs) del sistema.
from django.urls import path

# Aquí importamos las vistas de cada módulo.
# Cada módulo tiene su lógica y aquí solo las conectamos.
from bongusto.modules.auth import views as auth_views
from bongusto.modules.bitacora import views as bitacora_views
from bongusto.modules.calificaciones import views as calificaciones_views
from bongusto.modules.categorias import views as categorias_views
from bongusto.modules.chat import views as chat_views
from bongusto.modules.dashboard import views as dashboard_views
from bongusto.modules.eventos import views as eventos_views
from bongusto.modules.menus import views as menus_views
from bongusto.modules.mesas import views as mesas_views
from bongusto.modules.musica import views as musica_views
from bongusto.modules.notificaciones import views as notificaciones_views
from bongusto.modules.pedidos import views as pedidos_views
from bongusto.modules.perfil import views as perfil_views
from bongusto.modules.permisos import views as permisos_views
from bongusto.modules.productos import views as productos_views
from bongusto.modules.roles import views as roles_views
from bongusto.modules.shared import views as shared_views
from bongusto.modules.usuarios import views as usuarios_views

# Este archivo es básicamente el mapa completo del sistema.
# Aquí se define qué URL lleva a qué vista.
urlpatterns = [

    # Pagina principal publica del entorno web administrativo.
    path("", shared_views.home, name="home"),

    # =========================
    # AUTENTICACIÓN
    # =========================

    path("login", auth_views.login_view, name="login"),
    path("logout", auth_views.logout_view, name="logout"),

    # =========================
    # SALUD DEL SISTEMA / APIs GENERALES
    # =========================

    # Ruta para saber si el sistema está funcionando (healthcheck)
    path("healthz", shared_views.healthcheck, name="healthcheck"),
    path("api/language", shared_views.api_language, name="api_language"),
    path("api/language/", shared_views.api_language),
    path("api/translate", shared_views.api_translate, name="api_translate"),
    path("api/translate/", shared_views.api_translate),

    # APIs relacionadas con mesas
    path("api/mesas", mesas_views.api_listar, name="api_mesas"),
    path("api/mesas/", mesas_views.api_listar),
    path("api/mesas/estado", mesas_views.api_estado, name="api_mesas_estado"),
    path("api/mesas/estado/", mesas_views.api_estado),
    path("api/mesas/<int:pk>", mesas_views.api_detalle, name="api_mesa_detalle"),
    path("api/mesas/<int:pk>/", mesas_views.api_detalle),

    path("api/mesas/asignar", mesas_views.api_asignar_mesa, name="api_mesas_asignar"),
    path("api/mesas/asignar/", mesas_views.api_asignar_mesa),
    path("api/mesas/seleccionar", mesas_views.api_asignar_mesa, name="api_mesas_seleccionar"),
    path("api/mesas/seleccionar/", mesas_views.api_asignar_mesa),

    path("api/mesas/<int:mesa_id>/estado", mesas_views.api_actualizar_mesa, name="api_mesa_actualizar_estado"),
    path("api/mesas/<int:mesa_id>/estado/", mesas_views.api_actualizar_mesa),
    path("api/mesas/<int:pk>/solicitar-pago", mesas_views.api_solicitar_pago_mesa, name="api_mesa_solicitar_pago"),
    path("api/mesas/<int:pk>/solicitar-pago/", mesas_views.api_solicitar_pago_mesa),
    path("api/mesas/<int:pk>/confirmar-pago", mesas_views.api_confirmar_pago_mesa, name="api_mesa_confirmar_pago"),
    path("api/mesas/<int:pk>/confirmar-pago/", mesas_views.api_confirmar_pago_mesa),
    path("api/mesas/<int:pk>/liberar", mesas_views.api_liberar_mesa, name="api_mesa_liberar"),
    path("api/mesas/<int:pk>/liberar/", mesas_views.api_liberar_mesa),
    path("api/mesas/limpiar-cache", mesas_views.api_limpiar_cache_mesas, name="api_mesas_limpiar_cache"),
    path("api/mesas/limpiar-cache/", mesas_views.api_limpiar_cache_mesas),
    path("api/mesas/<int:pk>/bloquear", mesas_views.api_bloquear_mesa, name="api_mesa_bloquear"),
    path("api/mesas/<int:pk>/bloquear/", mesas_views.api_bloquear_mesa),
    path("api/mesas/<int:pk>/activar", mesas_views.api_activar_mesa, name="api_mesa_activar"),
    path("api/mesas/<int:pk>/activar/", mesas_views.api_activar_mesa),
    path("api/mesas/<int:pk>/desactivar", mesas_views.api_desactivar_mesa, name="api_mesa_desactivar"),
    path("api/mesas/<int:pk>/desactivar/", mesas_views.api_desactivar_mesa),
    path("api/mesas/<int:pk>/reactivar", mesas_views.api_reactivar_mesa, name="api_mesa_reactivar"),
    path("api/mesas/<int:pk>/reactivar/", mesas_views.api_reactivar_mesa),
    path("api/mesas/<int:pk>/historial", mesas_views.api_historial_mesa, name="api_mesa_historial"),
    path("api/mesas/<int:pk>/historial/", mesas_views.api_historial_mesa),

    path("api/mi-mesa", mesas_views.api_mi_mesa, name="api_mi_mesa"),
    path("api/mi-mesa/", mesas_views.api_mi_mesa),

    # =========================
    # RECUPERACIÓN DE CONTRASEÑA
    # =========================

    path("password/email", auth_views.password_email, name="password_email"),
    path("password/reset", auth_views.password_reset, name="password_reset"),
    path("restablecer-password", auth_views.restablecer_password_link, name="restablecer_password_link"),
    path("restablecer-password/", auth_views.restablecer_password_link),
    path("api/password/request-code", auth_views.api_password_request_code, name="api_password_request_code"),
    path("api/password/request-code/", auth_views.api_password_request_code),
    path("api/password/reset", auth_views.api_password_reset, name="api_password_reset"),
    path("api/password/reset/", auth_views.api_password_reset),
    path("api/auth/forgot-password", auth_views.api_forgot_password, name="api_auth_forgot_password"),
    path("api/auth/forgot-password/", auth_views.api_forgot_password),
    path("api/auth/reset-password", auth_views.api_reset_password, name="api_auth_reset_password"),
    path("api/auth/reset-password/", auth_views.api_reset_password),

    # =========================
    # DASHBOARD
    # =========================

    path("dashboard", dashboard_views.index, name="dashboard"),
    path("dashboard/reporte", dashboard_views.reporte, name="dashboard_reporte"),
    path("mesas", mesas_views.index, name="mesas"),
    path("mesas/store", mesas_views.store, name="mesa_store"),
    path("mesas/<int:pk>/update", mesas_views.update, name="mesa_update"),
    path("mesas/<int:pk>/toggle", mesas_views.toggle, name="mesa_toggle"),
    path("mesas/<int:pk>/delete", mesas_views.delete, name="mesa_delete"),

    # =========================
    # PERFIL
    # =========================

    path("perfil", perfil_views.ver, name="perfil"),
    path("perfil/editar", perfil_views.editar, name="perfil_editar"),
    path("perfil/actualizar", perfil_views.actualizar, name="perfil_actualizar"),

    # =========================
    # USUARIOS
    # =========================

    # CRUD completo de usuarios
    path("usuarios", usuarios_views.index, name="usuarios"),
    path("usuarios/create", usuarios_views.create, name="usuario_create"),
    path("usuarios/<int:pk>", usuarios_views.ver, name="usuario_ver"),
    path("usuarios/store", usuarios_views.store, name="usuario_store"),
    path("usuarios/<int:pk>/edit", usuarios_views.edit, name="usuario_edit"),
    path("usuarios/<int:pk>/update", usuarios_views.update, name="usuario_update"),
    path("usuarios/<int:pk>/delete", usuarios_views.delete, name="usuario_delete"),

    # Activar o desactivar usuario
    path("usuarios/<int:pk>/toggle", usuarios_views.toggle_estado, name="usuario_toggle"),

    # Reporte en PDF
    path("usuarios/reporte", usuarios_views.reporte, name="usuario_reporte"),

    # =========================
    # ROLES
    # =========================

    path("roles", roles_views.index, name="roles"),
    path("roles/create", roles_views.create, name="rol_create"),
    path("roles/<int:pk>", roles_views.ver, name="rol_ver"),
    path("roles/store", roles_views.store, name="rol_store"),
    path("roles/<int:pk>/edit", roles_views.edit, name="rol_edit"),
    path("roles/<int:pk>/update", roles_views.update, name="rol_update"),
    path("roles/<int:pk>/delete", roles_views.delete, name="rol_delete"),

    # =========================
    # PERMISOS
    # =========================

    path("permisos", permisos_views.index, name="permisos"),

    # =========================
    # BITÁCORA
    # =========================

    # Historial de acciones del sistema
    path("bitacora", bitacora_views.index, name="bitacora"),
    path("bitacora/create", bitacora_views.create, name="bitacora_create"),
    path("bitacora/<int:pk>", bitacora_views.ver, name="bitacora_ver"),
    path("bitacora/store", bitacora_views.store, name="bitacora_store"),
    path("bitacora/<int:pk>/edit", bitacora_views.edit, name="bitacora_edit"),
    path("bitacora/<int:pk>/update", bitacora_views.update, name="bitacora_update"),
    path("bitacora/<int:pk>/delete", bitacora_views.delete, name="bitacora_delete"),
    path("bitacora/reporte", bitacora_views.reporte, name="bitacora_reporte"),

    # =========================
    # CALIFICACIONES
    # =========================

    path("calificaciones", calificaciones_views.index, name="calificaciones"),
    path("calificaciones/<int:pk>", calificaciones_views.ver, name="calificacion_ver"),
    path("calificaciones/reporte", calificaciones_views.reporte, name="calificacion_reporte"),

    # =========================
    # MENÚS
    # =========================

    path("menus", menus_views.index, name="menus"),
    path("menus/create", menus_views.create, name="menu_create"),
    path("menus/<int:pk>", menus_views.ver, name="menu_ver"),
    path("menus/store", menus_views.store, name="menu_store"),
    path("menus/<int:pk>/edit", menus_views.edit, name="menu_edit"),
    path("menus/<int:pk>/update", menus_views.update, name="menu_update"),
    path("menus/<int:pk>/delete", menus_views.delete, name="menu_delete"),

    # Importar y generar PDF
    path("menus/importar", menus_views.importar_excel, name="menu_importar_excel"),
    path("menus/pdf", menus_views.pdf, name="menu_pdf"),

    # =========================
    # CATEGORÍAS
    # =========================

    path("categorias", categorias_views.index, name="categorias"),
    path("categorias/create", categorias_views.create, name="categoria_create"),
    path("categorias/<int:pk>", categorias_views.ver, name="categoria_ver"),
    path("categorias/store", categorias_views.store, name="categoria_store"),
    path("categorias/<int:pk>/edit", categorias_views.edit, name="categoria_edit"),
    path("categorias/<int:pk>/update", categorias_views.update, name="categoria_update"),
    path("categorias/<int:pk>/delete", categorias_views.delete, name="categoria_delete"),

    # =========================
    # PRODUCTOS
    # =========================

    path("productos", productos_views.index, name="productos"),
    path("productos/create", productos_views.create, name="producto_create"),
    path("productos/<int:pk>", productos_views.ver, name="producto_ver"),
    path("productos/store", productos_views.store, name="producto_store"),
    path("productos/<int:pk>/edit", productos_views.edit, name="producto_edit"),
    path("productos/<int:pk>/update", productos_views.update, name="producto_update"),
    path("productos/<int:pk>/delete", productos_views.delete, name="producto_delete"),

    # Extras
    path("productos/importar", productos_views.importar_excel, name="producto_importar_excel"),
    path("productos/reporte", productos_views.reporte, name="producto_reporte"),

    # =========================
    # MÚSICA (ROCOLA)
    # =========================

    path("musicas", musica_views.index, name="musicas"),
    path("musicas/nueva", musica_views.nueva, name="musica_nueva"),
    path("musicas/<int:pk>", musica_views.ver, name="musica_ver"),
    path("musicas/store", musica_views.store, name="musica_store"),
    path("musicas/<int:pk>/eliminar", musica_views.eliminar, name="musica_eliminar"),

    # Importación y reportes
    path("musicas/importar", musica_views.importar_excel, name="musica_importar_excel"),
    path("musicas/reporte", musica_views.reporte, name="musica_reporte"),

    # =========================
    # NOTIFICACIONES
    # =========================

    path("notificaciones", notificaciones_views.index, name="notificaciones"),
    path("notificaciones/create", notificaciones_views.create, name="notificacion_create"),
    path("notificaciones/store", notificaciones_views.store, name="notificacion_store"),

    # APIs de música
    path("api/musicas", musica_views.api_listar, name="api_musicas"),
    path("api/musicas/", musica_views.api_listar),
    path("api/musica/validar-duplicada", musica_views.api_validar_duplicada, name="api_musica_validar_duplicada"),
    path("api/musica/validar-duplicada/", musica_views.api_validar_duplicada),

    path("api/musicas/cola", musica_views.api_cola, name="api_musicas_cola"),
    path("api/musicas/cola/", musica_views.api_cola),
    path("api/musica/cola", musica_views.api_cola, name="api_musica_cola"),
    path("api/musica/cola/", musica_views.api_cola),
    path("api/musica/historial", musica_views.api_historial, name="api_musica_historial"),
    path("api/musica/historial/", musica_views.api_historial),
    path("api/musica/snapshot", musica_views.api_snapshot, name="api_musica_snapshot"),
    path("api/musica/snapshot/", musica_views.api_snapshot),

    path("api/solicitudes-musica", musica_views.api_solicitar, name="api_solicitudes_musica"),
    path("api/solicitudes-musica/", musica_views.api_solicitar),
    path("api/musica/solicitar", musica_views.api_solicitar, name="api_musica_solicitar"),
    path("api/musica/solicitar/", musica_views.api_solicitar),
    path("api/musica/<int:pk>/eliminar", musica_views.api_eliminar_solicitud, name="api_musica_eliminar"),
    path("api/musica/<int:pk>/eliminar/", musica_views.api_eliminar_solicitud),
    path("api/musica/<int:pk>/subir", musica_views.api_subir, name="api_musica_subir"),
    path("api/musica/<int:pk>/subir/", musica_views.api_subir),
    path("api/musica/<int:pk>/bajar", musica_views.api_bajar, name="api_musica_bajar"),
    path("api/musica/<int:pk>/bajar/", musica_views.api_bajar),
    path("api/musica/<int:pk>/saltar", musica_views.api_saltar, name="api_musica_saltar"),
    path("api/musica/<int:pk>/saltar/", musica_views.api_saltar),
    path("api/musica/<int:pk>/reproducida", musica_views.api_marcar_reproducida, name="api_musica_reproducida"),
    path("api/musica/<int:pk>/reproducida/", musica_views.api_marcar_reproducida),

    # =========================
    # EVENTOS / RESERVAS
    # =========================

    path("eventos", eventos_views.index, name="eventos"),
    path("eventos/nuevo", eventos_views.nuevo, name="evento_nuevo"),
    path("eventos/<int:pk>", eventos_views.ver, name="evento_ver"),
    path("eventos/store", eventos_views.store, name="evento_store"),
    path("eventos/editar/<int:pk>", eventos_views.editar, name="evento_editar"),
    path("eventos/<int:pk>/update", eventos_views.update, name="evento_update"),
    path("eventos/<int:pk>/eliminar", eventos_views.eliminar, name="evento_eliminar"),
    path("eventos/pdf", eventos_views.pdf, name="evento_pdf"),

    # =========================
    # APIs (LOGIN, PEDIDOS, ETC)
    # =========================

    path("api/clientes/login", usuarios_views.api_login_cliente, name="api_clientes_login"),
    path("api/clientes/login/", usuarios_views.api_login_cliente),

    path("api/meseros/login", usuarios_views.api_login_mesero, name="api_meseros_login"),
    path("api/meseros/login/", usuarios_views.api_login_mesero),

    path("api/clientes/register", usuarios_views.api_registro_cliente, name="api_clientes_register"),
    path("api/clientes/register/", usuarios_views.api_registro_cliente),

    path("api/session/refresh", usuarios_views.api_refresh_session, name="api_session_refresh"),
    path("api/session/refresh/", usuarios_views.api_refresh_session),
    path("api/perfil/actualizar", perfil_views.api_actualizar_perfil, name="api_perfil_actualizar"),
    path("api/perfil/actualizar/", perfil_views.api_actualizar_perfil),
    path("api/perfil/cambiar-contrasena", perfil_views.api_cambiar_contrasena, name="api_perfil_cambiar_contrasena"),
    path("api/perfil/cambiar-contrasena/", perfil_views.api_cambiar_contrasena),

    path("api/calificaciones", calificaciones_views.api_crear, name="api_calificaciones"),
    path("api/calificaciones/", calificaciones_views.api_crear),
    path("api/calificaciones/pendiente", calificaciones_views.api_pendiente, name="api_calificaciones_pendiente"),
    path("api/calificaciones/pendiente/", calificaciones_views.api_pendiente),

    path("api/menus", menus_views.api_listar, name="api_menus"),
    path("api/menus/", menus_views.api_listar),

    path("api/categorias", categorias_views.api_listar, name="api_categorias"),
    path("api/categorias/", categorias_views.api_listar),

    path("api/productos", productos_views.api_listar, name="api_productos"),
    path("api/productos/", productos_views.api_listar),

    path("api/pedidos", pedidos_views.listar_o_crear, name="api_pedidos"),
    path("api/pedidos/", pedidos_views.listar_o_crear),

    path("api/pedidos/<int:pk>", pedidos_views.detalle, name="api_pedido_detalle"),
    path("api/pedidos/<int:pk>/", pedidos_views.detalle),
    path("api/pedidos/<int:pk>/estado", pedidos_views.actualizar_estado_pedido, name="api_pedido_estado"),
    path("api/pedidos/<int:pk>/estado/", pedidos_views.actualizar_estado_pedido),

    path("api/pagos/solicitudes", pedidos_views.solicitudes_pago, name="api_pagos_solicitudes"),
    path("api/pagos/solicitudes/", pedidos_views.solicitudes_pago),
    path("api/pagos/solicitudes/<int:pk>/estado", pedidos_views.actualizar_solicitud_pago, name="api_pago_solicitud_estado"),
    path("api/pagos/solicitudes/<int:pk>/estado/", pedidos_views.actualizar_solicitud_pago),

    path("api/operacion/snapshot", mesas_views.api_snapshot, name="api_operacion_snapshot"),
    path("api/operacion/snapshot/", mesas_views.api_snapshot),

    path("api/notificaciones", notificaciones_views.api_listar, name="api_notificaciones"),
    path("api/notificaciones/", notificaciones_views.api_listar),

    path("api/notificaciones/<int:pk>/leer", notificaciones_views.api_marcar_leida, name="api_notificacion_leer"),
    path("api/notificaciones/<int:pk>/leer/", notificaciones_views.api_marcar_leida),
    path("api/notificaciones/leer-todas", notificaciones_views.api_marcar_todas_leidas, name="api_notificaciones_leer_todas"),
    path("api/notificaciones/leer-todas/", notificaciones_views.api_marcar_todas_leidas),

    # Llamados a meseros (clave en BonGusto)
    path("api/mesero/llamados", pedidos_views.llamados_mesero, name="api_llamados_mesero"),
    path("api/mesero/llamados/", pedidos_views.llamados_mesero),

    path("api/mesero/llamados/<int:pk>/atender", pedidos_views.atender_llamado, name="api_atender_llamado_mesero"),
    path("api/mesero/llamados/<int:pk>/atender/", pedidos_views.atender_llamado),

    # =========================
    # CHAT
    # =========================

    path("api/chat/historial", chat_views.api_historial, name="api_chat_historial"),
    path("api/chat/historial/", chat_views.api_historial),

    path("api/chat/enviar", chat_views.api_enviar, name="api_chat_enviar"),
    path("api/chat/enviar/", chat_views.api_enviar),

    # Vista principal del chat
    path("chat", chat_views.index, name="chat"),
]
