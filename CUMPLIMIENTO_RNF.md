# Cumplimiento De Requerimientos No Funcionales

Este documento resume lo que el repositorio ya deja implementado y lo que debes operar para sostenerlo.

## RN01 Rendimiento menu < 3 segundos

- Se agrego cache para `GET /api/menus` y `GET /api/productos`.
- Si Redis esta configurado, el cache sera compartido entre procesos.

## RN02 Portabilidad Android y Web

- Las apps `clientes` y `mesero` incluyen carpeta `web/` y configuracion Flutter para Android/Web.

## RN03 Disponibilidad 99%

- Se agrego endpoint `GET /healthz` para monitoreo.
- Se agrego script `run_resilient_server.ps1` para reinicio automatico local.

## RN04 Seguridad y cifrado

- Tokens firmados para API y WebSocket.
- Sesion Flutter almacenada con `flutter_secure_storage`.
- Cookies seguras fuera de `DEBUG`.
- Configuracion lista para `https` y `wss` por variables de entorno.
- `settings.py` exige `DJANGO_SECRET_KEY` cuando `DEBUG=false`.

## RN05 Escalabilidad

- Se agrego soporte opcional a Redis para cache y channel layer.

## RN06 Usabilidad

- Se conserva la interfaz actual orientada por actor con estados de carga, error y feedback visible.

## RN07 150 pedidos simultaneos

- La arquitectura queda mejor preparada al usar Daphne + Channels + Redis.
- Para afirmarlo formalmente debes correr una prueba de carga.

## RN08 Notificaciones < 1 segundo

- Ya existe WebSocket para chat/notificaciones.
- Con Redis y despliegue estable queda apto para baja latencia.

## RN09 Backups diarios

- Se agrego `manage.py backup_data`.
- Se agrego `run_daily_backup.ps1`.
- Se agrego `setup_daily_backup_task.ps1`.

## RN10 Recuperacion < 30 segundos

- Se agrego `run_resilient_server.ps1`.
- Se agrego `GET /healthz` para deteccion automatica por monitoreo.
