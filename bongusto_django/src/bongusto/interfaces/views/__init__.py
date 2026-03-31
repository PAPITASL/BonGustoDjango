"""Punto de agrupacion para vistas expuestas desde la capa de interfaces.

Este archivo reune las vistas importadas desde los modulos para que la
capacidad de enrutamiento y organizacion del proyecto quede centralizada
y sea mas facil de ubicar para alguien que esta aprendiendo Django.
"""

# Importaciones agrupadas de vistas y paquetes que se exponen desde la
# capa de interfaces del proyecto.
from bongusto.modules import (
    auth,
    bitacora,
    calificaciones,
    categorias as categoria,
    chat,
    dashboard,
    eventos as reserva,
    menus as menu,
    musica,
    pedidos as pedido,
    perfil,
    permisos as permiso,
    productos as producto,
    roles as rol,
    usuarios as usuario,
)
