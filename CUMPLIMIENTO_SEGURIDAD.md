# Cumplimiento De Seguridad Y Calidad

Este documento resume el estado del proyecto despues del endurecimiento tecnico aplicado en esta sesion.

## Mejoras implementadas

- Las contrasenas de usuarios ya no se guardan ni validan en texto plano.
- Se agrego hash seguro con utilidades compartidas en:
  - `bongusto_django/src/bongusto/modules/shared/security.py`
- El login ahora migra automaticamente contrasenas legacy en texto plano al nuevo formato hash cuando un usuario inicia sesion correctamente.
- Los cambios de contrasena desde:
  - login web de recuperacion
  - perfil web
  - creacion de usuarios mesero
  - registro de clientes por API
  ya guardan la clave hasheada.
- Se introdujo autenticacion por token firmado para las apps Flutter en:
  - `bongusto_django/src/bongusto/modules/shared/api_auth.py`
- Los endpoints sensibles de API ahora validan autenticacion y autorizacion:
  - pedidos
  - llamados al mesero
  - calificaciones
  - solicitudes musicales
  - cola musical
  - historial de chat
- El chat WebSocket ahora valida token de app movil y mantiene compatibilidad con la sesion web del panel.
- Se endurecio configuracion base de Django:
  - cookies `HttpOnly`
  - `SameSite=Lax`
  - cookies seguras fuera de `DEBUG`
  - `X_FRAME_OPTIONS = DENY`
  - `SECURE_CONTENT_TYPE_NOSNIFF`
  - `SECURE_REFERRER_POLICY`
- Se retiraron secretos sensibles del codigo de `settings.py`.
- El script `runserver_email.ps1` ya no deja la app password escrita en claro; ahora la pide en ejecucion si no existe en el entorno.

## Brechas que siguen existiendo

Estas brechas ya no son solo de codigo local. Requieren despliegue, infraestructura o proceso:

- TLS real en produccion:
  - Las apps siguen usando `http://` para desarrollo local.
  - Para un cumplimiento serio en produccion se necesita `https://` y `wss://`.
- Secretos de entorno:
  - `DJANGO_SECRET_KEY`, credenciales de base de datos y credenciales SMTP deben cargarse desde variables de entorno reales o un gestor de secretos.
- Base de datos:
  - Falta endurecer usuario/clave de MySQL y privilegios minimos.
- Persistencia segura del token en Flutter:
  - El token queda en memoria de sesion.
  - Para un nivel mas fuerte se recomienda almacenamiento seguro del dispositivo.
- Pruebas automatizadas:
  - Aun falta una suite de pruebas de seguridad, autenticacion y autorizacion.
- Ciclo de vida:
  - Falta CI/CD, control formal de cambios, revisiones, trazabilidad, respaldo y monitoreo.
- Certificacion:
  - Este trabajo mejora el cumplimiento tecnico, pero no equivale a una certificacion formal ISO.

## Estado real

Con los cambios aplicados, el proyecto queda mucho mejor alineado con buenas practicas de:

- seguridad de autenticacion
- control de acceso
- confidencialidad basica
- integridad de sesion
- mantenibilidad tecnica

No obstante, todavia no se puede afirmar una certificacion completa de ISO/IEC 25010 o de seguridad solo con este repositorio. Para eso faltan controles de despliegue, proceso y evidencia.
