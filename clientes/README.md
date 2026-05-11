# BonGusto Clientes

App Flutter para clientes del restaurante BonGusto. Se conecta al backend Django para:
- registro e inicio de sesión
- menú digital
- carrito y pedidos
- solicitud de música
- llamado al mesero
- visualización de mesa asignada
- historial y detalle de pedidos

## Estructura

```text
clientes/
|-- lib/
|   |-- main.dart
|   |-- api_config.dart
|   |-- local_database_service.dart
|   |-- screens/
|   |-- services/
|   `-- utils/
|-- assets/
|-- android/
|-- ios/
|-- web/
`-- pubspec.yaml
```

Archivos base:
- [main.dart](c:/Users/sebas/Downloads/bongusto_django/clientes/lib/main.dart)
- [api_config.dart](c:/Users/sebas/Downloads/bongusto_django/clientes/lib/api_config.dart)
- [local_database_service.dart](c:/Users/sebas/Downloads/bongusto_django/clientes/lib/local_database_service.dart)
- [services/bongusto_api.dart](c:/Users/sebas/Downloads/bongusto_django/clientes/lib/services/bongusto_api.dart)
- [services/session_service.dart](c:/Users/sebas/Downloads/bongusto_django/clientes/lib/services/session_service.dart)

## Flujo principal

Rutas principales:
- `'/start'`
- `'/login'`
- `'/register'`
- `'/home'`
- `'/menu'`
- `'/restaurante'`
- `'/pedidos'`
- `'/opciones-pedido'`

Flujo actual:
1. el cliente inicia sesión o se registra
2. la app guarda token y datos en almacenamiento seguro
3. el cliente entra, consulta menú, productos y categorías
4. puede escanear QR y obtener una mesa asignada
5. arma su pedido
6. puede pedir música o llamar al mesero
7. puede ver `Tu mesa actual` desde la zona del pedido
8. consulta pedidos e historial

## Pantallas importantes

- [home_screen.dart](c:/Users/sebas/Downloads/bongusto_django/clientes/lib/screens/home_screen.dart)
- [menu_screen.dart](c:/Users/sebas/Downloads/bongusto_django/clientes/lib/screens/menu_screen.dart)
- [restaurante_screen.dart](c:/Users/sebas/Downloads/bongusto_django/clientes/lib/screens/restaurante_screen.dart)
- [carrito_screen.dart](c:/Users/sebas/Downloads/bongusto_django/clientes/lib/screens/carrito_screen.dart)
- [pedidos_screen.dart](c:/Users/sebas/Downloads/bongusto_django/clientes/lib/screens/pedidos_screen.dart)
- [pedido_detalle_screen.dart](c:/Users/sebas/Downloads/bongusto_django/clientes/lib/screens/pedido_detalle_screen.dart)
- [opciones_pedido_screen.dart](c:/Users/sebas/Downloads/bongusto_django/clientes/lib/screens/opciones_pedido_screen.dart)
- [musica_screen.dart](c:/Users/sebas/Downloads/bongusto_django/clientes/lib/screens/musica_screen.dart)
- [mesero_screen.dart](c:/Users/sebas/Downloads/bongusto_django/clientes/lib/screens/mesero_screen.dart)
- [qr_screen.dart](c:/Users/sebas/Downloads/bongusto_django/clientes/lib/screens/qr_screen.dart)

## Integración con Django

Cliente HTTP principal:
- [services/bongusto_api.dart](c:/Users/sebas/Downloads/bongusto_django/clientes/lib/services/bongusto_api.dart)

Endpoints usados:
- `POST /api/clientes/register`
- `POST /api/clientes/login`
- `GET /api/session/refresh`
- `GET /api/menus`
- `GET /api/categorias`
- `GET /api/productos`
- `POST /api/pedidos`
- `GET /api/pedidos`
- `GET /api/mi-mesa`
- `POST /api/mesas/asignar`
- `GET /api/musicas`
- `POST /api/solicitudes-musica`
- `POST /api/mesero/llamados`
- `POST /api/calificaciones`

Notas importantes:
- el chat ya no forma parte de la app `clientes`
- el flujo de cliente se conecta a mesa y llamado a mesero
- los pedidos y llamados deben ir asociados a la mesa actual

## Mesa actual

La mesa del cliente se usa en estos puntos:
- asignación por QR
- vista `Tu mesa actual`
- creación de pedidos
- llamado al mesero
- solicitudes musicales

Archivos clave:
- [qr_screen.dart](c:/Users/sebas/Downloads/bongusto_django/clientes/lib/screens/qr_screen.dart)
- [opciones_pedido_screen.dart](c:/Users/sebas/Downloads/bongusto_django/clientes/lib/screens/opciones_pedido_screen.dart)
- [session_service.dart](c:/Users/sebas/Downloads/bongusto_django/clientes/lib/services/session_service.dart)

## Configuración del backend

La URL base se arma en:
- [api_config.dart](c:/Users/sebas/Downloads/bongusto_django/clientes/lib/api_config.dart)

Valores típicos:
- esquema: `http`
- host local: `127.0.0.1`
- puerto: `8080`

Overrides por `dart-define`:

```powershell
flutter run --dart-define=API_HOST=192.168.1.50 --dart-define=API_PORT=8080
```

## Ejecución local

Backend Django:

```powershell
cd C:\Users\sebas\Downloads\bongusto_django\bongusto_django
.\.venv\Scripts\Activate.ps1
python manage.py runserver 0.0.0.0:8080
```

App Flutter:

```powershell
cd C:\Users\sebas\Downloads\bongusto_django\clientes
flutter pub get
flutter run
```

Android físico:

```powershell
adb reverse tcp:8080 tcp:8080
```

## Conexión con el sistema completo

`clientes` trabaja junto con:
- [bongusto_django/README.md](c:/Users/sebas/Downloads/bongusto_django/bongusto_django/README.md)
- [mesero/README.md](c:/Users/sebas/Downloads/bongusto_django/mesero/README.md)

Flujos compartidos:
- el cliente crea pedidos y `mesero` los ve
- el cliente llama al mesero y `mesero` atiende
- el cliente queda vinculado a una mesa
- el cliente puede marcar actividad que luego se refleja en `mesero`

## Notas prácticas

- la app usa `flutter_secure_storage` para el token
- hay refresco de sesión al arrancar
- si Android no conecta al backend, casi siempre falta `adb reverse` o el host correcto
- si se cambió código de servicios o conexión, usa `full restart`, no solo hot reload
