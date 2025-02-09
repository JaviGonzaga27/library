# services/loan/loan_service.py
from datetime import timedelta
from typing import Dict, Any
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.apps import apps

class LoanService:
    def __init__(self):
        self.Loan = apps.get_model('biblioteca', 'Loan')
        self.Book = apps.get_model('biblioteca', 'Book')
        self.User = apps.get_model('auth', 'User')
        self.MAX_LOANS = 5
        self.LOAN_DAYS = 15
        self.GRACE_DAYS = 2
        self.DAILY_FINE = 10

    def create_loan(self, user_id: int, book_id: int) -> object:
        """Crea un nuevo préstamo."""
        user = self._verify_user(user_id)
        book = self._verify_book(book_id)
        self._verify_loan_limits(user_id)
        
        due_date = timezone.now().date() + timedelta(days=self.LOAN_DAYS)
        
        try:
            loan = self.Loan.objects.create(
                user=user,
                book=book,
                due_date=due_date
            )
            book.status = 'borrowed'
            book.save()
            return loan
        except Exception as e:
            raise ValidationError(f"Error al crear el préstamo: {str(e)}")

    def process_return(self, loan_id: int, damaged: bool = False) -> Dict[str, Any]:
        """Procesa la devolución de un libro."""
        loan = self._get_loan(loan_id)
        
        if loan.returned:
            raise ValidationError("Este préstamo ya fue devuelto")
        
        return_info = {
            'loan': loan,
            'return_date': timezone.now(),
            'fine_amount': 0,
            'days_late': 0
        }
        
        if not loan.returned:
            fine_info = self._calculate_fine(loan)
            return_info.update(fine_info)
        
        loan.returned = True
        loan.returned_date = return_info['return_date']
        loan.save()
        
        new_status = 'damaged' if damaged else 'available'
        loan.book.status = new_status
        loan.book.save()
        
        return return_info

    def _verify_user(self, user_id: int) -> object:
        """Verifica que el usuario exista y esté activo."""
        try:
            user = self.User.objects.get(id=user_id)
            if not user.is_active:
                raise ValidationError("El usuario no está activo")
            return user
        except self.User.DoesNotExist:
            raise ValidationError("Usuario no encontrado")

    def _verify_book(self, book_id: int) -> object:
        """Verifica que el libro exista y esté disponible."""
        try:
            book = self.Book.objects.get(id=book_id)
            if book.status != 'available':
                raise ValidationError("El libro no está disponible para préstamo")
            return book
        except self.Book.DoesNotExist:
            raise ValidationError("Libro no encontrado")

    def _verify_loan_limits(self, user_id: int) -> None:
        """Verifica que el usuario no exceda el límite de préstamos."""
        active_loans = self.Loan.objects.filter(
            user_id=user_id,
            returned=False
        ).count()
        
        if active_loans >= self.MAX_LOANS:
            raise ValidationError(
                f"El usuario ha alcanzado el límite de {self.MAX_LOANS} préstamos"
            )

    def _calculate_fine(self, loan: object) -> Dict[str, Any]:
        """Calcula la multa por retraso si aplica."""
        today = timezone.now().date()
        days_late = (today - loan.due_date).days
        
        fine_info = {
            'days_late': max(0, days_late),
            'fine_amount': 0
        }
        
        if days_late > self.GRACE_DAYS:
            billable_days = days_late - self.GRACE_DAYS
            fine_info['fine_amount'] = billable_days * self.DAILY_FINE
            
        return fine_info
    
    def _get_loan(self, loan_id: int) -> object:
        """
        Obtiene un préstamo por su ID.
        
        Args:
            loan_id (int): ID del préstamo
            
        Returns:
            object: Instancia del préstamo
            
        Raises:
            ValidationError: Si el préstamo no existe
        """
        try:
            return self.Loan.objects.get(id=loan_id)
        except self.Loan.DoesNotExist:
            raise ValidationError(f"Préstamo con ID {loan_id} no encontrado")

    def process_return(self, loan_id: int, damaged: bool = False) -> Dict[str, Any]:
        """
        Procesa la devolución de un libro.
        
        Args:
            loan_id (int): ID del préstamo
            damaged (bool): Indica si el libro fue devuelto dañado
            
        Returns:
            Dict[str, Any]: Información de la devolución
        """
        loan = self._get_loan(loan_id)
        
        if loan.returned:
            raise ValidationError("Este préstamo ya fue devuelto")
        
        return_info = {
            'loan': loan,
            'return_date': timezone.now(),
            'fine_amount': 0,
            'days_late': 0
        }
        
        if not loan.returned:
            fine_info = self._calculate_fine(loan)
            return_info.update(fine_info)
        
        loan.returned = True
        loan.returned_date = return_info['return_date']
        loan.save()
        
        new_status = 'damaged' if damaged else 'available'
        loan.book.status = new_status
        loan.book.save()
        
        return return_info