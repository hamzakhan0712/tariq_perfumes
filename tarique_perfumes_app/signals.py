from urllib import request
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.models import User  # Assuming your user model is named 'User'

@receiver(post_save, sender=User)
def send_welcome_email(sender, instance, created, **kwargs):
    if created:
        subject = 'Welcome to Tarique Perfumes'
        message = render_to_string('welcome_email.html', {'user': instance})
        from_email = settings.EMAIL_HOST_USER
        to_email = instance.email
        send_mail(subject, '', from_email, [to_email], html_message=message)

