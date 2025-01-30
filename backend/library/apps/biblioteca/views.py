from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Book, Loan, Reservation
from django.contrib.auth.models import User
from .serializers import (
    BookSerializer, LoanSerializer, ReservationSerializer, UserSerializer
)
from .observers import NotificationSubject, EmailNotifier
from .factories import DueDateNotificationFactory, OverdueNotificationFactory
from django.db.models import Q
from django.utils import timezone

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    @action(detail=False, methods=['get'])
    def search(self, request):
        query = request.query_params.get('query', '')
        search_type = request.query_params.get('type', 'title')

        if search_type == 'title':
            books = Book.objects.filter(title__icontains=query)
        elif search_type == 'author':
            books = Book.objects.filter(author__icontains=query)
        elif search_type == 'genre':
            books = Book.objects.filter(genre__icontains=query)
        elif search_type == 'code':
            books = Book.objects.filter(code__icontains=query)
        else:
            books = Book.objects.filter(
                Q(title__icontains=query) |
                Q(author__icontains=query) |
                Q(genre__icontains=query) |
                Q(code__icontains=query)
            )

        serializer = self.get_serializer(books, many=True)
        return Response(serializer.data)

class LoanViewSet(viewsets.ModelViewSet):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer
    notification_subject = NotificationSubject()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.notification_subject.attach(EmailNotifier())

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                # Crear el préstamo
                loan = serializer.save()

                # Enviar notificación de préstamo nuevo
                due_date_factory = DueDateNotificationFactory()
                subject, message = due_date_factory.create_notification(loan)
                self.notification_subject.notify(
                    subject=subject,
                    message=message,
                    recipient=loan.user.email
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
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def check_overdue_loans(self):
        """Verifica y notifica préstamos vencidos"""
        overdue_loans = Loan.objects.filter(
            returned=False,
            due_date__lt=timezone.now().date()
        )

        factory = OverdueNotificationFactory()
        for loan in overdue_loans:
            subject, message = factory.create_notification(loan)
            self.notification_subject.notify(
                subject=subject,
                message=message,
                recipient=loan.user.email
            )

    @action(detail=False, methods=['post'])
    def check_overdue(self, request):
        """Endpoint para verificar manualmente préstamos vencidos"""
        self.check_overdue_loans()
        return Response({'message': 'Verificación de préstamos vencidos completada'})

    @action(detail=True, methods=['post'])
    def return_book(self, request, pk=None):
        loan = self.get_object()
        if loan.returned:
            return Response(
                {'error': 'Este libro ya fue devuelto'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        loan.returned = True
        loan.returned_date = timezone.now()
        loan.book.status = 'available'
        loan.book.save()
        loan.save()
        
        return Response(self.get_serializer(loan).data)

class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    notification_subject = NotificationSubject()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                book = get_object_or_404(Book, id=request.data.get('book_id'))
                user = get_object_or_404(User, id=request.data.get('user_id'))

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
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)