# Guia Del Codigo

Esta guia resume donde esta cada parte importante del proyecto BonGusto para ubicar rapido backend, app `clientes` y app `mesero`.

## Mapa General

```text
bongusto_django/
|-- bongusto_django/     -> backend Django
|-- clientes/            -> app Flutter para clientes
`-- mesero/              -> app Flutter para meseros
```

## Backend Django

Ruta base:
- [bongusto_django](C:/Users/sebas/Downloads/bongusto_django/bongusto_django)

Archivos de entrada:
- [manage.py](C:/Users/sebas/Downloads/bongusto_django/bongusto_django/manage.py)
  Punto de entrada de comandos Django.
- [settings.py](C:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/infrastructure/settings.py)
  Configuracion principal: base de datos, sesiones, email, apps y middleware.
- [urls.py](C:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/interfaces/urls.py)
  Registro central de rutas web y API.
- [asgi.py](C:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/infrastructure/asgi.py)
  Entrada ASGI para HTTP y WebSocket.

Modelos principales:
- [models.py](C:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/domain/models.py)
  Aqui viven `Usuario`, `Menu`, `Producto`, `PedidoEncabezado`, `PedidoDetalle`, `Musica` y demas entidades.

Modulos importantes:
- [auth/views.py](C:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/auth/views.py)
  Login web, logout y recuperacion de contrasena.
- [usuarios/views.py](C:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/usuarios/views.py)
  CRUD de usuarios del panel y login/register API para `clientes` y `mesero`.
- [usuarios/services.py](C:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/usuarios/services.py)
  Busqueda, autenticacion y persistencia de usuarios.
- [pedidos/views.py](C:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/pedidos/views.py)
  API de pedidos y llamados al mesero.
- [pedidos/services.py](C:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/pedidos/services.py)
  Logica de creacion y consulta de pedidos.
- [menus/views.py](C:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/menus/views.py)
  CRUD y API de menus.
- [productos/views.py](C:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/productos/views.py)
  CRUD y API de productos por menu y categoria.
- [musica/views.py](C:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/musica/views.py)
  Catalogo musical y cola de solicitudes.
- [chat/views.py](C:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/chat/views.py)
  Historial y endpoints del chat.
- [shared/middleware.py](C:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/shared/middleware.py)
  Protege rutas privadas del panel web.

Plantillas de autenticacion:
- [login.html](C:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/auth/templates/auth/login.html)
- [email.html](C:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/auth/templates/auth/email.html)
- [reset_password.html](C:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/auth/templates/auth/reset_password.html)
- [password_reset_email.html](C:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/auth/templates/auth/password_reset_email.html)

## App Flutter Clientes

Ruta base:
- [clientes](C:/Users/sebas/Downloads/bongusto_django/clientes)

Entrada principal:
- [main.dart](C:/Users/sebas/Downloads/bongusto_django/clientes/lib/main.dart)
  Tema, rutas y arranque de la app.

Configuracion y servicios:
- [api_config.dart](C:/Users/sebas/Downloads/bongusto_django/clientes/lib/api_config.dart)
  Host y puerto del backend.
- [bongusto_api.dart](C:/Users/sebas/Downloads/bongusto_django/clientes/lib/services/bongusto_api.dart)
  Cliente HTTP para login, registro, menus, pedidos, musica, chat y mesero.
- [session_service.dart](C:/Users/sebas/Downloads/bongusto_django/clientes/lib/services/session_service.dart)
  Guarda sesion local del cliente.

Pantallas clave:
- [login_screen.dart](C:/Users/sebas/Downloads/bongusto_django/clientes/lib/screens/login_screen.dart)
  Inicio de sesion del cliente.
- [register_screen.dart](C:/Users/sebas/Downloads/bongusto_django/clientes/lib/screens/register_screen.dart)
  Registro de cliente.
- [home_screen.dart](C:/Users/sebas/Downloads/bongusto_django/clientes/lib/screens/home_screen.dart)
  Inicio general del cliente.
- [menu_screen.dart](C:/Users/sebas/Downloads/bongusto_django/clientes/lib/screens/menu_screen.dart)
  Lista de menus del restaurante.
- [platos_screen.dart](C:/Users/sebas/Downloads/bongusto_django/clientes/lib/screens/platos_screen.dart)
  Productos del menu elegido.
- [carrito_screen.dart](C:/Users/sebas/Downloads/bongusto_django/clientes/lib/screens/carrito_screen.dart)
  Carrito previo al pedido.
- [metodos_screen.dart](C:/Users/sebas/Downloads/bongusto_django/clientes/lib/screens/metodos_screen.dart)
  Confirmacion y creacion del pedido.
- [pedidos_screen.dart](C:/Users/sebas/Downloads/bongusto_django/clientes/lib/screens/pedidos_screen.dart)
  Lista de pedidos del cliente.
- [pedido_detalle_screen.dart](C:/Users/sebas/Downloads/bongusto_django/clientes/lib/screens/pedido_detalle_screen.dart)
  Detalle de cada pedido del cliente.
- [musica_screen.dart](C:/Users/sebas/Downloads/bongusto_django/clientes/lib/screens/musica_screen.dart)
  Solicitud de musica.
- [mesero_screen.dart](C:/Users/sebas/Downloads/bongusto_django/clientes/lib/screens/mesero_screen.dart)
  Solicitud de ayuda al mesero.
- [chat_screen.dart](C:/Users/sebas/Downloads/bongusto_django/clientes/lib/screens/chat_screen.dart)
  Chat con mesero o administrador.
- [conocenos_screen.dart](C:/Users/sebas/Downloads/bongusto_django/clientes/lib/screens/conocenos_screen.dart)
  Informacion institucional de Santa Juana.

Modelos locales utiles:
- [producto_global.dart](C:/Users/sebas/Downloads/bongusto_django/clientes/lib/screens/producto_global.dart)
- [pedido_global.dart](C:/Users/sebas/Downloads/bongusto_django/clientes/lib/screens/pedido_global.dart)
- [carrito_global.dart](C:/Users/sebas/Downloads/bongusto_django/clientes/lib/screens/carrito_global.dart)

## App Flutter Mesero

Ruta base:
- [mesero](C:/Users/sebas/Downloads/bongusto_django/mesero)

Entrada principal:
- [main.dart](C:/Users/sebas/Downloads/bongusto_django/mesero/lib/main.dart)
  Tema, rutas y arranque de la app de meseros.

Configuracion y servicios:
- [api_config.dart](C:/Users/sebas/Downloads/bongusto_django/mesero/lib/api_config.dart)
  Host y puerto del backend.
- [bongusto_api.dart](C:/Users/sebas/Downloads/bongusto_django/mesero/lib/services/bongusto_api.dart)
  Cliente HTTP para login de meseros, pedidos, menu, musica y chat.
- [session_service.dart](C:/Users/sebas/Downloads/bongusto_django/mesero/lib/services/session_service.dart)
  Estado local del mesero autenticado.

Pantallas clave:
- [login_screen.dart](C:/Users/sebas/Downloads/bongusto_django/mesero/lib/screens/login_screen.dart)
  Inicio de sesion del mesero.
- [home_screen.dart](C:/Users/sebas/Downloads/bongusto_django/mesero/lib/screens/home_screen.dart)
  Panel principal operativo.
- [pedidos_screen.dart](C:/Users/sebas/Downloads/bongusto_django/mesero/lib/screens/pedidos_screen.dart)
  Lista de pedidos creados por clientes.
- [pedido_detalle_screen.dart](C:/Users/sebas/Downloads/bongusto_django/mesero/lib/screens/pedido_detalle_screen.dart)
  Detalle puntual de un pedido.
- [menu_screen.dart](C:/Users/sebas/Downloads/bongusto_django/mesero/lib/screens/menu_screen.dart)
  Lista de menus disponibles.
- [menu_detalle_screen.dart](C:/Users/sebas/Downloads/bongusto_django/mesero/lib/screens/menu_detalle_screen.dart)
  Platos del menu seleccionado.
- [musica_screen.dart](C:/Users/sebas/Downloads/bongusto_django/mesero/lib/screens/musica_screen.dart)
  Cola musical.
- [notificaciones_admin_screen.dart](C:/Users/sebas/Downloads/bongusto_django/mesero/lib/screens/notificaciones_admin_screen.dart)
  Avisos e interaccion con administracion.
- [gestion_mesas_screen.dart](C:/Users/sebas/Downloads/bongusto_django/mesero/lib/screens/gestion_mesas_screen.dart)
  Vista de mesas y su estado.
- [interaccion_screen.dart](C:/Users/sebas/Downloads/bongusto_django/mesero/lib/screens/interaccion_screen.dart)
  Interacciones de servicio.

## Rutas API Mas Usadas

Autenticacion:
- `/api/clientes/register`
- `/api/clientes/login`
- `/api/meseros/login`

Contenido:
- `/api/menus`
- `/api/categorias`
- `/api/productos`
- `/api/musicas`
- `/api/musicas/cola`

Pedidos y servicio:
- `/api/pedidos`
- `/api/mesero/llamados`
- `/api/chat/historial`

## Flujo Rapido De Datos

1. `clientes` o `mesero` llaman metodos en `bongusto_api.dart`.
2. Esos metodos pegan a rutas declaradas en [urls.py](C:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/interfaces/urls.py).
3. Django resuelve la vista del modulo correspondiente.
4. La vista usa servicios como `UsuarioService` o `PedidoService`.
5. Los servicios operan sobre modelos en [models.py](C:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/domain/models.py).
6. Django responde JSON para Flutter o HTML para el panel web.

