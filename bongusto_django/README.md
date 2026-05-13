# BonGusto Django

Backend Django del sistema BonGusto. Este proyecto se conecta con dos apps Flutter:
- `clientes`
- `mesero`

Este `README.md` funciona como mapa rÃ¡pido para ubicar:
- mÃ³dulos Django
- rutas web y API
- base de datos
- archivos HTML y CSS
- conexiÃ³n con las apps Flutter

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

## MÃ³dulos principales

Ruta:
- [modules](c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules)

MÃ³dulos del sistema:
- `auth`: login, logout, recuperaciÃ³n de contraseÃ±a.
- `dashboard`: panel administrativo, mÃ©tricas, PDF y grÃ¡ficas.
- `usuarios`: registro, login API, gestiÃ³n de cuentas y refresco de sesiÃ³n.
- `roles`: CRUD de roles.
- `permisos`: consulta de permisos.
- `perfil`: ediciÃ³n y visualizaciÃ³n de perfil.
- `menus`: CRUD de menÃºs y API pÃºblica.
- `categorias`: CRUD de categorÃ­as y API pÃºblica.
- `productos`: CRUD de productos y API pÃºblica.
- `pedidos`: pedidos, detalle, llamado a mesero y atenciÃ³n.
- `musica`: catÃ¡logo musical y cola de solicitudes.
- `eventos`: reservas y eventos.
- `bitacora`: auditorÃ­a e historial.
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

ConfiguraciÃ³n:
- [settings.py](c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/infrastructure/settings.py)

Motor:
- PostgreSQL mediante `django.db.backends.postgresql`

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

AutenticaciÃ³n:
- `POST /api/clientes/register`
- `POST /api/clientes/login`
- `POST /api/meseros/login`
- `GET /api/session/refresh`

CatÃ¡logos:
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

ImportaciÃ³n masiva:
- `POST /menus/importar`
- `POST /productos/importar`
- `POST /musicas/importar`

Notas:
- varias rutas aceptan versiÃ³n con y sin slash final
- el entorno local tiene compatibilidades extra para desarrollo y pruebas manuales

## HTML y CSS

Layout base:
- [base.html](c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/shared/templates/base.html)

CSS compartido:
- [common-table.css](c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/shared/static/css/common-table.css)

DÃ³nde estÃ¡n los templates:
- cada mÃ³dulo tiene su carpeta `templates`
- ejemplos:
  - [usuarios/templates](c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/usuarios/templates)
  - [productos/templates](c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/productos/templates)
  - [menus/templates](c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/menus/templates)
  - [dashboard/templates](c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/dashboard/templates)

DÃ³nde estÃ¡n los CSS por mÃ³dulo:
- cada mÃ³dulo puede tener `static/css`
- ejemplos:
  - [shared/static/css](c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/shared/static/css)
  - [bitacora/static/css](c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/bitacora/static/css)
  - [eventos/static/css](c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/eventos/static/css)

Archivos visuales clave recientes:
- [auth/templates/auth/reset_password.html](c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/auth/templates/auth/reset_password.html)
- [usuarios/templates/usuario/create.html](c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/usuarios/templates/usuario/create.html)

## ConexiÃ³n con Flutter

Apps conectadas:
- [clientes](c:/Users/sebas/Downloads/bongusto_django/clientes)
- [mesero](c:/Users/sebas/Downloads/bongusto_django/mesero)

Clientes HTTP principales:
- [clientes/lib/services/bongusto_api.dart](c:/Users/sebas/Downloads/bongusto_django/clientes/lib/services/bongusto_api.dart)
- [mesero/lib/services/bongusto_api.dart](c:/Users/sebas/Downloads/bongusto_django/mesero/lib/services/bongusto_api.dart)

SesiÃ³n local:
- [clientes/lib/services/session_service.dart](c:/Users/sebas/Downloads/bongusto_django/clientes/lib/services/session_service.dart)
- [mesero/lib/services/session_service.dart](c:/Users/sebas/Downloads/bongusto_django/mesero/lib/services/session_service.dart)

Flujos conectados hoy:
- cliente inicia sesiÃ³n y crea pedidos
- cliente solicita mÃºsica
- cliente llama al mesero
- cliente recibe o conserva mesa asignada
- mesero ve pedidos, llamados, mÃºsica y mesas
- administrador web usa dashboard, CRUD y chat

## Tiempo real y sincronizaciÃ³n

Chat:
- tiempo real por WebSocket
- respaldo por API/historial si falla la conexiÃ³n

Pedidos, mÃºsica, llamados y mesas:
- refresco periÃ³dico desde Flutter
- el panel de `mesero` se actualiza cada pocos segundos

Estado de mesas:
- `disponible`: mesa libre
- `con_pedidos` u ocupada: mesa asignada o con consumo activo
- `pagada`: mesa marcada como pagada por el mesero

## ImportaciÃ³n masiva por Excel

Helper compartido:
- [shared/excel_import.py](c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/shared/excel_import.py)

MÃ³dulos que usan importaciÃ³n:
- [menus/views.py](c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/menus/views.py)
- [productos/views.py](c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/productos/views.py)
- [musica/views.py](c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/musica/views.py)

Reglas actuales:
- solo acepta `.xlsx`
- valida encabezados en la primera fila
- omite filas vacÃ­as
- normaliza encabezados antes de leer columnas
- permite actualizar registros repetidos segÃºn el mÃ³dulo
- usa `openpyxl`

## AutenticaciÃ³n y recuperaciÃ³n

Archivos clave:
- [auth/views.py](c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/auth/views.py)
- [usuarios/views.py](c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/usuarios/views.py)
- [shared/api_auth.py](c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/shared/api_auth.py)
- [shared/security.py](c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/shared/security.py)

QuÃ© cubre:
- login web
- logout web
- login API para clientes
- login API para meseros
- refresh de sesiÃ³n por token
- recuperaciÃ³n por correo
- cambio de contraseÃ±a con polÃ­tica de seguridad

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
- psycopg
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
python manage.py runserver 0.0.0.0:8001
```

Panel web:
- `http://127.0.0.1:8001/login`

Healthcheck:
- `http://127.0.0.1:8001/healthz`

## Scripts Ãºtiles

En la raÃ­z del repositorio:
- [run_clientes.ps1](/c:/Users/sebas/Downloads/bongusto_django/run_clientes.ps1)
- [run_mesero.ps1](/c:/Users/sebas/Downloads/bongusto_django/run_mesero.ps1)
- [run_daily_backup.ps1](/c:/Users/sebas/Downloads/bongusto_django/run_daily_backup.ps1)
- [run_resilient_server.ps1](/c:/Users/sebas/Downloads/bongusto_django/run_resilient_server.ps1)
- [setup_daily_backup_task.ps1](/c:/Users/sebas/Downloads/bongusto_django/setup_daily_backup_task.ps1)

## Documentos complementarios

- [GUIA_CODIGO.md](/c:/Users/sebas/Downloads/bongusto_django/GUIA_CODIGO.md)
- [CUMPLIMIENTO_RNF.md](/c:/Users/sebas/Downloads/bongusto_django/CUMPLIMIENTO_RNF.md)
- [CUMPLIMIENTO_SEGURIDAD.md](/c:/Users/sebas/Downloads/bongusto_django/CUMPLIMIENTO_SEGURIDAD.md)

## Estado actual del proyecto

Resumen prÃ¡ctico:
- backend Django organizado por mÃ³dulos
- cÃ³digo simplificado en buena parte para nivel junior
- HTML y CSS mÃ¡s uniformes desde el layout compartido
- APIs principales disponibles para Flutter clientes y Flutter mesero
- base de datos conectada por Django ORM con PostgreSQL
- frontend dividido en dos apps Flutter que consumen el backend

Si necesitas ubicar algo rÃ¡pido:
- rutas: [urls.py](/c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/interfaces/urls.py)
- configuraciÃ³n: [settings.py](/c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/infrastructure/settings.py)
- modelos: [models.py](/c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/domain/models.py)
- layout web: [base.html](/c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/shared/templates/base.html)
- CSS global: [common-table.css](/c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/shared/static/css/common-table.css)
- mapa de mÃ³dulos: [main.py](/c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/main.py)

