# factories/notification/book_availability_notification.py
from typing import Tuple
from django.contrib.auth.models import User
from ...models import Book
from ..base_notification import BaseNotificationFactory

class BookAvailableNotificationFactory(BaseNotificationFactory):
    def create_notification(self, book: Book, user: User) -> Tuple[str, str]:
        if not user.email:
            raise ValueError("El usuario no tiene email registrado")

        subject = "Libro disponible"
        message = (
            f"Estimado/a {user.get_full_name() or user.username},\n\n"
            f"El libro '{book.title}' que reservó ya está disponible.\n\n"
            f"Por favor, pase por la biblioteca para retirarlo en los próximos 2 días.\n\n"
            f"Saludos cordiales,\nBiblioteca"
        )
        
        self.save_notification(subject, message, user.email)
        return subject, message