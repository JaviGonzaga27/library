from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    genre = models.CharField(max_length=100)
    code = models.CharField(max_length=50, unique=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('available', 'Disponible'),
            ('borrowed', 'En préstamo'),
            ('lost', 'Perdido'),
            ('damaged', 'Dañado')
        ],
        default='available'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.author}"

    class Meta:
        verbose_name = 'Libro'
        verbose_name_plural = 'Libros'

class Loan(models.Model):
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

    def save(self, *args, **kwargs):
        if not self.id:  # Si es un nuevo préstamo
            self.book.status = 'borrowed'
            self.book.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.book.title} - {self.user.username}"

    class Meta:
        verbose_name = 'Préstamo'
        verbose_name_plural = 'Préstamos'

class Reservation(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reservations')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservations')
    reservation_date = models.DateTimeField(default=timezone.now)
    active = models.BooleanField(default=True)

    def clean(self):
        # Verificar si el usuario ya tiene una reservación activa para este libro
        if self.active and Reservation.objects.filter(
            book=self.book,
            user=self.user,
            active=True
        ).exists() and not self.id:  # Añadido not self.id para permitir actualizaciones
            raise ValidationError('Ya tienes una reservación activa para este libro')

        # Verificar si el libro está disponible
        if self.book.status == 'available':
            raise ValidationError('Este libro está disponible para préstamo directo')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.book.title} - {self.user.username}"

    class Meta:
        verbose_name = 'Reservación'
        verbose_name_plural = 'Reservaciones'

class Notification(models.Model):
    subject = models.CharField(max_length=200)
    message = models.TextField()
    recipient = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.subject} - {self.recipient}"

    class Meta:
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'