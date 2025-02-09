# services/report_service.py
from typing import Dict, List, Any
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Count, Q, Avg, F
from django.db.models.functions import TruncMonth

from ..models import Book, Loan, User

class ReportService:
    def get_most_borrowed_books(self, start_date: datetime = None, 
                              end_date: datetime = None,
                              limit: int = 10) -> List[Dict[str, Any]]:
        """
        Obtiene los libros más prestados en un período.
        
        Args:
            start_date (datetime): Fecha inicial del período
            end_date (datetime): Fecha final del período
            limit (int): Cantidad de libros a retornar
            
        Returns:
            List[Dict]: Lista de libros con cantidad de préstamos
        """
        loans = Loan.objects.all()
        
        if start_date:
            loans = loans.filter(loan_date__gte=start_date)
        if end_date:
            loans = loans.filter(loan_date__lte=end_date)
            
        return (
            loans.values('book__title', 'book__author')
            .annotate(total_loans=Count('book'))
            .order_by('-total_loans')[:limit]
        )

    def get_frequent_users(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Obtiene los usuarios más frecuentes.
        
        Args:
            limit (int): Cantidad de usuarios a retornar
            
        Returns:
            List[Dict]: Lista de usuarios con cantidad de préstamos
        """
        return (
            Loan.objects.values(
                'user__username',
                'user__first_name',
                'user__last_name'
            )
            .annotate(total_loans=Count('user'))
            .order_by('-total_loans')[:limit]
        )

    def get_overdue_loans_report(self) -> Dict[str, Any]:
        """
        Genera reporte de préstamos vencidos.
        
        Returns:
            Dict: Estadísticas de préstamos vencidos
        """
        overdue_loans = Loan.objects.filter(
            returned=False,
            due_date__lt=timezone.now().date()
        )
        
        return {
            'total_overdue': overdue_loans.count(),
            'loans_by_days': self._group_by_days_overdue(overdue_loans),
            'users_with_most_overdue': self._get_users_with_most_overdue(overdue_loans)
        }

    def get_monthly_statistics(self, year: int = None) -> Dict[str, Any]:
        """
        Genera estadísticas mensuales de préstamos.
        
        Args:
            year (int): Año para filtrar estadísticas
            
        Returns:
            Dict: Estadísticas mensuales
        """
        loans = Loan.objects.all()
        if year:
            loans = loans.filter(loan_date__year=year)
            
        monthly_loans = (
            loans.annotate(month=TruncMonth('loan_date'))
            .values('month')
            .annotate(
                total_loans=Count('id'),
                avg_loan_duration=Avg(
                    F('returned_date') - F('loan_date'),
                    filter=Q(returned=True)
                )
            )
            .order_by('month')
        )
        
        return {
            'total_loans': loans.count(),
            'monthly_breakdown': list(monthly_loans),
            'most_active_month': self._get_most_active_month(monthly_loans)
        }

    def get_genre_statistics(self) -> List[Dict[str, Any]]:
        """
        Genera estadísticas de préstamos por género literario.
        
        Returns:
            List[Dict]: Estadísticas por género
        """
        return (
            Loan.objects.values('book__genre')
            .annotate(
                total_loans=Count('id'),
                unique_books=Count('book', distinct=True)
            )
            .order_by('-total_loans')
        )

    def _group_by_days_overdue(self, loans: Any) -> Dict[str, int]:
        """Agrupa préstamos vencidos por rangos de días."""
        ranges = {
            '1-7 días': 0,
            '8-15 días': 0,
            '16-30 días': 0,
            'Más de 30 días': 0
        }
        
        for loan in loans:
            days_overdue = (timezone.now().date() - loan.due_date).days
            if days_overdue <= 7:
                ranges['1-7 días'] += 1
            elif days_overdue <= 15:
                ranges['8-15 días'] += 1
            elif days_overdue <= 30:
                ranges['16-30 días'] += 1
            else:
                ranges['Más de 30 días'] += 1
                
        return ranges

    def _get_users_with_most_overdue(self, loans: Any, limit: int = 5) -> List[Dict[str, Any]]:
        """Obtiene usuarios con más préstamos vencidos."""
        return (
            loans.values(
                'user__username',
                'user__first_name',
                'user__last_name'
            )
            .annotate(overdue_count=Count('user'))
            .order_by('-overdue_count')[:limit]
        )

    def _get_most_active_month(self, monthly_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Determina el mes con más actividad de préstamos."""
        if not monthly_data:
            return None
            
        return max(monthly_data, key=lambda x: x['total_loans'])