# services/notification/database_notification_service.py
from typing import Optional, List
from django.apps import apps
import logging

logger = logging.getLogger(__name__)

class DatabaseNotificationService:
    def __init__(self):
        self.Notification = apps.get_model('biblioteca', 'Notification')

    def save_notification(self, subject: str, message: str, recipient: str) -> Optional[object]:
        """
        Guarda una notificación en la base de datos.
        """
        try:
            notification = self.Notification.objects.create(
                subject=subject,
                message=message,
                recipient=recipient
            )
            logger.info(f"Notificación guardada en BD: {notification.id}")
            return notification
        except Exception as e:
            logger.error(f"Error guardando notificación: {str(e)}")
            return None

    def get_unread_notifications(self, recipient: str) -> List[object]:
        """
        Obtiene las notificaciones no leídas de un usuario.
        """
        return self.Notification.objects.filter(
            recipient=recipient,
            read=False
        ).order_by('-created_at')

    def mark_as_read(self, notification_id: int) -> bool:
        """
        Marca una notificación como leída.
        """
        try:
            notification = self.Notification.objects.get(id=notification_id)
            notification.read = True
            notification.save()
            return True
        except self.Notification.DoesNotExist:
            logger.error(f"Notificación {notification_id} no encontrada")
            return False