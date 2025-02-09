# services/notification/email_service.py
from typing import Optional
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class EmailService:
    def send_email(self, subject: str, message: str, recipient: str) -> bool:
        """
        Envía un email usando la configuración de Django.
        """
        try:
            if not recipient:
                raise ValueError("Email de destinatario no proporcionado")

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