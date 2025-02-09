
# serializers/book_serializers.py
from rest_framework import serializers
from ..models import Book

class BookListSerializer(serializers.ModelSerializer):
    """Serializer para listar libros con información básica"""
    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'status']

class BookDetailSerializer(serializers.ModelSerializer):
    """Serializer para ver detalles completos de un libro"""
    created_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    updated_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'genre', 'code', 'status', 'created_at', 'updated_at']
