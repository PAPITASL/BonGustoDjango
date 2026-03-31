# BonGusto Django

BonGusto es un sistema compuesto por:
- un backend Django
- una app Flutter para clientes
- una app Flutter para meseros

Este `README.md` sirve como mapa general para ubicar rápido:
- módulos
- URLs web y API
- base de datos
- backend
- frontend
- templates HTML
- CSS compartido
- archivos clave del sistema

## Vista general

Estructura principal del repositorio:

```text
bongusto_django/
|-- bongusto_django/          -> backend Django
|-- clientes/                 -> app Flutter de clientes
|-- mesero/                   -> app Flutter de meseros
|-- .env.example              -> variables de entorno de referencia
|-- GUIA_CODIGO.md            -> guía complementaria del proyecto
|-- CUMPLIMIENTO_RNF.md       -> estado de requerimientos no funcionales
|-- CUMPLIMIENTO_SEGURIDAD.md -> notas de seguridad
|-- run_clientes.ps1          -> arranque Flutter clientes
|-- run_mesero.ps1            -> arranque Flutter mesero
|-- run_daily_backup.ps1      -> script de respaldo
|-- run_resilient_server.ps1  -> arranque resiliente del backend
`-- setup_daily_backup_task.ps1
```

## Backend Django

Ruta base del backend:
- [bongusto_django](/c:/Users/sebas/Downloads/bongusto_django/bongusto_django)

Estructura interna:

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

Archivos base importantes:
- [manage.py](/c:/Users/sebas/Downloads/bongusto_django/bongusto_django/manage.py): punto de entrada de Django
- [settings.py](/c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/infrastructure/settings.py): configuración principal
- [urls.py](/c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/interfaces/urls.py): rutas web y API
- [models.py](/c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/domain/models.py): modelos ORM principales
- [main.py](/c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/main.py): mapa principal de módulos
- [base.html](/c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/shared/templates/base.html): layout base del panel web
- [common-table.css](/c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/shared/static/css/common-table.css): estilos visuales compartidos

## Módulos Django

Ruta de módulos:
- [modules](/c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules)

Módulos principales del backend:

1. `auth`
   Responsable de login, logout y recuperación de contraseña.
   Archivo clave: [auth/views.py](/c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/auth/views.py)

2. `dashboard`
   Panel principal administrativo, métricas y reporte PDF.
   Archivo clave: [dashboard/views.py](/c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/dashboard/views.py)

3. `usuarios`
   Gestión de usuarios, meseros, estados y APIs de login/registro.
   Archivo clave: [usuarios/views.py](/c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/usuarios/views.py)

4. `roles`
   CRUD de roles del sistema.
   Archivo clave: [roles/views.py](/c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/roles/views.py)

5. `permisos`
   Consulta de permisos disponibles.
   Archivo clave: [permisos/views.py](/c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/permisos/views.py)

6. `perfil`
   Ver y editar perfil del usuario autenticado.
   Archivo clave: [perfil/views.py](/c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/perfil/views.py)

7. `menus`
   CRUD de menús, importación Excel, PDF y API pública.
   Archivo clave: [menus/views.py](/c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/menus/views.py)

8. `categorias`
   CRUD de categorías y API pública.
   Archivo clave: [categorias/views.py](/c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/categorias/views.py)

9. `productos`
   CRUD de productos, filtros, importación Excel, PDF y API pública.
   Archivo clave: [productos/views.py](/c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/productos/views.py)

10. `pedidos`
   APIs de pedidos, detalle, llamados al mesero y atención.
   Archivo clave: [pedidos/views.py](/c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/pedidos/views.py)

11. `musica`
   Gestión web de música y APIs para cola y solicitudes.
   Archivo clave: [musica/views.py](/c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/musica/views.py)

12. `eventos`
   Reservas y eventos del restaurante.
   Archivo clave: [eventos/views.py](/c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/eventos/views.py)

13. `bitacora`
   Historial de acciones y auditoría.
   Archivo clave: [bitacora/views.py](/c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/bitacora/views.py)

14. `calificaciones`
   Calificaciones del servicio y API para clientes.
   Archivo clave: [calificaciones/views.py](/c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/calificaciones/views.py)

15. `chat`
   Pantalla y API de historial de chat.
   Archivo clave: [chat/views.py](/c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/chat/views.py)

16. `shared`
   Elementos compartidos: base visual, middleware, auth API, seguridad, salud, backup.
   Archivos clave:
   - [shared/views.py](/c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/shared/views.py)
   - [shared/middleware.py](/c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/shared/middleware.py)
   - [shared/api_auth.py](/c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/shared/api_auth.py)
   - [shared/security.py](/c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/shared/security.py)

## Arquitectura Django

Capas principales:
- `domain`: modelos y reglas principales
- `application`: espacio reservado para servicios/casos de uso
- `infrastructure`: settings, ASGI, PDF y configuración técnica
- `interfaces`: URLs y agrupación de vistas
- `modules`: funcionalidades organizadas por contexto

Mapa de módulos:
- [main.py](/c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/main.py)

Agrupador de vistas:
- [interfaces/views/__init__.py](/c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/interfaces/views/__init__.py)

## Base de datos

Configuración principal:
- [settings.py](/c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/infrastructure/settings.py)

Motor usado:
- `django.db.backends.mysql`

Variables principales:
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `DB_HOST`
- `DB_PORT`

Valores por defecto en desarrollo:
- host: `127.0.0.1`
- puerto: `3306`
- usuario: `root`

Modelo principal ORM:
- [models.py](/c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/domain/models.py)

El proyecto sigue usando Django ORM como forma principal de acceso a datos:
- `all()`
- `filter()`
- `first()`
- `create()`
- `save()`
- `delete()`
- `select_related()`
- `prefetch_related()`

## URLs web principales

Archivo central:
- [urls.py](/c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/interfaces/urls.py)

Rutas web principales:
- `/login`
- `/logout`
- `/healthz`
- `/password/email`
- `/password/reset`
- `/dashboard`
- `/perfil`
- `/usuarios`
- `/roles`
- `/permisos`
- `/bitacora`
- `/calificaciones`
- `/menus`
- `/categorias`
- `/productos`
- `/musicas`
- `/eventos`
- `/chat`

## APIs principales

Autenticación:
- `/api/clientes/register`
- `/api/clientes/login`
- `/api/meseros/login`

Catálogos:
- `/api/menus`
- `/api/categorias`
- `/api/productos`
- `/api/musicas`
- `/api/musicas/cola`

Pedidos y servicio:
- `/api/pedidos`
- `/api/pedidos/<id>`
- `/api/mesero/llamados`
- `/api/mesero/llamados/<id>/atender`
- `/api/calificaciones`
- `/api/solicitudes-musica`
- `/api/chat/historial`

Notas:
- varias rutas API aceptan versión con y sin slash final
- varias rutas protegidas usan token Bearer

## HTML y CSS

Layout principal:
- [base.html](/c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/shared/templates/base.html)

CSS compartido principal:
- [common-table.css](/c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/shared/static/css/common-table.css)

Dónde están los templates HTML:
- cada módulo tiene su carpeta `templates`
- ejemplo:
  - [usuarios/templates](/c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/usuarios/templates)
  - [productos/templates](/c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/productos/templates)
  - [menus/templates](/c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/menus/templates)
  - [eventos/templates](/c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/eventos/templates)

Dónde están los CSS por módulo:
- cada módulo puede tener `static/css`
- ejemplo:
  - [bitacora/static/css](/c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/bitacora/static/css)
  - [eventos/static/css](/c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/eventos/static/css)
  - [pedidos/static/css](/c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/pedidos/static/css)

Regla práctica:
- si el cambio afecta casi todo el panel, normalmente va en `common-table.css`
- si el cambio afecta solo un módulo, normalmente va en el `static/css` de ese módulo

## Frontend Flutter

### App clientes

Ruta:
- [clientes](/c:/Users/sebas/Downloads/bongusto_django/clientes)

Estructura `lib`:

```text
clientes/lib/
|-- main.dart
|-- api_config.dart
|-- local_database_service.dart
|-- screens/
|-- services/
`-- utils/
```

Archivos importantes:
- [clientes/lib/main.dart](/c:/Users/sebas/Downloads/bongusto_django/clientes/lib/main.dart)
- [clientes/lib/api_config.dart](/c:/Users/sebas/Downloads/bongusto_django/clientes/lib/api_config.dart)
- [clientes/lib/services/bongusto_api.dart](/c:/Users/sebas/Downloads/bongusto_django/clientes/lib/services/bongusto_api.dart)
- [clientes/lib/services/session_service.dart](/c:/Users/sebas/Downloads/bongusto_django/clientes/lib/services/session_service.dart)

Responsabilidad:
- menú digital
- carrito
- pedidos
- música
- chat/interacción
- perfil
- historial y experiencia del cliente

### App mesero

Ruta:
- [mesero](/c:/Users/sebas/Downloads/bongusto_django/mesero)

Estructura `lib`:

```text
mesero/lib/
|-- main.dart
|-- api_config.dart
|-- screens/
`-- services/
```

Archivos importantes:
- [mesero/lib/main.dart](/c:/Users/sebas/Downloads/bongusto_django/mesero/lib/main.dart)
- [mesero/lib/api_config.dart](/c:/Users/sebas/Downloads/bongusto_django/mesero/lib/api_config.dart)
- [mesero/lib/services/bongusto_api.dart](/c:/Users/sebas/Downloads/bongusto_django/mesero/lib/services/bongusto_api.dart)
- [mesero/lib/services/session_service.dart](/c:/Users/sebas/Downloads/bongusto_django/mesero/lib/services/session_service.dart)

Responsabilidad:
- pedidos
- mesas
- detalle de pedidos
- interacción con clientes
- música
- vista operativa del mesero

## Conexión entre backend y Flutter

Punto de unión principal:
- las dos apps Flutter consumen las rutas del backend Django

Archivos clave:
- [clientes/lib/services/bongusto_api.dart](/c:/Users/sebas/Downloads/bongusto_django/clientes/lib/services/bongusto_api.dart)
- [mesero/lib/services/bongusto_api.dart](/c:/Users/sebas/Downloads/bongusto_django/mesero/lib/services/bongusto_api.dart)
- [clientes/lib/api_config.dart](/c:/Users/sebas/Downloads/bongusto_django/clientes/lib/api_config.dart)
- [mesero/lib/api_config.dart](/c:/Users/sebas/Downloads/bongusto_django/mesero/lib/api_config.dart)

## Variables de entorno

Referencia:
- [.env.example](/c:/Users/sebas/Downloads/bongusto_django/.env.example)

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

Comportamiento actual:
- por defecto el entorno local arranca como desarrollo
- en producción se exige `DJANGO_SECRET_KEY` si `DEBUG=false`

## Dependencias

Archivos:
- [pyproject.toml](/c:/Users/sebas/Downloads/bongusto_django/bongusto_django/pyproject.toml)
- [requirements.txt](/c:/Users/sebas/Downloads/bongusto_django/bongusto_django/requirements.txt)

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

Backend Django:

```powershell
cd C:\Users\sebas\Downloads\bongusto_django\bongusto_django
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install -e . --no-deps
python manage.py check
python manage.py runserver 127.0.0.1:8080
```

Panel web:
- `http://127.0.0.1:8080/login`

Healthcheck:
- `http://127.0.0.1:8080/healthz`

## Scripts útiles

En la raíz del repositorio:
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

Resumen práctico:
- backend Django organizado por módulos
- código simplificado en buena parte para nivel junior
- HTML y CSS más uniformes desde el layout compartido
- APIs principales disponibles para Flutter clientes y Flutter mesero
- base de datos conectada por Django ORM con MySQL
- frontend dividido en dos apps Flutter que consumen el backend

Si necesitas ubicar algo rápido:
- rutas: [urls.py](/c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/interfaces/urls.py)
- configuración: [settings.py](/c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/infrastructure/settings.py)
- modelos: [models.py](/c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/domain/models.py)
- layout web: [base.html](/c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/shared/templates/base.html)
- CSS global: [common-table.css](/c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/modules/shared/static/css/common-table.css)
- mapa de módulos: [main.py](/c:/Users/sebas/Downloads/bongusto_django/bongusto_django/src/bongusto/main.py)
