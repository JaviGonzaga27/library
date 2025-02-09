# serializers/reservation_serializers.py
from rest_framework import serializers
from ..models import Reservation, Book
from .book_serializers import BookDetailSerializer
from .user_serializers import UserSerializer

class ReservationCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear reservaciones"""
    book_id = serializers.IntegerField()
    user_id = serializers.IntegerField()

    class Meta:
        model = Reservation
        fields = ['book_id', 'user_id']

    def validate(self, data):
        try:
            book = Book.objects.get(id=data['book_id'])
            if book.status == 'available':
                raise serializers.ValidationError('Este libro está disponible para préstamo directo')
            return data
        except Book.DoesNotExist:
            raise serializers.ValidationError('Libro no encontrado')

class ReservationDetailSerializer(serializers.ModelSerializer):
    """Serializer para ver detalles de reservaciones"""
    book = BookDetailSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    reservation_date = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)

    class Meta:
        model = Reservation
        fields = ['id', 'book', 'user', 'reservation_date', 'active']