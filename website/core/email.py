from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _


def send_email_message(question):
    message = render_to_string('core/includes/question.html', {
        'first_name': question.first_name,
        'email': question.email,
        'content': question.content,
    })
    email = EmailMessage(
        _('Question from the website'),
        message,
        settings.SERVER_EMAIL,
        [settings.EMAIL_ADMIN]
    )
    email.send(fail_silently=False)
