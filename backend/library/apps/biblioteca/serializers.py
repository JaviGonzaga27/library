from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Book, Loan, Reservation

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class BookSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    updated_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'genre', 'code', 'status', 'created_at', 'updated_at']

class LoanSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    book_id = serializers.IntegerField(write_only=True)
    user_id = serializers.IntegerField(write_only=True)
    loan_date = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)
    due_date = serializers.DateField(format='%Y-%m-%d')
    returned_date = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)

    class Meta:
        model = Loan
        fields = [
            'id', 'book', 'user', 'book_id', 'user_id', 
            'loan_date', 'due_date', 'returned_date', 'returned'
        ]

    def validate_book_id(self, value):
        try:
            book = Book.objects.get(id=value)
            if book.status != 'available':
                raise serializers.ValidationError(
                    'Este libro no está disponible para préstamo'
                )
            return value
        except Book.DoesNotExist:
            raise serializers.ValidationError('Libro no encontrado')

    def validate_user_id(self, value):
        try:
            user = User.objects.get(id=value)
            if not user.is_active:
                raise serializers.ValidationError('Usuario inactivo')
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError('Usuario no encontrado')

class ReservationSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    book_id = serializers.IntegerField(write_only=True)
    user_id = serializers.IntegerField(write_only=True)
    reservation_date = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)

    class Meta:
        model = Reservation
        fields = [
            'id', 'book', 'user', 'book_id', 'user_id', 
            'reservation_date', 'active'
        ]

    def validate(self, data):
        try:
            book = Book.objects.get(id=data['book_id'])
            user = User.objects.get(id=data['user_id'])

            if book.status == 'available':
                raise serializers.ValidationError(
                    'Este libro está disponible para préstamo directo'
                )

            if Reservation.objects.filter(
                book=book,
                user=user,
                active=True
            ).exists():
                raise serializers.ValidationError(
                    'Ya existe una reservación activa para este libro'
                )

            return data
        except Book.DoesNotExist:
            raise serializers.ValidationError('Libro no encontrado')
        except User.DoesNotExist:
            raise serializers.ValidationError('Usuario no encontrado')