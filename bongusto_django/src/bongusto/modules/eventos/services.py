"""Servicios del modulo `eventos`. Aqui se concentra la logica de negocio relacionada con reservas y eventos del restaurante."""

# ===== Importaciones | Dependencias que este archivo necesita para funcionar dentro del modulo. =====
from bongusto.domain.models import Reserva



# ===== Clase `ReservaService` | Modulo `eventos` | Esta clase agrupa logica relacionada con eventos y reservas. =====
class ReservaService:

# ===== Funcion `listar_todas` | Modulo `eventos` | Implementa una parte de la logica de eventos y reservas. =====
    def listar_todas(self):
        return Reserva.objects.select_related("id_usuario").all().order_by("-fecha_reser", "-hora_reser", "-id_reser")


# ===== Funcion `listar_filtrado` | Modulo `eventos` | Implementa una parte de la logica de eventos y reservas. =====
    def listar_filtrado(self, estado=None, fecha=None):
        qs = self.listar_todas()
        if estado:
            qs = qs.filter(estado_reser__iexact=estado)
        if fecha:
            qs = qs.filter(fecha_reser=fecha)
        return qs


# ===== Funcion `buscar_por_id` | Modulo `eventos` | Implementa una parte de la logica de eventos y reservas. =====
    def buscar_por_id(self, pk):
        return Reserva.objects.filter(pk=pk).first()


# ===== Funcion `guardar` | Modulo `eventos` | Implementa una parte de la logica de eventos y reservas. =====
    def guardar(self, reserva):
        reserva.save()
        return reserva


# ===== Funcion `eliminar` | Modulo `eventos` | Implementa una parte de la logica de eventos y reservas. =====
    def eliminar(self, pk):
        Reserva.objects.filter(pk=pk).delete()


__all__ = ["ReservaService", "Reserva"]
