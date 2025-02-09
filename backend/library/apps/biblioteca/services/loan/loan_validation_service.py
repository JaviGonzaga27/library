# services/loan/loan_validation_service.py
from datetime import datetime
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.apps import apps

class LoanValidationService:
    def __init__(self):
        self.Loan = apps.get_model('biblioteca', 'Loan')
        self.MAX_LOANS = 5

    def validate_loan_limits(self, user_id: int) -> bool:
        """Valida los límites de préstamo para un usuario."""
        active_loans = self.Loan.objects.filter(
            user_id=user_id,
            returned=False
        ).count()
        return active_loans < self.MAX_LOANS

    def validate_due_date(self, due_date: datetime) -> bool:
        """Valida que la fecha de devolución sea válida."""
        if due_date < timezone.now().date():
            raise ValidationError("La fecha de devolución no puede ser anterior a hoy")
        return True

    def can_extend_loan(self, loan_id: int) -> bool:
        """Verifica si un préstamo puede ser extendido."""
        try:
            loan = self.Loan.objects.get(id=loan_id)
            if loan.returned:
                return False
            if loan.due_date < timezone.now().date():
                return False
            return True
        except self.Loan.DoesNotExist:
            raise ValidationError("Préstamo no encontrado")