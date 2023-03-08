from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator


def send_code_email(user):
    """Отправка сообщения на почтус токеном доступа"""

    subject = 'Активируйте ваш аккаунт'
    confirmation_code = default_token_generator.make_token(user)
    message = f'{confirmation_code} - ваш код подтверждения'
    admin_email = settings.EMAIL_HOST
    return send_mail(subject, message, admin_email, [user.email])
