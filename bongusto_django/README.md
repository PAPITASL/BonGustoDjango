# BonGusto Django

Backend Django del sistema BonGusto. Este proyecto se conecta con dos apps Flutter:
- `clientes`
- `mesero`

Este `README.md` funciona como mapa rápido para ubicar:
- módulos Django
- rutas web y API
- base de datos
- archivos HTML y CSS
- conexión con las apps Flutter

## Estructura general

```text
bongusto_django/
|-- manage.py
|-- pyproject.toml
|-- requirements.txt
`-- src/
    `-- bongusto/
        |-- application/
        |-- domain/
        |-- infrastructure/
        |-- interfaces/
        |-- modules/
        `-- main.py
```

Archivos base:
- [manage.py](c:/Users/sebas/Downloads/bongusto_django/bongusto_django/manage.py)
- [settings.py](c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/infrastructure/settings.py)
- [urls.py](c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/interfaces/urls.py)
- [models.py](c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/domain/models.py)
- [main.py](c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/main.py)

## Módulos principales

Ruta:
- [modules](c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules)

Módulos del sistema:
- `auth`: login, logout, recuperación de contraseña.
- `dashboard`: panel administrativo, métricas, PDF y gráficas.
- `usuarios`: registro, login API, gestión de cuentas y refresco de sesión.
- `roles`: CRUD de roles.
- `permisos`: consulta de permisos.
- `perfil`: edición y visualización de perfil.
- `menus`: CRUD de menús y API pública.
- `categorias`: CRUD de categorías y API pública.
- `productos`: CRUD de productos y API pública.
- `pedidos`: pedidos, detalle, llamado a mesero y atención.
- `musica`: catálogo musical y cola de solicitudes.
- `eventos`: reservas y eventos.
- `bitacora`: auditoría e historial.
- `calificaciones`: opiniones y calificaciones.
- `chat`: historial de chat y soporte tiempo real.
- `shared`: piezas compartidas de seguridad, base visual, salud, mesas simuladas y utilidades.

Archivos clave por capa:
- [dashboard/views.py](c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/dashboard/views.py)
- [usuarios/views.py](c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/usuarios/views.py)
- [pedidos/views.py](c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/pedidos/views.py)
- [musica/views.py](c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/musica/views.py)
- [chat/views.py](c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/chat/views.py)
- [shared/views.py](c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/shared/views.py)
- [shared/table_state.py](c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/shared/table_state.py)
- [shared/excel_import.py](c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/shared/excel_import.py)

## Base de datos

Configuración:
- [settings.py](c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/infrastructure/settings.py)

Motor:
- MySQL mediante `django.db.backends.mysql`

Variables usadas:
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `DB_HOST`
- `DB_PORT`

Modelo ORM principal:
- [models.py](c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/domain/models.py)

El acceso a datos sigue principalmente Django ORM:
- `all()`
- `filter()`
- `first()`
- `create()`
- `save()`
- `delete()`
- `select_related()`
- `prefetch_related()`

## URLs web

Archivo central:
- [urls.py](c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/interfaces/urls.py)

Rutas web principales:
- `/login`
- `/logout`
- `/dashboard`
- `/perfil`
- `/usuarios`
- `/roles`
- `/permisos`
- `/menus`
- `/categorias`
- `/productos`
- `/musicas`
- `/eventos`
- `/bitacora`
- `/calificaciones`
- `/chat`
- `/password/email`
- `/password/reset`
- `/healthz`
- `/menus/importar`
- `/productos/importar`
- `/musicas/importar`

## APIs principales

Autenticación:
- `POST /api/clientes/register`
- `POST /api/clientes/login`
- `POST /api/meseros/login`
- `GET /api/session/refresh`

Catálogos:
- `GET /api/menus`
- `GET /api/categorias`
- `GET /api/productos`
- `GET /api/musicas`
- `GET /api/musicas/cola`

Pedidos y servicio:
- `GET /api/pedidos`
- `POST /api/pedidos`
- `GET /api/pedidos/<id>`
- `POST /api/mesero/llamados`
- `GET /api/mesero/llamados`
- `POST /api/mesero/llamados/<id>/atender`
- `POST /api/solicitudes-musica`
- `POST /api/calificaciones`

Chat:
- `GET /api/chat/historial`
- `POST /api/chat/enviar`
- `ws /ws/chat/<participante>/?token=...`

Mesas:
- `GET /api/mesas`
- `POST /api/mesas/asignar`
- `GET /api/mi-mesa`
- `POST /api/mesas/<id>/estado`

Importación masiva:
- `POST /menus/importar`
- `POST /productos/importar`
- `POST /musicas/importar`

Notas:
- varias rutas aceptan versión con y sin slash final
- el entorno local tiene compatibilidades extra para desarrollo y pruebas manuales

## HTML y CSS

Layout base:
- [base.html](c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/shared/templates/base.html)

CSS compartido:
- [common-table.css](c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/shared/static/css/common-table.css)

Dónde están los templates:
- cada módulo tiene su carpeta `templates`
- ejemplos:
  - [usuarios/templates](c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/usuarios/templates)
  - [productos/templates](c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/productos/templates)
  - [menus/templates](c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/menus/templates)
  - [dashboard/templates](c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/dashboard/templates)

Dónde están los CSS por módulo:
- cada módulo puede tener `static/css`
- ejemplos:
  - [shared/static/css](c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/shared/static/css)
  - [bitacora/static/css](c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/bitacora/static/css)
  - [eventos/static/css](c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/eventos/static/css)

Archivos visuales clave recientes:
- [auth/templates/auth/reset_password.html](c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/auth/templates/auth/reset_password.html)
- [usuarios/templates/usuario/create.html](c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/usuarios/templates/usuario/create.html)

## Conexión con Flutter

Apps conectadas:
- [clientes](c:/Users/sebas/Downloads/bongusto_django/clientes)
- [mesero](c:/Users/sebas/Downloads/bongusto_django/mesero)

Clientes HTTP principales:
- [clientes/lib/services/bongusto_api.dart](c:/Users/sebas/Downloads/bongusto_django/clientes/lib/services/bongusto_api.dart)
- [mesero/lib/services/bongusto_api.dart](c:/Users/sebas/Downloads/bongusto_django/mesero/lib/services/bongusto_api.dart)

Sesión local:
- [clientes/lib/services/session_service.dart](c:/Users/sebas/Downloads/bongusto_django/clientes/lib/services/session_service.dart)
- [mesero/lib/services/session_service.dart](c:/Users/sebas/Downloads/bongusto_django/mesero/lib/services/session_service.dart)

Flujos conectados hoy:
- cliente inicia sesión y crea pedidos
- cliente solicita música
- cliente llama al mesero
- cliente recibe o conserva mesa asignada
- mesero ve pedidos, llamados, música y mesas
- administrador web usa dashboard, CRUD y chat

## Tiempo real y sincronización

Chat:
- tiempo real por WebSocket
- respaldo por API/historial si falla la conexión

Pedidos, música, llamados y mesas:
- refresco periódico desde Flutter
- el panel de `mesero` se actualiza cada pocos segundos

Estado de mesas:
- `disponible`: mesa libre
- `con_pedidos` u ocupada: mesa asignada o con consumo activo
- `pagada`: mesa marcada como pagada por el mesero

## Importación masiva por Excel

Helper compartido:
- [shared/excel_import.py](c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/shared/excel_import.py)

Módulos que usan importación:
- [menus/views.py](c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/menus/views.py)
- [productos/views.py](c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/productos/views.py)
- [musica/views.py](c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/musica/views.py)

Reglas actuales:
- solo acepta `.xlsx`
- valida encabezados en la primera fila
- omite filas vacías
- normaliza encabezados antes de leer columnas
- permite actualizar registros repetidos según el módulo
- usa `openpyxl`

## Autenticación y recuperación

Archivos clave:
- [auth/views.py](c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/auth/views.py)
- [usuarios/views.py](c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/usuarios/views.py)
- [shared/api_auth.py](c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/shared/api_auth.py)
- [shared/security.py](c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/shared/security.py)

Qué cubre:
- login web
- logout web
- login API para clientes
- login API para meseros
- refresh de sesión por token
- recuperación por correo
- cambio de contraseña con política de seguridad

## Variables de entorno

Referencia:
- [../.env.example](c:/Users/sebas/Downloads/bongusto_django/.env.example)

Variables importantes:
- `DJANGO_ENV`
- `DJANGO_DEBUG`
- `DJANGO_SECRET_KEY`
- `DJANGO_ALLOWED_HOSTS`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `DB_HOST`
- `DB_PORT`
- `EMAIL_HOST`
- `EMAIL_PORT`
- `EMAIL_HOST_USER`
- `EMAIL_HOST_PASSWORD`
- `DEFAULT_FROM_EMAIL`
- `REDIS_URL`

## Dependencias

Archivos:
- [pyproject.toml](c:/Users/sebas/Downloads/bongusto_django/bongusto_django/pyproject.toml)
- [requirements.txt](c:/Users/sebas/Downloads/bongusto_django/bongusto_django/requirements.txt)

Stack principal:
- Python `>=3.11`
- Django `>=5.0,<6.0`
- Channels
- Daphne
- mysqlclient
- reportlab
- pillow
- openpyxl
- redis
- channels-redis

## Arranque local

```powershell
cd C:\Users\sebas\Downloads\bongusto_django\bongusto_django
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install -e . --no-deps
python manage.py check
python manage.py runserver 0.0.0.0:8080
```

Panel web:
- `http://127.0.0.1:8080/login`

Healthcheck:
- `http://127.0.0.1:8080/healthz`

## Scripts útiles del repo raíz

- [run_clientes.ps1](c:/Users/sebas/Downloads/bongusto_django/run_clientes.ps1)
- [run_mesero.ps1](c:/Users/sebas/Downloads/bongusto_django/run_mesero.ps1)
- [run_daily_backup.ps1](c:/Users/sebas/Downloads/bongusto_django/run_daily_backup.ps1)
- [run_resilient_server.ps1](c:/Users/sebas/Downloads/bongusto_django/run_resilient_server.ps1)
- [setup_daily_backup_task.ps1](c:/Users/sebas/Downloads/bongusto_django/setup_daily_backup_task.ps1)

## Estado práctico actual

El proyecto hoy tiene:
- backend Django modular
- frontend web administrativo con HTML/CSS unificados
- app `clientes` conectada a pedidos, música, mesa y llamado a mesero
- app `mesero` conectada a pedidos, mesas, llamados, música y chat
- simulación de cinco mesas compartidas entre cliente y mesero
- importación masiva por Excel en menús, productos y música
- recuperación de contraseña por código de correo cuando SMTP está configurado