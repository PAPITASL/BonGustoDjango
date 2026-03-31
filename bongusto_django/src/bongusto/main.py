"""Mapa principal del backend BonGusto organizado por modulos.

Este archivo funciona como un punto central para ubicar los modulos
principales del proyecto. No ejecuta logica del negocio; solo expone
una estructura sencilla para consulta, depuracion o integraciones.
"""

# Importaciones de los modulos principales del backend.
from bongusto.modules import auth
from bongusto.modules import bitacora
from bongusto.modules import calificaciones
from bongusto.modules import categorias
from bongusto.modules import chat
from bongusto.modules import dashboard
from bongusto.modules import eventos
from bongusto.modules import menus
from bongusto.modules import musica
from bongusto.modules import pedidos
from bongusto.modules import perfil
from bongusto.modules import permisos
from bongusto.modules import productos
from bongusto.modules import roles
from bongusto.modules import shared
from bongusto.modules import usuarios

# Diccionario principal donde cada clave representa el nombre del modulo
# y cada valor apunta al paquete correspondiente.
PROJECT_MODULES = {
    "auth": auth,
    "bitacora": bitacora,
    "calificaciones": calificaciones,
    "categorias": categorias,
    "chat": chat,
    "dashboard": dashboard,
    "eventos": eventos,
    "menus": menus,
    "musica": musica,
    "perfil": perfil,
    "pedidos": pedidos,
    "permisos": permisos,
    "productos": productos,
    "roles": roles,
    "shared": shared,
    "usuarios": usuarios,
}


def get_project_modules():
    """Retorna el mapa principal de modulos del proyecto.

    Se usa cuando otra parte del sistema necesita conocer que modulos
    estan disponibles dentro del backend.
    """
    return PROJECT_MODULES
