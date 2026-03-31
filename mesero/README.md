# BonGusto Mesero

Aplicacion Flutter para el flujo operativo de meseros de BonGusto. Se conecta al backend Django para login, consulta de pedidos, atencion de llamados, revision del menu, cola musical y chat interno con clientes.

Referencia general del repo:
- [GUIA_CODIGO.md](C:/Users/sebas/Downloads/bongusto_django/GUIA_CODIGO.md)

## Stack

- Flutter 3 / Dart 3
- `http`
- `flutter_secure_storage`
- `web_socket_channel`
- `stomp_dart_client`

## Estructura

```text
mesero/
|-- lib/
|   |-- main.dart
|   |-- api_config.dart
|   |-- services/
|   `-- screens/
|-- assets/
|-- android/
|-- ios/
|-- web/
`-- pubspec.yaml
```

Archivos clave:
- [main.dart](C:/Users/sebas/Downloads/bongusto_django/mesero/lib/main.dart)
- [api_config.dart](C:/Users/sebas/Downloads/bongusto_django/mesero/lib/api_config.dart)
- [services/bongusto_api.dart](C:/Users/sebas/Downloads/bongusto_django/mesero/lib/services/bongusto_api.dart)
- [services/session_service.dart](C:/Users/sebas/Downloads/bongusto_django/mesero/lib/services/session_service.dart)
- [screens/home_screen.dart](C:/Users/sebas/Downloads/bongusto_django/mesero/lib/screens/home_screen.dart)
- [screens/pedidos_screen.dart](C:/Users/sebas/Downloads/bongusto_django/mesero/lib/screens/pedidos_screen.dart)
- [screens/notificaciones_admin_screen.dart](C:/Users/sebas/Downloads/bongusto_django/mesero/lib/screens/notificaciones_admin_screen.dart)
- [screens/interaccion_screen.dart](C:/Users/sebas/Downloads/bongusto_django/mesero/lib/screens/interaccion_screen.dart)

## Flujo actual

La app arranca en `'/start'` y expone estas rutas principales:

- `'/login'`
- `'/home'`
- `'/pedidos'`
- `'/notificaciones'`
- `'/menu'`
- `'/mesas'`
- `'/musica'`
- `'/interaccion'`
- `'/perfil'`

Flujo operativo principal:

1. Inicio de sesion de mesero.
2. Persistencia local de sesion con `flutter_secure_storage`.
3. Entrada al home con accesos rapidos al flujo operativo.
4. Revision de pedidos registrados por clientes.
5. Apertura del detalle de cada pedido.
6. Atencion de llamados a mesero pendientes.
7. Consulta del menu y de los productos por menu.
8. Revision de la cola musical enviada por clientes.
9. Chat en tiempo real con cliente o administrador.
10. Gestion visual de mesas desde una grilla local de estados.

Pantallas funcionales destacadas:
- [login_screen.dart](C:/Users/sebas/Downloads/bongusto_django/mesero/lib/screens/login_screen.dart)
- [home_screen.dart](C:/Users/sebas/Downloads/bongusto_django/mesero/lib/screens/home_screen.dart)
- [pedidos_screen.dart](C:/Users/sebas/Downloads/bongusto_django/mesero/lib/screens/pedidos_screen.dart)
- [pedido_detalle_screen.dart](C:/Users/sebas/Downloads/bongusto_django/mesero/lib/screens/pedido_detalle_screen.dart)
- [notificaciones_admin_screen.dart](C:/Users/sebas/Downloads/bongusto_django/mesero/lib/screens/notificaciones_admin_screen.dart)
- [menu_screen.dart](C:/Users/sebas/Downloads/bongusto_django/mesero/lib/screens/menu_screen.dart)
- [musica_screen.dart](C:/Users/sebas/Downloads/bongusto_django/mesero/lib/screens/musica_screen.dart)
- [interaccion_screen.dart](C:/Users/sebas/Downloads/bongusto_django/mesero/lib/screens/interaccion_screen.dart)
- [gestion_mesas_screen.dart](C:/Users/sebas/Downloads/bongusto_django/mesero/lib/screens/gestion_mesas_screen.dart)
- [perfil_screen.dart](C:/Users/sebas/Downloads/bongusto_django/mesero/lib/screens/perfil_screen.dart)

## Integracion con Django

Cliente HTTP principal:
- [services/bongusto_api.dart](C:/Users/sebas/Downloads/bongusto_django/mesero/lib/services/bongusto_api.dart)

Endpoints usados desde la app:

- `POST /api/meseros/login`
- `GET /api/pedidos`
- `GET /api/mesero/llamados`
- `POST /api/mesero/llamados/{id}/atender`
- `GET /api/chat/historial`
- `GET /api/menus`
- `GET /api/productos?menu_id=...`
- `GET /api/musicas/cola`

La sesion autenticada usa token `Bearer` guardado por [session_service.dart](C:/Users/sebas/Downloads/bongusto_django/mesero/lib/services/session_service.dart).

## Configuracion del backend

La URL base se arma en [api_config.dart](C:/Users/sebas/Downloads/bongusto_django/mesero/lib/api_config.dart).

Valores por defecto:
- esquema: `http`
- host local en web/desktop/android: `127.0.0.1`
- host remoto de respaldo: `192.168.10.12`
- puerto: `8080`

Overrides soportados con `--dart-define`:

```powershell
flutter run --dart-define=API_HOST=192.168.1.50 --dart-define=API_PORT=8080
```

Tambien puedes definir el esquema:

```powershell
flutter run --dart-define=API_SCHEME=https --dart-define=API_HOST=api.midominio.com
```

## Ejecucion local

Backend Django:

```powershell
cd C:\Users\sebas\Downloads\bongusto_django\bongusto_django
.\.venv\Scripts\Activate.ps1
python manage.py runserver 127.0.0.1:8080
```

App Flutter:

```powershell
cd C:\Users\sebas\Downloads\bongusto_django\mesero
flutter pub get
flutter run
```

En Android fisico, expone el puerto del backend con `adb reverse`:

```powershell
adb reverse tcp:8080 tcp:8080
```

Si quieres fijar un dispositivo:

```powershell
flutter devices
flutter run -d DEVICE_ID
```

## Ejecucion junto a Clientes

Terminal 1. Django:

```powershell
cd C:\Users\sebas\Downloads\bongusto_django\bongusto_django
.\.venv\Scripts\Activate.ps1
python manage.py runserver 127.0.0.1:8080
```

Terminal 2. `adb reverse`:

```powershell
adb -s DEVICE_ID reverse tcp:8080 tcp:8080
```

Terminal 3. Clientes:

```powershell
cd C:\Users\sebas\Downloads\bongusto_django\clientes
flutter run -d DEVICE_ID
```

Terminal 4. Mesero:

```powershell
cd C:\Users\sebas\Downloads\bongusto_django\mesero
flutter run -d SEGUNDO_DEVICE_ID
```

Si usas dos dispositivos, ejecuta tambien:

```powershell
adb -s SEGUNDO_DEVICE_ID reverse tcp:8080 tcp:8080
```

## Notas

- El modulo correcto del repo es `mesero`, no `meseros`.
- El chat usa `web_socket_channel` y agrega el token a la conexion.
- `stomp_dart_client` figura en dependencias, pero la mensajeria activa del codigo revisado usa WebSocket directo.
- La vista de mesas actual es local al cliente Flutter y no consume API propia para persistir estados.
- Si Android no conecta al backend, casi siempre falta `adb reverse` o Django no esta corriendo en `127.0.0.1:8080`.
