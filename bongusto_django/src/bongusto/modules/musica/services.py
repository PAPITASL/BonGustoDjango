"""Servicios del modulo musica, aqui se maneja la logica principal para canciones y solicitudes."""

# ===== Importaciones principales | Se usan los modelos desde la capa de dominio. =====
from bongusto.domain.models import Musica, Usuario


# ===== Clase principal del modulo musica | Aqui se centraliza la logica del catalogo musical. =====
class MusicaService:

    # Listar todas las canciones
    def listar_todas(self):
        return Musica.objects.all()


    # Buscar una cancion por id
    def buscar_por_id(self, pk):
        return Musica.objects.filter(pk=pk).first()


    # Buscar el usuario que hace la solicitud
    def buscar_usuario_por_id(self, pk):
        return Usuario.objects.filter(pk=pk).first()


    # Guardar o actualizar una cancion
    def guardar(self, musica):
        musica.save()
        return musica


    # Eliminar una cancion
    def eliminar(self, pk):
        Musica.objects.filter(pk=pk).delete()


# ===== Exportacion del servicio =====
__all__ = ["MusicaService", "Musica", "Usuario"]