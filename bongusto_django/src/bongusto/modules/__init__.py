"""Paquete principal de modulos Django de BonGusto.

Aqui se agrupan los modulos funcionales del backend, cada uno organizado
como una app pequena y separada por responsabilidad.

Modulos principales:
- auth: login, logout y recuperacion de contrasena
- dashboard: panel principal y reportes generales
- usuarios: gestion web y autenticacion API de usuarios
- roles y permisos: administracion de acceso
- perfil: datos del usuario autenticado
- menus, categorias y productos: catalogo del restaurante
- pedidos: pedidos, detalle y llamados al mesero
- musica: catalogo musical y solicitudes
- eventos: reservas y eventos
- calificaciones: opiniones de clientes
- bitacora: historial de acciones del sistema
- chat: historial y soporte de conversacion
- shared: utilidades comunes, seguridad, middleware y helpers
"""

__all__ = [
    "auth",
    "bitacora",
    "calificaciones",
    "categorias",
    "chat",
    "dashboard",
    "eventos",
    "menus",
    "musica",
    "perfil",
    "pedidos",
    "permisos",
    "productos",
    "roles",
    "shared",
    "usuarios",
]
