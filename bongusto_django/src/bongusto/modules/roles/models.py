"""Modelos o aliases del modulo `roles`. 
Este archivo expone las entidades principales relacionadas con los roles del sistema y su gestion."""


# ===== Importaciones | Dependencias que este archivo necesita para funcionar dentro del modulo. =====
from bongusto.domain.models import Permiso, Rol


# ===== Exportaciones | Define que entidades se pueden usar desde este modulo. =====
__all__ = ["Rol", "Permiso"]

