# observers/database_observer.py
from typing import List
from django.apps import apps
from .notification_observer import NotificationObserver
import logging

logger = logging.getLogger(__name__)

class DatabaseObserver(NotificationObserver):
    def __init__(self):
        self.Notification = apps.get_model('biblioteca', 'Notification')

    def update(self, subject: str, message: str, recipient: str) -> bool:
        """Guarda las notificaciones en la base de datos."""
        try:
            notification = self.Notification.objects.create(
                subject=subject,
                message=message,
                recipient=recipient
            )
            logger.info(f"Notificación {notification.id} guardada en la base de datos")
            return True
            
        except Exception as e:
            logger.error(f"Error guardando notificación en BD: {str(e)}")
            return False

    def get_unread_notifications(self, recipient: str) -> List[object]:
        """
        Obtiene las notificaciones no leídas de un destinatario.
        Args:
            recipient (str): Email del destinatario
        Returns:
            List[object]: Lista de objetos Notification no leídos
        """
        return self.Notification.objects.filter(
            recipient=recipient,
            read=False
        ).order_by('-created_at')