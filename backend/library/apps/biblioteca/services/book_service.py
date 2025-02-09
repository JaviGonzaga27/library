from typing import List, Optional
from django.db.models import Q, QuerySet
from django.core.exceptions import ValidationError
from django.utils import timezone

from ..models import Book, Loan, Reservation
from .notification_service import NotificationService

class BookService:
    def __init__(self):
        self.notification_service = NotificationService()

    def create_book(self, data: dict) -> Book:
        """
        Crea un nuevo libro en el sistema.
        
        Args:
            data (dict): Diccionario con los datos del libro
            
        Returns:
            Book: Instancia del libro creado
            
        Raises:
            ValidationError: Si los datos son inválidos
        """
        try:
            book = Book.objects.create(**data)
            return book
        except Exception as e:
            raise ValidationError(f"Error al crear el libro: {str(e)}")

    def update_book(self, book_id: int, data: dict) -> Book:
        """
        Actualiza los datos de un libro existente.
        
        Args:
            book_id (int): ID del libro a actualizar
            data (dict): Datos a actualizar
            
        Returns:
            Book: Libro actualizado
            
        Raises:
            ValidationError: Si el libro no existe o los datos son inválidos
        """
        try:
            book = self.get_book_by_id(book_id)
            for key, value in data.items():
                setattr(book, key, value)
            book.save()
            return book
        except Exception as e:
            raise ValidationError(f"Error al actualizar el libro: {str(e)}")

    def delete_book(self, book_id: int) -> bool:
        """
        Elimina un libro del sistema.
        
        Args:
            book_id (int): ID del libro a eliminar
            
        Returns:
            bool: True si se eliminó correctamente
            
        Raises:
            ValidationError: Si el libro no existe o tiene préstamos activos
        """
        book = self.get_book_by_id(book_id)
        
        # Verificar si tiene préstamos activos
        if Loan.objects.filter(book=book, returned=False).exists():
            raise ValidationError("No se puede eliminar un libro con préstamos activos")
            
        book.delete()
        return True

    def get_book_by_id(self, book_id: int) -> Book:
        """
        Obtiene un libro por su ID.
        
        Args:
            book_id (int): ID del libro
            
        Returns:
            Book: Instancia del libro
            
        Raises:
            ValidationError: Si el libro no existe
        """
        try:
            return Book.objects.get(id=book_id)
        except Book.DoesNotExist:
            raise ValidationError(f"El libro con ID {book_id} no existe")

    def search_books(self, query: str, search_type: str = 'all') -> QuerySet:
        """
        Busca libros según diferentes criterios.
        
        Args:
            query (str): Término de búsqueda
            search_type (str): Tipo de búsqueda ('title', 'author', 'genre', 'code', 'all')
            
        Returns:
            QuerySet: QuerySet con los resultados
        """
        if search_type == 'title':
            return Book.objects.filter(title__icontains=query)
        elif search_type == 'author':
            return Book.objects.filter(author__icontains=query)
        elif search_type == 'genre':
            return Book.objects.filter(genre__icontains=query)
        elif search_type == 'code':
            return Book.objects.filter(code__icontains=query)
        else:
            return Book.objects.filter(
                Q(title__icontains=query) |
                Q(author__icontains=query) |
                Q(genre__icontains=query) |
                Q(code__icontains=query)
            )

    def update_book_status(self, book_id: int, status: str) -> Book:
        """
        Actualiza el estado de un libro.
        
        Args:
            book_id (int): ID del libro
            status (str): Nuevo estado ('available', 'borrowed', 'lost', 'damaged')
            
        Returns:
            Book: Libro actualizado
            
        Raises:
            ValidationError: Si el estado es inválido
        """
        valid_statuses = ['available', 'borrowed', 'lost', 'damaged']
        if status not in valid_statuses:
            raise ValidationError(f"Estado inválido. Debe ser uno de: {', '.join(valid_statuses)}")
            
        book = self.get_book_by_id(book_id)
        book.status = status
        book.save()
        
        # Si el libro está disponible, notificar a usuarios con reservas
        if status == 'available':
            self._notify_book_available(book)
            
        return book

    def check_availability(self, book_id: int) -> bool:
        """
        Verifica si un libro está disponible para préstamo.
        
        Args:
            book_id (int): ID del libro
            
        Returns:
            bool: True si está disponible
        """
        book = self.get_book_by_id(book_id)
        return book.status == 'available'

    def get_active_reservations(self, book_id: int) -> QuerySet:
        """
        Obtiene las reservas activas de un libro.
        
        Args:
            book_id (int): ID del libro
            
        Returns:
            QuerySet: Reservas activas
        """
        return Reservation.objects.filter(
            book_id=book_id,
            active=True
        ).order_by('reservation_date')

    def _notify_book_available(self, book: Book) -> None:
        """
        Notifica a los usuarios con reservas activas que el libro está disponible.
        
        Args:
            book (Book): Libro que está disponible
        """
        reservations = self.get_active_reservations(book.id)
        if reservations.exists():
            first_reservation = reservations.first()
            self.notification_service.notify_book_available(book, first_reservation.user)