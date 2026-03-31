"""Compatibilidad: la implementacion real de servicios vive por modulo."""

from bongusto.modules.bitacora.services import BitacoraService
from bongusto.modules.calificaciones.services import CalificacionService
from bongusto.modules.categorias.services import CategoriaService
from bongusto.modules.chat.services import ChatService
from bongusto.modules.dashboard.services import DashboardService
from bongusto.modules.eventos.services import ReservaService
from bongusto.modules.menus.services import MenuService
from bongusto.modules.musica.services import MusicaService
from bongusto.modules.pedidos.services import PedidoService
from bongusto.modules.permisos.services import PermisoService
from bongusto.modules.productos.services import ProductoService
from bongusto.modules.roles.services import RolService
from bongusto.modules.usuarios.services import UsuarioService

__all__ = [
    "UsuarioService",
    "RolService",
    "PermisoService",
    "BitacoraService",
    "CalificacionService",
    "MenuService",
    "CategoriaService",
    "ProductoService",
    "MusicaService",
    "ReservaService",
    "PedidoService",
    "ChatService",
    "DashboardService",
]
