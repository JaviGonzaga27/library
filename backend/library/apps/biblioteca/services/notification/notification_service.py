# services/notification/notification_service.py
from typing import Optional, List
from django.apps import apps
from .email_service import EmailService
from .database_notification_service import DatabaseNotificationService

class NotificationService:
    def __init__(self):
        self.Loan = apps.get_model('biblioteca', 'Loan')
        self.Book = apps.get_model('biblioteca', 'Book')
        self.email_service = EmailService()
        self.db_service = DatabaseNotificationService()

    def send_loan_notification(self, loan: object) -> bool:
        """
        Envía notificación de préstamo nuevo.
        """
        try:
            subject = "Préstamo registrado"
            message = (
                f"Se ha registrado el préstamo del libro '{loan.book.title}' "
                f"hasta el {loan.due_date.strftime('%d/%m/%Y')}."
            )
            
            self.email_service.send_email(subject, message, loan.user.email)
            self.db_service.save_notification(subject, message, loan.user.email)
            return True
        except Exception as e:
            print(f"Error en notificación de préstamo: {e}")
            return False

    def send_due_date_reminder(self, loan: object) -> bool:
        """
        Envía recordatorio de fecha de devolución próxima.
        """
        try:
            subject = "Recordatorio de devolución"
            message = (
                f"El libro '{loan.book.title}' debe ser devuelto "
                f"el día {loan.due_date.strftime('%d/%m/%Y')}."
            )
            
            self.email_service.send_email(subject, message, loan.user.email)
            self.db_service.save_notification(subject, message, loan.user.email)
            return True
        except Exception as e:
            print(f"Error en recordatorio de devolución: {e}")
            return False

    def send_overdue_notification(self, loan: object) -> bool:
        """
        Envía notificación de préstamo vencido.
        """
        try:
            subject = "Préstamo vencido"
            message = (
                f"El libro '{loan.book.title}' está vencido "
                f"desde el {loan.due_date.strftime('%d/%m/%Y')}."
            )
            
            self.email_service.send_email(subject, message, loan.user.email)
            self.db_service.save_notification(subject, message, loan.user.email)
            return True
        except Exception as e:
            print(f"Error en notificación de vencimiento: {e}")
            return False