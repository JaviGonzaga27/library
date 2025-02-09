# observers/notification_observer.py
from abc import ABC, abstractmethod

class NotificationObserver(ABC):
    @abstractmethod
    def update(self, subject: str, message: str, recipient: str) -> bool:
        """
        Método abstracto para actualizar las notificaciones.
        """
        pass