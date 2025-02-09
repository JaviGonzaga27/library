# services/book/book_service.py
from typing import List, Optional
from django.db.models import Q, QuerySet
from django.core.exceptions import ValidationError
from django.apps import apps

class BookService:
    def __init__(self):
        self.Book = apps.get_model('biblioteca', 'Book')
        self.Loan = apps.get_model('biblioteca', 'Loan')

    def create_book(self, data: dict) -> object:
        """Crea un nuevo libro en el sistema."""
        try:
            book = self.Book.objects.create(**data)
            return book
        except Exception as e:
            raise ValidationError(f"Error al crear el libro: {str(e)}")

    def update_book(self, book_id: int, data: dict) -> object:
        """Actualiza los datos de un libro existente."""
        try:
            book = self.get_book_by_id(book_id)
            for key, value in data.items():
                setattr(book, key, value)
            book.save()
            return book
        except Exception as e:
            raise ValidationError(f"Error al actualizar el libro: {str(e)}")

    def delete_book(self, book_id: int) -> bool:
        """Elimina un libro del sistema."""
        book = self.get_book_by_id(book_id)
        
        if self.Loan.objects.filter(book=book, returned=False).exists():
            raise ValidationError("No se puede eliminar un libro con préstamos activos")
            
        book.delete()
        return True

    def get_book_by_id(self, book_id: int) -> object:
        """Obtiene un libro por su ID."""
        try:
            return self.Book.objects.get(id=book_id)
        except self.Book.DoesNotExist:
            raise ValidationError(f"El libro con ID {book_id} no existe")

    def search_books(self, query: str, search_type: str = 'all') -> QuerySet:
        """Busca libros según diferentes criterios."""
        if search_type == 'title':
            return self.Book.objects.filter(title__icontains=query)
        elif search_type == 'author':
            return self.Book.objects.filter(author__icontains=query)
        elif search_type == 'genre':
            return self.Book.objects.filter(genre__icontains=query)
        elif search_type == 'code':
            return self.Book.objects.filter(code__icontains=query)
        else:
            return self.Book.objects.filter(
                Q(title__icontains=query) |
                Q(author__icontains=query) |
                Q(genre__icontains=query) |
                Q(code__icontains=query)
            )