# services/book/book_availability_service.py
from django.core.exceptions import ValidationError
from django.apps import apps
from django.db.models import QuerySet

class BookAvailabilityService:
    def __init__(self):
        self.Book = apps.get_model('biblioteca', 'Book')
        self.Reservation = apps.get_model('biblioteca', 'Reservation')

    def update_book_status(self, book_id: int, status: str) -> object:
        """Actualiza el estado de un libro."""
        valid_statuses = ['available', 'borrowed', 'lost', 'damaged']
        if status not in valid_statuses:
            raise ValidationError(f"Estado inválido. Debe ser uno de: {', '.join(valid_statuses)}")
            
        book = self.get_book_by_id(book_id)
        book.status = status
        book.save()
        return book

    def check_availability(self, book_id: int) -> bool:
        """Verifica si un libro está disponible para préstamo."""
        book = self.get_book_by_id(book_id)
        return book.status == 'available'

    def get_active_reservations(self, book_id: int) -> QuerySet:
        """Obtiene las reservas activas de un libro."""
        return self.Reservation.objects.filter(
            book_id=book_id,
            active=True
        ).order_by('reservation_date')