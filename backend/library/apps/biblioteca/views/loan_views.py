# views/loan_views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from ..models import Loan
from ..serializers.loan_serializers import LoanCreateSerializer, LoanDetailSerializer
from ..services.loan.loan_service import LoanService
from ..services.report.loan_report_service import LoanReportService

class LoanViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.loan_service = LoanService()
        self.report_service = LoanReportService()

    def get_queryset(self):
        return Loan.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return LoanCreateSerializer
        return LoanDetailSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                loan = self.loan_service.create_loan(
                    user_id=serializer.validated_data['user_id'],
                    book_id=serializer.validated_data['book_id']
                )
                return Response(
                    LoanDetailSerializer(loan).data,
                    status=status.HTTP_201_CREATED
                )
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        try:
            stats = self.report_service.get_loan_statistics()
            return Response(stats)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)