# services/report/book_report_service.py
from typing import Dict, List, Any
from datetime import datetime
from django.db.models import Count, Q
from django.apps import apps

class BookReportService:
    def __init__(self):
        self.Book = apps.get_model('biblioteca', 'Book')
        self.Loan = apps.get_model('biblioteca', 'Loan')

    def get_most_borrowed_books(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Obtiene los libros más prestados."""
        return (
            self.Loan.objects.values(
                'book__title',
                'book__author'
            )
            .annotate(total_loans=Count('book'))
            .order_by('-total_loans')[:limit]
        )

    def get_genre_statistics(self) -> List[Dict[str, Any]]:
        """Obtiene estadísticas por género."""
        return (
            self.Book.objects.values('genre')
            .annotate(
                total_books=Count('id'),
                available_books=Count(
                    'id',
                    filter=Q(status='available')
                ),
                borrowed_books=Count(
                    'id',
                    filter=Q(status='borrowed')
                )
            )
            .order_by('genre')
        )