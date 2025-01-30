from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BookViewSet, 
    LoanViewSet, 
    ReservationViewSet,
    UserViewSet
)

router = DefaultRouter()
router.register(r'books', BookViewSet, basename='book')
router.register(r'loans', LoanViewSet, basename='loan')
router.register(r'reservations', ReservationViewSet, basename='reservation')
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
]