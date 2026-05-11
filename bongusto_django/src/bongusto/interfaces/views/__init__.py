"""Punto donde se agrupan todas las vistas que vienen desde los módulos.
"""
# Aquí básicamente se centralizan todos los módulos que tienen vistas.
# Esto ayuda a mantener el proyecto más organizado y saber desde un solo lugar
# qué módulos están conectados con la capa de interfaces.

from bongusto.modules import (
    auth,           # Maneja todo lo relacionado con autenticación (login, logout, recuperación, etc.)
    bitacora,       # Historial de movimientos del sistema
    calificaciones, # Opiniones y puntajes de los clientes
    categorias as categoria,  # Clasificación de productos (se renombra para usarlo más fácil)
    chat,           # Chat en tiempo real
    dashboard,      # Panel principal con métricas y estadísticas
    eventos as reserva,  # Reservas y eventos del sistema
    menus as menu,       # Gestión de menús
    musica,         # Sistema de música / rocola
    pedidos as pedido,   # Gestión de pedidos
    perfil,         # Perfil de usuario
    permisos as permiso, # Permisos del sistema
    productos as producto, # Productos del menú
    roles as rol,   # Roles de usuarios
    usuarios as usuario, # Gestión de usuarios
)