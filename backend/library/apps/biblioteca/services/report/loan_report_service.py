# services/report/loan_report_service.py
from typing import Dict, List, Any
from datetime import datetime
from django.db.models import Count, Q, Avg, F
from django.db.models.functions import TruncMonth
from django.apps import apps
from django.utils import timezone
from django.db.models.query import QuerySet

class LoanReportService:
    def __init__(self):
        self.Loan = apps.get_model('biblioteca', 'Loan')

    def get_loan_statistics(self, start_date: datetime = None, 
                          end_date: datetime = None) -> Dict[str, Any]:
        """Genera estadísticas de préstamos."""
        loans = self.Loan.objects.all()
        
        if start_date:
            loans = loans.filter(loan_date__gte=start_date)
        if end_date:
            loans = loans.filter(loan_date__lte=end_date)

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
            'overdue_loans': self._get_overdue_statistics(loans),
            'user_statistics': self._get_user_statistics(loans)
        }

    def _get_overdue_statistics(self, loans: QuerySet) -> Dict[str, Any]:
        """Obtiene estadísticas de préstamos vencidos."""
        overdue = loans.filter(
            returned=False,
            due_date__lt=timezone.now().date()
        )
        
        return {
            'total_overdue': overdue.count(),
            'overdue_by_days': self._group_by_days_overdue(overdue)
        }

    def _get_user_statistics(self, loans: QuerySet) -> List[Dict[str, Any]]:
        """Obtiene estadísticas por usuario."""
        return (
            loans.values(
                'user__username',
                'user__email'
            )
            .annotate(
                total_loans=Count('id'),
                overdue_loans=Count(
                    'id',
                    filter=Q(
                        returned=False,
                        due_date__lt=timezone.now().date()
                    )
                )
            )
            .order_by('-total_loans')
        )