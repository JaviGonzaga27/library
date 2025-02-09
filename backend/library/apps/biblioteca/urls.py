# biblioteca/urls.py (URLs de la aplicación)
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BookViewSet, 
    LoanViewSet, 
    ReservationViewSet,
    UserViewSet
)

# Crear router y registrar viewsets
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'books', BookViewSet, basename='book')
router.register(r'loans', LoanViewSet, basename='loan')
router.register(r'reservations', ReservationViewSet, basename='reservation')

urlpatterns = [
    path('', include(router.urls)),
]

# Las URLs generadas automáticamente incluirán:
# /api/users/
# /api/books/
# /api/books/search/
# /api/loans/
# /api/loans/return_book/
# /api/loans/overdue/
# /api/loans/statistics/
# /api/reservations/
# /api/reservations/active/
# /api/reservations/cancel/