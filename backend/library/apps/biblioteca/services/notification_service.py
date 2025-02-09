# services/notification_service.py
from typing import Optional
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import datetime

from ..models import Notification, Loan, Book, User
from ..observers import NotificationSubject, EmailNotifier
from ..factories import (
    DueDateNotificationFactory, 
    OverdueNotificationFactory,
    BookAvailableNotificationFactory
)

class NotificationService:
    def __init__(self):
        self.subject = NotificationSubject()
        self.email_notifier = EmailNotifier()
        self.subject.attach(self.email_notifier)

    def send_loan_notification(self, loan: Loan) -> bool:
        """
        Envía notificación de préstamo nuevo.
        
        Args:
            loan (Loan): Préstamo realizado
            
        Returns:
            bool: True si la notificación se envió correctamente
        """
        try:
            factory = DueDateNotificationFactory()
            subject, message = factory.create_notification(loan)
            notification = self._create_notification(
                subject=subject,
                message=message,
                recipient=loan.user.email
            )
            return self.subject.notify(subject, message, loan.user.email)
        except Exception as e:
            self._log_error("loan", loan.id, str(e))
            return False

    def send_due_date_reminder(self, loan: Loan) -> bool:
        """
        Envía recordatorio de fecha de devolución próxima.
        
        Args:
            loan (Loan): Préstamo próximo a vencer
            
        Returns:
            bool: True si la notificación se envió correctamente
        """
        try:
            factory = DueDateNotificationFactory()
            subject, message = factory.create_notification(loan)
            notification = self._create_notification(
                subject=subject,
                message=message,
                recipient=loan.user.email
            )
            return self.subject.notify(subject, message, loan.user.email)
        except Exception as e:
            self._log_error("due_date_reminder", loan.id, str(e))
            return False

    def send_overdue_notification(self, loan: Loan) -> bool:
        """
        Envía notificación de préstamo vencido.
        
        Args:
            loan (Loan): Préstamo vencido
            
        Returns:
            bool: True si la notificación se envió correctamente
        """
        try:
            factory = OverdueNotificationFactory()
            subject, message = factory.create_notification(loan)
            notification = self._create_notification(
                subject=subject,
                message=message,
                recipient=loan.user.email
            )
            return self.subject.notify(subject, message, loan.user.email)
        except Exception as e:
            self._log_error("overdue", loan.id, str(e))
            return False

    def send_long_overdue_notification(self, loan: Loan) -> bool:
        """
        Envía notificación de préstamo con retraso prolongado.
        
        Args:
            loan (Loan): Préstamo con retraso prolongado
            
        Returns:
            bool: True si la notificación se envió correctamente
        """
        try:
            subject = "URGENTE: Préstamo con retraso prolongado"
            message = (
                f"El préstamo del libro '{loan.book.title}' tiene un retraso "
                f"superior a 30 días. Por favor, contacte con el usuario "
                f"{loan.user.get_full_name()} inmediatamente."
            )
            
            # Enviar a bibliotecarios
            admin_emails = User.objects.filter(is_staff=True).values_list('email', flat=True)
            
            for email in admin_emails:
                notification = self._create_notification(subject, message, email)
                self.subject.notify(subject, message, email)
                
            return True
        except Exception as e:
            self._log_error("long_overdue", loan.id, str(e))
            return False

    def notify_book_available(self, book: Book, user: User) -> bool:
        """
        Notifica a un usuario que un libro reservado está disponible.
        
        Args:
            book (Book): Libro disponible
            user (User): Usuario a notificar
            
        Returns:
            bool: True si la notificación se envió correctamente
        """
        try:
            factory = BookAvailableNotificationFactory()
            subject, message = factory.create_notification(book, user)
            notification = self._create_notification(
                subject=subject,
                message=message,
                recipient=user.email
            )
            return self.subject.notify(subject, message, user.email)
        except Exception as e:
            self._log_error("book_available", book.id, str(e))
            return False

    def _create_notification(self, subject: str, message: str, recipient: str) -> Notification:
        """Crea un registro de notificación en la base de datos."""
        return Notification.objects.create(
            subject=subject,
            message=message,
            recipient=recipient
        )

    def _log_error(self, notification_type: str, reference_id: int, error: str) -> None:
        """Registra errores de notificación para debugging."""
        print(f"Error en notificación {notification_type} (ID: {reference_id}): {error}")