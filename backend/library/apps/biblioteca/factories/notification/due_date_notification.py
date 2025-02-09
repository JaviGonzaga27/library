# factories/notification/due_date_notification.py
from typing import Tuple
from django.apps import apps
from ..base_notification import BaseNotificationFactory
from ...models import Loan

class DueDateNotificationFactory(BaseNotificationFactory):
    def __init__(self):
        super().__init__()
        self.Loan = apps.get_model('biblioteca', 'Loan')

    def create_notification(self, loan: 'Loan') -> Tuple[str, str]:
        if not loan.user.email:
            raise ValueError("El usuario no tiene email registrado")

        subject = "Recordatorio de devolución"
        message = (
            f"Estimado/a {loan.user.get_full_name() or loan.user.username},\n\n"
            f"Le recordamos que el libro '{loan.book.title}' debe ser devuelto "
            f"el día {loan.due_date.strftime('%d/%m/%Y')}.\n\n"
            f"Por favor, asegúrese de devolverlo a tiempo para evitar sanciones.\n\n"
            f"Saludos cordiales,\nBiblioteca"
        )
        
        self.save_notification(subject, message, loan.user.email)
        return subject, message