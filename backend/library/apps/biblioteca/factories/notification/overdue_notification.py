# factories/notification/overdue_notification.py
from typing import Tuple
from ...models import Loan
from ..base_notification import BaseNotificationFactory

class OverdueNotificationFactory(BaseNotificationFactory):
    def create_notification(self, loan: Loan) -> Tuple[str, str]:
        if not loan.user.email:
            raise ValueError("El usuario no tiene email registrado")

        subject = "Préstamo vencido"
        message = (
            f"Estimado/a {loan.user.get_full_name() or loan.user.username},\n\n"
            f"El libro '{loan.book.title}' que tiene en préstamo está vencido "
            f"desde el {loan.due_date.strftime('%d/%m/%Y')}.\n\n"
            f"Por favor, devuélvalo lo antes posible para evitar sanciones adicionales.\n\n"
            f"Saludos cordiales,\nBiblioteca"
        )
        
        self.save_notification(subject, message, loan.user.email)
        return subject, message