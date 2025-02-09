# factories/base_notification_factory.py
from abc import ABC, abstractmethod
from typing import Tuple, Optional

from django.apps import apps

class BaseNotificationFactory(ABC):
    def __init__(self):
        self.Notification = apps.get_model('biblioteca', 'Notification')

    @abstractmethod
    def create_notification(self) -> Tuple[str, str]:
        """
        Método abstracto que debe ser implementado por las clases hijas.
        Returns:
            Tuple[str, str]: Una tupla con (asunto, mensaje)
        """
        pass

    def save_notification(self, subject: str, message: str, recipient: str) -> Optional[object]:
        """
        Guarda la notificación en la base de datos.
        Args:
            subject (str): Asunto de la notificación
            message (str): Mensaje de la notificación
            recipient (str): Destinatario de la notificación
        Returns:
            Optional[object]: El objeto Notification creado o None si hay error
        """
        try:
            return self.Notification.objects.create(
                subject=subject,
                message=message,
                recipient=recipient
            )
        except Exception as e:
            print(f"Error al guardar la notificación: {e}")
            return None