# views/reservation_views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from ..models import Reservation
from ..serializers.reservation_serializers import (
    ReservationCreateSerializer, 
    ReservationDetailSerializer
)

class ReservationViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Reservation.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return ReservationCreateSerializer
        return ReservationDetailSerializer

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