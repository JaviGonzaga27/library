from datetime import datetime, timedelta
from typing import List, Optional
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import QuerySet

from ..models import Loan, Book, User
from .notification_service import NotificationService
from .book_service import BookService

class LoanService:
    def __init__(self):
        self.notification_service = NotificationService()
        self.book_service = BookService()
        self.MAX_LOANS = 5  # Límite máximo de préstamos por usuario
        self.LOAN_DAYS = 15  # Días estándar de préstamo
        self.GRACE_DAYS = 2  # Días de gracia antes de aplicar multa
        self.DAILY_FINE = 10  # Multa diaria por retraso

    def create_loan(self, user_id: int, book_id: int) -> Loan:
        """
        Crea un nuevo préstamo verificando todas las condiciones necesarias.
        
        Args:
            user_id (int): ID del usuario
            book_id (int): ID del libro
            
        Returns:
            Loan: Préstamo creado
            
        Raises:
            ValidationError: Si no se cumplen las condiciones para el préstamo
        """
        # Verificar usuario
        user = self._verify_user(user_id)
        
        # Verificar libro
        book = self._verify_book(book_id)
        
        # Verificar límites de préstamo
        self._verify_loan_limits(user_id)
        
        # Calcular fecha de devolución
        due_date = timezone.now().date() + timedelta(days=self.LOAN_DAYS)
        
        try:
            # Crear el préstamo
            loan = Loan.objects.create(
                user=user,
                book=book,
                due_date=due_date
            )
            
            # Actualizar estado del libro
            self.book_service.update_book_status(book_id, 'borrowed')
            
            # Enviar notificación
            self.notification_service.send_loan_notification(loan)
            
            return loan
            
        except Exception as e:
            raise ValidationError(f"Error al crear el préstamo: {str(e)}")

    def process_return(self, loan_id: int, damaged: bool = False) -> dict:
        """
        Procesa la devolución de un libro.
        
        Args:
            loan_id (int): ID del préstamo
            damaged (bool): Indica si el libro fue devuelto dañado
            
        Returns:
            dict: Información de la devolución incluyendo multas si aplica
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
        
        # Calcular multa si aplica
        if not loan.returned:
            fine_info = self._calculate_fine(loan)
            return_info.update(fine_info)
        
        # Actualizar préstamo
        loan.returned = True
        loan.returned_date = return_info['return_date']
        loan.save()
        
        # Actualizar estado del libro
        new_status = 'damaged' if damaged else 'available'
        self.book_service.update_book_status(loan.book.id, new_status)
        
        return return_info

    def get_active_loans(self, user_id: Optional[int] = None) -> QuerySet:
        """
        Obtiene los préstamos activos, opcionalmente filtrados por usuario.
        
        Args:
            user_id (Optional[int]): ID del usuario para filtrar
            
        Returns:
            QuerySet: Préstamos activos
        """
        loans = Loan.objects.filter(returned=False)
        if user_id:
            loans = loans.filter(user_id=user_id)
        return loans

    def get_overdue_loans(self) -> QuerySet:
        """
        Obtiene todos los préstamos vencidos.
        
        Returns:
            QuerySet: Préstamos vencidos
        """
        return Loan.objects.filter(
            returned=False,
            due_date__lt=timezone.now().date()
        )

    def check_and_notify_due_loans(self) -> None:
        """
        Verifica préstamos próximos a vencer y vencidos para enviar notificaciones.
        """
        # Notificar préstamos próximos a vencer (3 días antes)
        upcoming_due = Loan.objects.filter(
            returned=False,
            due_date=timezone.now().date() + timedelta(days=3)
        )
        for loan in upcoming_due:
            self.notification_service.send_due_date_reminder(loan)
        
        # Notificar préstamos vencidos
        overdue_loans = self.get_overdue_loans()
        for loan in overdue_loans:
            self.notification_service.send_overdue_notification(loan)
            
            # Notificar préstamos con más de 30 días de retraso
            days_overdue = (timezone.now().date() - loan.due_date).days
            if days_overdue >= 30:
                self.notification_service.send_long_overdue_notification(loan)

    def _verify_user(self, user_id: int) -> User:
        """Verifica que el usuario exista y esté activo."""
        try:
            user = User.objects.get(id=user_id)
            if not user.is_active:
                raise ValidationError("El usuario no está activo")
            return user
        except User.DoesNotExist:
            raise ValidationError("Usuario no encontrado")

    def _verify_book(self, book_id: int) -> Book:
        """Verifica que el libro exista y esté disponible."""
        book = self.book_service.get_book_by_id(book_id)
        if book.status != 'available':
            raise ValidationError("El libro no está disponible para préstamo")
        return book

    def _verify_loan_limits(self, user_id: int) -> None:
        """Verifica que el usuario no exceda el límite de préstamos."""
        active_loans = self.get_active_loans(user_id).count()
        if active_loans >= self.MAX_LOANS:
            raise ValidationError(
                f"El usuario ha alcanzado el límite de {self.MAX_LOANS} préstamos"
            )

    def _calculate_fine(self, loan: Loan) -> dict:
        """Calcula la multa por retraso si aplica."""
        today = timezone.now().date()
        days_late = (today - loan.due_date).days
        
        fine_info = {
            'days_late': max(0, days_late),
            'fine_amount': 0
        }
        
        if days_late > self.GRACE_DAYS:
            # Restar días de gracia del cálculo de la multa
            billable_days = days_late - self.GRACE_DAYS
            fine_info['fine_amount'] = billable_days * self.DAILY_FINE
            
        return fine_info

    def _get_loan(self, loan_id: int) -> Loan:
        """Obtiene un préstamo por su ID."""
        try:
            return Loan.objects.get(id=loan_id)
        except Loan.DoesNotExist:
            raise ValidationError(f"Préstamo {loan_id} no encontrado")