from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from .book import Book

class Loan(models.Model):
    MAX_LOANS = 5  # Constante para el límite máximo de préstamos

    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='loans')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='loans')
    loan_date = models.DateTimeField(default=timezone.now)
    due_date = models.DateField()
    returned_date = models.DateTimeField(null=True, blank=True)
    returned = models.BooleanField(default=False)

    def clean(self):
        if self.book.status != 'available' and not self.id:
            raise ValidationError('Este libro no está disponible para préstamo')
        
        if self.due_date and self.due_date < timezone.now().date():
            raise ValidationError('La fecha de devolución no puede ser anterior a hoy')

        # Verificar límite de préstamos
        active_loans = Loan.objects.filter(
            user=self.user,
            returned=False
        ).count()
        
        if active_loans >= self.MAX_LOANS and not self.id:
            raise ValidationError(f'El usuario ha alcanzado el límite de {self.MAX_LOANS} préstamos')

    def save(self, *args, **kwargs):
        self.clean()
        if not self.id:  # Si es un nuevo préstamo
            self.book.status = 'borrowed'
            self.book.save()
        elif self.returned and not self.returned_date:
            self.returned_date = timezone.now()
            self.book.status = 'available'
            self.book.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.book.title} - {self.user.username}"

    class Meta:
        verbose_name = 'Préstamo'
        verbose_name_plural = 'Préstamos'
        ordering = ['-loan_date']