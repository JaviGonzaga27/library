from abc import ABC, abstractmethod
from typing import List, Optional
from django.core.mail import send_mail
from django.conf import settings
import logging
from .models import Notification

# Configurar logging
logger = logging.getLogger(__name__)

class NotificationObserver(ABC):
    @abstractmethod
    def update(self, subject: str, message: str, recipient: str) -> bool:
        """
        Método abstracto para actualizar las notificaciones.
        
        Args:
            subject (str): Asunto de la notificación
            message (str): Contenido de la notificación
            recipient (str): Destinatario de la notificación
            
        Returns:
            bool: True si la notificación fue exitosa, False en caso contrario
        """
        pass

class EmailNotifier(NotificationObserver):
    def update(self, subject: str, message: str, recipient: str) -> bool:
        """
        Envía notificaciones por correo electrónico.
        
        Args:
            subject (str): Asunto del correo
            message (str): Contenido del correo
            recipient (str): Dirección de correo del destinatario
            
        Returns:
            bool: True si el correo fue enviado exitosamente, False en caso contrario
        """
        try:
            if not recipient:
                raise ValueError("No se proporcionó un destinatario válido")

            send_mail(
                subject=subject,
                message=message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[recipient],
                fail_silently=False,
            )
            logger.info(f"Email enviado exitosamente a {recipient}")
            return True
            
        except Exception as e:
            logger.error(f"Error enviando email a {recipient}: {str(e)}")
            return False

class NotificationSubject:
    def __init__(self):
        self._observers: List[NotificationObserver] = []

    def attach(self, observer: NotificationObserver) -> None:
        """
        Añade un nuevo observador a la lista de observadores.
        
        Args:
            observer (NotificationObserver): El observador a añadir
        """
        if observer not in self._observers:
            self._observers.append(observer)
            logger.debug(f"Observador {observer.__class__.__name__} añadido")

    def detach(self, observer: NotificationObserver) -> None:
        """
        Elimina un observador de la lista de observadores.
        
        Args:
            observer (NotificationObserver): El observador a eliminar
        """
        try:
            self._observers.remove(observer)
            logger.debug(f"Observador {observer.__class__.__name__} eliminado")
        except ValueError:
            logger.warning(f"Observador {observer.__class__.__name__} no encontrado")

    def notify(self, subject: str, message: str, recipient: str) -> List[bool]:
        """
        Notifica a todos los observadores registrados.
        
        Args:
            subject (str): Asunto de la notificación
            message (str): Contenido de la notificación
            recipient (str): Destinatario de la notificación
            
        Returns:
            List[bool]: Lista de resultados de cada notificación
        """
        results = []
        for observer in self._observers:
            success = observer.update(subject, message, recipient)
            results.append(success)
            if not success:
                logger.warning(
                    f"Fallo en la notificación usando {observer.__class__.__name__}"
                )
        return results

class DatabaseNotifier(NotificationObserver):
    def update(self, subject: str, message: str, recipient: str) -> bool:
        """
        Guarda las notificaciones en la base de datos.
        
        Args:
            subject (str): Asunto de la notificación
            message (str): Contenido de la notificación
            recipient (str): Destinatario de la notificación
            
        Returns:
            bool: True si la notificación fue guardada exitosamente, False en caso contrario
        """
        try:
            notification = Notification.objects.create(
                subject=subject,
                message=message,
                recipient=recipient
            )
            logger.info(f"Notificación {notification.id} guardada en la base de datos")
            return True
            
        except Exception as e:
            logger.error(f"Error guardando notificación en BD: {str(e)}")
            return False

    def get_unread_notifications(self, recipient: str) -> List[Notification]:
        """
        Obtiene las notificaciones no leídas de un destinatario.
        
        Args:
            recipient (str): Email del destinatario
            
        Returns:
            List[Notification]: Lista de notificaciones no leídas
        """
        return Notification.objects.filter(
            recipient=recipient,
            read=False
        ).order_by('-created_at')