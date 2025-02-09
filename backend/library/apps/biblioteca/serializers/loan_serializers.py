# serializers/loan_serializers.py
from rest_framework import serializers
from ..models import Loan, Book
from .book_serializers import BookDetailSerializer
from .user_serializers import UserSerializer

class LoanCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear préstamos"""
    book_id = serializers.IntegerField()
    user_id = serializers.IntegerField()

    class Meta:
        model = Loan
        fields = ['book_id', 'user_id', 'due_date']

    def validate_book_id(self, value):
        try:
            book = Book.objects.get(id=value)
            if book.status != 'available':
                raise serializers.ValidationError('Este libro no está disponible para préstamo')
            return value
        except Book.DoesNotExist:
            raise serializers.ValidationError('Libro no encontrado')

class LoanDetailSerializer(serializers.ModelSerializer):
    """Serializer para ver detalles de préstamos"""
    book = BookDetailSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    loan_date = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)
    due_date = serializers.DateField(format='%Y-%m-%d')
    returned_date = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)

    class Meta:
        model = Loan
        fields = ['id', 'book', 'user', 'loan_date', 'due_date', 'returned_date', 'returned']
