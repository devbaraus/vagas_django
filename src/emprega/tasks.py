from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from emprega.models import Token, TokenTypeChoices


@shared_task(max_retries=3, default_retry_delay=60)
def send_email_confirmation(template: str, user_id: int):
    user = get_user_model().objects.get(id=user_id)

    token, _ = Token.objects.get_or_create(user=user, type=TokenTypeChoices.EMAIL_CONFIRMATION)
    url = f"{settings.FRONTEND_URL}/verificar-email?token={token.token}"

    html_message = render_to_string(template,
                                    {'confirm_url': url, 'user_email': user.email})
    plain_message = strip_tags(html_message)

    send_mail(
        "Confirme seu email",
        plain_message,
        settings.EMAIL_HOST_USER,
        [user.email],
        html_message=html_message
    )


@shared_task(max_retries=3, default_retry_delay=60)
def send_email_reset_password(template: str, user_id: int):
    user = get_user_model().objects.get(id=user_id)

    token, _ = Token.objects.get_or_create(user=user, type=TokenTypeChoices.PASSWORD_RESET)
    url = f"{settings.FRONTEND_URL}/redefinir-senha/?token={token.token}"

    html_message = render_to_string(template,
                                    {'reset_url': url, 'user_email': user.email})
    plain_message = strip_tags(html_message)

    send_mail(
        "Redefinição de senha",
        plain_message,
        settings.EMAIL_HOST_USER,
        [user.email],
        html_message=html_message
    )
