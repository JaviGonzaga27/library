from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

class Reservation(models.Model):
    book = models.ForeignKey('biblioteca.Book', on_delete=models.CASCADE, related_name='reservations')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservations')
    reservation_date = models.DateTimeField(default=timezone.now)
    active = models.BooleanField(default=True)

    def clean(self):
        if self.book.status == 'available':
            raise ValidationError('Este libro está disponible para préstamo directo')

        if self.active and Reservation.objects.filter(
            book=self.book,
            user=self.user,
            active=True
        ).exists() and not self.id:
            raise ValidationError('Ya tienes una reservación activa para este libro')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.book.title} - {self.user.username}"

    class Meta:
        verbose_name = 'Reservación'
        verbose_name_plural = 'Reservaciones'
        ordering = ['-reservation_date']