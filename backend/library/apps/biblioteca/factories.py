from abc import ABC, abstractmethod
from datetime import datetime
from typing import Tuple, Optional
from django.contrib.auth.models import User
from .models import Book, Loan, Notification

class NotificationFactory(ABC):
    @abstractmethod
    def create_notification(self) -> Tuple[str, str]:
        """
        Método abstracto que debe ser implementado por las clases hijas.
        Returns:
            Tuple[str, str]: Una tupla con (asunto, mensaje)
        """
        pass

    def save_notification(self, subject: str, message: str, recipient: str) -> Optional[Notification]:
        """
        Guarda la notificación en la base de datos.
        Args:
            subject (str): Asunto de la notificación
            message (str): Mensaje de la notificación
            recipient (str): Email del destinatario
        Returns:
            Optional[Notification]: La notificación creada o None si hay error
        """
        try:
            return Notification.objects.create(
                subject=subject,
                message=message,
                recipient=recipient
            )
        except Exception as e:
            print(f"Error al guardar la notificación: {e}")
            return None

class DueDateNotificationFactory(NotificationFactory):
    def create_notification(self, loan: Loan) -> Tuple[str, str]:
        if not loan.user.email:
            raise ValueError("El usuario no tiene email registrado")

        subject = "Recordatorio de devolución"
        message = (
            f"Estimado/a {loan.user.get_full_name() or loan.user.username},\n\n"
            f"Le recordamos que el libro '{loan.book.title}' debe ser devuelto "
            f"el día {loan.due_date.strftime('%d/%m/%Y')}.\n\n"
            f"Por favor, asegúrese de devolverlo a tiempo para evitar sanciones.\n\n"
            f"Saludos cordiales,\nBiblioteca"
        )
        
        self.save_notification(subject, message, loan.user.email)
        return subject, message

class OverdueNotificationFactory(NotificationFactory):
    def create_notification(self, loan: Loan) -> Tuple[str, str]:
        if not loan.user.email:
            raise ValueError("El usuario no tiene email registrado")

        subject = "Préstamo vencido"
        message = (
            f"Estimado/a {loan.user.get_full_name() or loan.user.username},\n\n"
            f"El libro '{loan.book.title}' que tiene en préstamo está vencido "
            f"desde el {loan.due_date.strftime('%d/%m/%Y')}.\n\n"
            f"Por favor, devuélvalo lo antes posible para evitar sanciones adicionales.\n\n"
            f"Saludos cordiales,\nBiblioteca"
        )
        
        self.save_notification(subject, message, loan.user.email)
        return subject, message

class BookAvailableNotificationFactory(NotificationFactory):
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

class NewAcquisitionNotificationFactory(NotificationFactory):
    def create_notification(self, book: Book) -> Tuple[str, str]:
        subject = "Nueva adquisición"
        message = (
            f"¡Nueva adquisición en la biblioteca!\n\n"
            f"Título: {book.title}\n"
            f"Autor: {book.author}\n"
            f"Género: {book.genre}\n"
            f"Código: {book.code}\n\n"
            f"Ya está disponible para préstamo.\n\n"
            f"Saludos cordiales,\nBiblioteca"
        )
        return subject, message