"""
Servicios del módulo chat.

Aquí se maneja la lógica del chat:
- obtener mensajes
- obtener conversaciones
- guardar mensajes
"""

# Q sirve para hacer filtros más avanzados (OR, AND, etc.)
from django.db.models import Q

# Modelo del chat
from bongusto.domain.models import MensajeChat


# Clase principal del chat
class ChatService:


    # Trae los últimos mensajes del sistema
    def obtener_mensajes(self, limite=50):

        # Excluye mensajes especiales del sistema (ej: llamado a mesero)
        # y ordena por fecha (los más antiguos primero)
        return MensajeChat.objects.exclude(
            destinatario="mesero_call"
        ).order_by("fecha")[:limite]


    # Trae la conversación entre dos usuarios
    def obtener_conversacion(self, participante, con=None, limite=100):

        # Base: todos los mensajes normales
        qs = MensajeChat.objects.exclude(
            destinatario="mesero_call"
        ).order_by("fecha")

        # Si hay un usuario específico con quien hablar
        if con:

            # Busca mensajes entre ambos (ida y vuelta)
            qs = qs.filter(
                Q(remitente=participante, destinatario=con)
                | Q(remitente=con, destinatario=participante)
            )

        else:
            # Si no hay destinatario, trae todos donde participe el usuario
            qs = qs.filter(
                Q(remitente=participante)
                | Q(destinatario=participante)
            )

        return qs[:limite]


    # Guarda un mensaje en la base de datos
    def guardar_mensaje(self, remitente, destinatario, mensaje):

        # Crea el objeto
        msg = MensajeChat(
            remitente=remitente,
            destinatario=destinatario,
            mensaje=mensaje
        )

        # Lo guarda en la base de datos
        msg.save()

        return msg


# Lo que se puede usar desde este archivo
__all__ = ["ChatService", "MensajeChat"]
