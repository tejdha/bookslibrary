from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User
from django.core.mail import send_mail
from django.conf import settings

@receiver(post_save, sender=User)
def send_welcome_email(sender, instance, created, **kwargs):
    if not created:
        return
    if not instance.email:
        return

    send_mail(
        subject="Welcome To BooksLibrary",
        message=f""""
        Hi {instance.username},
        Welcome to BooksLibrary!
        We're Exiceted to have you with us.
        Happy Reading!


        Regards,
        BooksLibrary Team        
        """,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[instance.email],
        fail_silently=False,
    )