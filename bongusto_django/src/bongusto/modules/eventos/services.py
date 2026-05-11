"""Servicios del modulo `eventos`. Aqui es donde se maneja toda la logica de reservas y eventos del sistema."""

# ===== Importaciones | Aqui simplemente traemos el modelo Reserva desde la capa domain. =====
# No creamos modelos aqui, solo usamos lo que ya existe para mantener todo organizado
from bongusto.domain.models import Reserva



# ===== Clase `ReservaService` | Aqui agrupamos toda la logica de reservas para no mezclarla con las vistas. =====
# La idea es que todo lo importante pase por aqui
class ReservaService:

# ===== Funcion `listar_todas` | Trae todas las reservas del sistema. =====
# Se ordenan de la mas reciente a la mas antigua
# select_related ayuda a traer el usuario de una vez (mejor rendimiento)
    def listar_todas(self):
        return Reserva.objects.select_related("id_usuario").all().order_by("-fecha_reser", "-hora_reser", "-id_reser")


# ===== Funcion `listar_filtrado` | Sirve para filtrar reservas segun lo que el usuario necesite. =====
# Puede filtrar por estado, por fecha o por ambos
    def listar_filtrado(self, estado=None, fecha=None):
        qs = self.listar_todas()

        # Si viene estado, lo filtra sin importar mayusculas o minusculas
        if estado:
            qs = qs.filter(estado_reser__iexact=estado)

        # Si viene fecha, filtra exactamente por esa fecha
        if fecha:
            qs = qs.filter(fecha_reser=fecha)

        return qs


# ===== Funcion `buscar_por_id` | Busca una reserva especifica por su ID. =====
# first() evita errores si no existe
    def buscar_por_id(self, pk):
        return Reserva.objects.filter(pk=pk).first()


# ===== Funcion `guardar` | Guarda la reserva en la base de datos. =====
# Sirve tanto para crear como para actualizar
    def guardar(self, reserva):
        reserva.save()
        return reserva


# ===== Funcion `eliminar` | Elimina una reserva directamente desde la base de datos. =====
    def eliminar(self, pk):
        Reserva.objects.filter(pk=pk).delete()


# ===== Exportaciones | Esto define que se puede usar desde este archivo en otros modulos. =====
__all__ = ["ReservaService", "Reserva"]