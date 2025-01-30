from django.contrib import admin
from django.core.mail import send_mail
from django.contrib import messages
from .models import Book, Loan, Reservation, Notification
from django.utils import timezone

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'genre', 'code', 'status')
    search_fields = ('title', 'author', 'code')
    list_filter = ('status', 'genre')
    ordering = ('title', 'author')
    list_per_page = 20

@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ('book', 'user', 'loan_date', 'due_date', 'returned')
    list_filter = ('returned', 'loan_date')
    search_fields = ('book__title', 'user__username')
    date_hierarchy = 'loan_date'
    list_per_page = 20
    actions = ['check_overdue_loans']

    def check_overdue_loans(self, request, queryset):
        try:
            from .factories import OverdueNotificationFactory
            from .observers import NotificationSubject, EmailNotifier
            
            notification_subject = NotificationSubject()
            notification_subject.attach(EmailNotifier())
            factory = OverdueNotificationFactory()

            overdue_loans = Loan.objects.filter(
                returned=False,
                due_date__lt=timezone.now().date()
            )

            notifications_sent = 0
            for loan in overdue_loans:
                subject, message = factory.create_notification(loan)
                notification_subject.notify(subject, message, loan.user.email)
                notifications_sent += 1

            self.message_user(
                request, 
                f'Se enviaron {notifications_sent} notificaciones de préstamos vencidos'
            )
        except Exception as e:
            self.message_user(
                request, 
                f'Error al verificar préstamos vencidos: {str(e)}',
                level=messages.ERROR
            )

    check_overdue_loans.short_description = "Verificar préstamos vencidos"

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('book', 'user', 'reservation_date', 'active')
    list_filter = ('active', 'reservation_date')
    search_fields = ('book__title', 'user__username')
    date_hierarchy = 'reservation_date'
    list_per_page = 20

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('subject', 'recipient', 'created_at', 'read')
    list_filter = ('read', 'created_at')
    search_fields = ('subject', 'recipient')
    date_hierarchy = 'created_at'
    list_per_page = 20