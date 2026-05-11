"""
Servicios del módulo chat.
Aquí es donde se maneja la lógica del chat:
- traer mensajes
- obtener conversaciones
- guardar mensajes
"""
# Q permite hacer filtros más completos (combinar condiciones)
from django.db.models import Q

# Modelo del chat
from bongusto.domain.models import MensajeChat


# Clase principal del chat
class ChatService:

    # Trae los últimos mensajes del sistema
    def obtener_mensajes(self, limite=50):

        # Excluye mensajes especiales (como llamados a mesero)
        # y los ordena por fecha (del más antiguo al más reciente)
        return MensajeChat.objects.exclude(
            destinatario="mesero_call"
        ).order_by("fecha")[:limite]


    # Trae la conversación entre dos usuarios
    def obtener_conversacion(self, participante, con=None, limite=100):

        # Base: todos los mensajes normales ordenados por fecha
        qs = MensajeChat.objects.exclude(
            destinatario="mesero_call"
        ).order_by("fecha")

        # Si se especifica con quién hablar
        if con:

            # Busca mensajes entre ambos (ida y vuelta)
            qs = qs.filter(
                Q(remitente=participante, destinatario=con)
                | Q(remitente=con, destinatario=participante)
            )

        else:
            # Si no hay destinatario específico, trae todo donde participe el usuario
            qs = qs.filter(
                Q(remitente=participante)
                | Q(destinatario=participante)
            )

        return qs[:limite]


    # Guarda un mensaje en la base de datos
    def guardar_mensaje(self, remitente, destinatario, mensaje):

        # Crea el objeto mensaje
        msg = MensajeChat(
            remitente=remitente,
            destinatario=destinatario,
            mensaje=mensaje
        )

        # Guarda el mensaje en la base de datos
        msg.save()

        return msg


# Define lo que se puede importar desde este archivo
__all__ = ["ChatService", "MensajeChat"]
