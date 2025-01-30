from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Book, Loan, Reservation

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'

class LoanSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    book_id = serializers.IntegerField(write_only=True)
    user_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Loan
        fields = ['id', 'book', 'user', 'book_id', 'user_id', 'loan_date', 
                 'due_date', 'returned_date', 'returned']

    def create(self, validated_data):
        book_id = validated_data.pop('book_id')
        user_id = validated_data.pop('user_id')
        book = Book.objects.get(id=book_id)
        user = User.objects.get(id=user_id)
        return Loan.objects.create(book=book, user=user, **validated_data)
    
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

class ReservationSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    book_id = serializers.IntegerField(write_only=True)
    user_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Reservation
        fields = ['id', 'book', 'user', 'book_id', 'user_id', 
                 'reservation_date', 'active']

    def create(self, validated_data):
        book_id = validated_data.pop('book_id')
        user_id = validated_data.pop('user_id')
        book = Book.objects.get(id=book_id)
        user = User.objects.get(id=user_id)
        return Reservation.objects.create(book=book, user=user, **validated_data)
    
    def validate(self, data):
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