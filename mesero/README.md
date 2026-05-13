# BonGusto Mesero

App Flutter para el flujo operativo del mesero. Se conecta al backend Django para:
- iniciar sesión
- ver pedidos de clientes
- revisar y atender llamados
- consultar la cola musical
- administrar visualmente las mesas
- chatear con administración

## Estructura

```text
mesero/
|-- lib/
|   |-- main.dart
|   |-- api_config.dart
|   |-- screens/
|   `-- services/
|-- assets/
|-- android/
|-- ios/
|-- web/
`-- pubspec.yaml
```

Archivos base:
- [main.dart](c:/Users/sebas/Downloads/bongusto_django/mesero/lib/main.dart)
- [api_config.dart](c:/Users/sebas/Downloads/bongusto_django/mesero/lib/api_config.dart)
- [services/bongusto_api.dart](c:/Users/sebas/Downloads/bongusto_django/mesero/lib/services/bongusto_api.dart)
- [services/session_service.dart](c:/Users/sebas/Downloads/bongusto_django/mesero/lib/services/session_service.dart)

## Rutas principales

- `'/start'`
- `'/login'`
- `'/home'`
- `'/pedidos'`
- `'/notificaciones'`
- `'/menu'`
- `'/mesas'`
- `'/musica'`
- `'/interaccion'`
- `'/perfil'`
- `'/reset'`

## Flujo operativo actual

1. el mesero inicia sesión
2. la app guarda token y datos del perfil
3. entra al panel principal
4. consulta pedidos creados por clientes
5. ve llamados a mesero
6. revisa la cola de música
7. entra a `Mesas` para ver quién ocupa cada mesa
8. puede marcar la mesa como `Pagada`
9. puede `Liberar` la mesa cuando ya se desocupó
10. puede abrir el chat con administración

## Pantallas importantes

- [home_screen.dart](c:/Users/sebas/Downloads/bongusto_django/mesero/lib/screens/home_screen.dart)
- [pedidos_screen.dart](c:/Users/sebas/Downloads/bongusto_django/mesero/lib/screens/pedidos_screen.dart)
- [pedido_detalle_screen.dart](c:/Users/sebas/Downloads/bongusto_django/mesero/lib/screens/pedido_detalle_screen.dart)
- [notificaciones_admin_screen.dart](c:/Users/sebas/Downloads/bongusto_django/mesero/lib/screens/notificaciones_admin_screen.dart)
- [menu_screen.dart](c:/Users/sebas/Downloads/bongusto_django/mesero/lib/screens/menu_screen.dart)
- [musica_screen.dart](c:/Users/sebas/Downloads/bongusto_django/mesero/lib/screens/musica_screen.dart)
- [gestion_mesas_screen.dart](c:/Users/sebas/Downloads/bongusto_django/mesero/lib/screens/gestion_mesas_screen.dart)
- [mesa_detail_screen.dart](c:/Users/sebas/Downloads/bongusto_django/mesero/lib/screens/mesa_detail_screen.dart)
- [interaccion_screen.dart](c:/Users/sebas/Downloads/bongusto_django/mesero/lib/screens/interaccion_screen.dart)
- [perfil_screen.dart](c:/Users/sebas/Downloads/bongusto_django/mesero/lib/screens/perfil_screen.dart)

## Integración con Django

Cliente HTTP principal:
- [services/bongusto_api.dart](c:/Users/sebas/Downloads/bongusto_django/mesero/lib/services/bongusto_api.dart)

Endpoints usados:
- `POST /api/meseros/login`
- `GET /api/session/refresh`
- `GET /api/pedidos`
- `GET /api/pedidos/<id>`
- `GET /api/mesero/llamados`
- `POST /api/mesero/llamados/<id>/atender`
- `GET /api/menus`
- `GET /api/productos`
- `GET /api/musicas/cola`
- `GET /api/mesas`
- `POST /api/mesas/<id>/estado`
- `GET /api/chat/historial`
- `POST /api/chat/enviar`

Tiempo real:
- chat por WebSocket
- respaldo por API/historial
- pedidos, llamados, música y mesas usan refresco periódico

## Módulo de mesas

Pantallas:
- [gestion_mesas_screen.dart](c:/Users/sebas/Downloads/bongusto_django/mesero/lib/screens/gestion_mesas_screen.dart)
- [mesa_detail_screen.dart](c:/Users/sebas/Downloads/bongusto_django/mesero/lib/screens/mesa_detail_screen.dart)

Estados visuales:
- `Disponible`: gris
- `Ocupada`: rojo suave
- `Pagada`: verde

Reglas actuales:
- si la mesa se asigna a un cliente, se considera ocupada
- si el cliente tiene pedidos, la mesa sigue ocupada
- desde el detalle el mesero puede marcarla como pagada
- luego puede liberarla para devolverla a disponible

La vista de mesas busca mostrar:
- cliente actual
- conteo de pedidos
- conteo de productos
- producto resumen
- estado operativo

## Configuración del backend

La URL base se arma en:
- [api_config.dart](c:/Users/sebas/Downloads/bongusto_django/mesero/lib/api_config.dart)

Valores típicos:
- esquema: `http`
- host local: `127.0.0.1`
- puerto: `8001`

Overrides por `dart-define`:

```powershell
flutter run --dart-define=API_HOST=192.168.1.50 --dart-define=API_PORT=8001
```

## Ejecución local

Backend Django:

```powershell
cd C:\Users\sebas\Downloads\bongusto_django\bongusto_django
.\.venv\Scripts\Activate.ps1
python manage.py runserver 0.0.0.0:8001
```

App Flutter:

```powershell
cd C:\Users\sebas\Downloads\bongusto_django\mesero
flutter pub get
flutter run
```

Android físico:

```powershell
adb reverse tcp:8001 tcp:8001
```

También puedes usar el script del repo raíz:
- [run_mesero.ps1](c:/Users/sebas/Downloads/bongusto_django/run_mesero.ps1)

## Conexión con el sistema completo

`mesero` trabaja junto con:
- [bongusto_django/README.md](c:/Users/sebas/Downloads/bongusto_django/bongusto_django/README.md)
- [clientes/README.md](c:/Users/sebas/Downloads/bongusto_django/clientes/README.md)

Flujos compartidos:
- `clientes` crea pedidos y `mesero` los ve
- `clientes` llama al mesero y `mesero` atiende
- `clientes` ocupa una mesa y `mesero` lo ve en la grilla
- administración web y `mesero` se comunican por chat

## Notas prácticas

- el módulo correcto se llama `mesero`, no `meseros`
- el cierre de sesión está en `Perfil`
- si cambias servicios, rutas o conexión, usa `full restart`
- si Android no conecta, revisa `adb reverse` y el host efectivo del backend
