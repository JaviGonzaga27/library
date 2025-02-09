from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import datetime
from typing import Any

from .models import Book, Loan, Reservation, User
from .serializers import (
    BookSerializer, 
    LoanSerializer, 
    ReservationSerializer,
    UserSerializer
)
from .services.book_service import BookService
from .services.loan_service import LoanService
from .services.notification_service import NotificationService
from .services.report_service import ReportService

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

class BookViewSet(viewsets.ModelViewSet):
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]
    
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.book_service = BookService()

    def get_queryset(self):
        return Book.objects.all()

    def create(self, request, *args, **kwargs):
        try:
            book = self.book_service.create_book(request.data)
            serializer = self.get_serializer(book)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def update(self, request, *args, **kwargs):
        try:
            book = self.book_service.update_book(
                book_id=kwargs['pk'],
                data=request.data
            )
            serializer = self.get_serializer(book)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def destroy(self, request, *args, **kwargs):
        try:
            self.book_service.delete_book(kwargs['pk'])
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def search(self, request):
        query = request.query_params.get('query', '')
        search_type = request.query_params.get('type', 'all')
        
        try:
            books = self.book_service.search_books(query, search_type)
            serializer = self.get_serializer(books, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class LoanViewSet(viewsets.ModelViewSet):
    serializer_class = LoanSerializer
    permission_classes = [IsAuthenticated]
    
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.loan_service = LoanService()
        self.report_service = ReportService()

    def get_queryset(self):
        return Loan.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                loan = self.loan_service.create_loan(
                    user_id=serializer.validated_data['user_id'],
                    book_id=serializer.validated_data['book_id']
                )
                return Response(
                    self.get_serializer(loan).data,
                    status=status.HTTP_201_CREATED
                )
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=['post'])
    def return_book(self, request, pk=None):
        damaged = request.data.get('damaged', False)
        try:
            return_info = self.loan_service.process_return(pk, damaged)
            return Response({
                'loan': self.get_serializer(return_info['loan']).data,
                'fine_amount': return_info['fine_amount'],
                'days_late': return_info['days_late']
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def overdue(self, request):
        overdue_loans = self.loan_service.get_overdue_loans()
        serializer = self.get_serializer(overdue_loans, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            
        stats = self.report_service.get_monthly_statistics()
        most_borrowed = self.report_service.get_most_borrowed_books(
            start_date=start_date,
            end_date=end_date
        )
        
        return Response({
            'monthly_stats': stats,
            'most_borrowed_books': most_borrowed
        })

    @action(detail=False, methods=['post'])
    def check_overdue(self, request):
        self.loan_service.check_and_notify_due_loans()
        return Response({'message': 'Notificaciones enviadas correctamente'})

class ReservationViewSet(viewsets.ModelViewSet):
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Reservation.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                book = get_object_or_404(
                    Book,
                    id=serializer.validated_data['book_id']
                )
                
                if book.status == 'available':
                    return Response(
                        {'error': 'El libro está disponible para préstamo directo'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                    
                reservation = serializer.save()
                return Response(
                    self.get_serializer(reservation).data,
                    status=status.HTTP_201_CREATED
                )
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        reservation = self.get_object()
        if not reservation.active:
            return Response(
                {'error': 'La reservación ya está cancelada'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        reservation.active = False
        reservation.save()
        return Response(self.get_serializer(reservation).data)

    @action(detail=False, methods=['get'])
    def active(self, request):
        active_reservations = self.get_queryset().filter(active=True)
        serializer = self.get_serializer(active_reservations, many=True)
        return Response(serializer.data)