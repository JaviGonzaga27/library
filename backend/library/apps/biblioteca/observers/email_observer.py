# observers/email_observer.py
from django.core.mail import send_mail
from django.conf import settings
import logging
from .notification_observer import NotificationObserver

logger = logging.getLogger(__name__)

class EmailObserver(NotificationObserver):
    def update(self, subject: str, message: str, recipient: str) -> bool:
        """Envía notificaciones por correo electrónico."""
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