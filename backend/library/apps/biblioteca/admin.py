from django.contrib import admin
from .models import Book, Loan, Reservation, Notification

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'status', 'code')
    search_fields = ('title', 'author', 'code')
    list_filter = ('status', 'genre')

@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ('book', 'user', 'loan_date', 'due_date', 'returned')
    list_filter = ('returned', 'loan_date')
    search_fields = ('book__title', 'user__username')

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('book', 'user', 'reservation_date', 'active')
    list_filter = ('active', 'reservation_date')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('subject', 'recipient', 'created_at', 'read')
    list_filter = ('read', 'created_at')