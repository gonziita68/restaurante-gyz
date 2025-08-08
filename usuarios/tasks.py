from celery import shared_task
from django.core.mail import send_mail
from django.utils.html import strip_tags
from django.conf import settings
from django.utils import timezone
from .models import EmailLog, Usuario
from django.template.loader import render_to_string

@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=5, retry_kwargs={'max_retries': 3})
def send_email_task(self, *, to_email: str, subject: str, template: str, context: dict, purpose: str = 'other'):
    log = EmailLog.objects.create(
        user=Usuario.objects.filter(email=to_email).first(),
        to_email=to_email,
        subject=subject,
        template=template,
        purpose=purpose,
        status='queued',
    )
    try:
        html = render_to_string(template, context)
        text = strip_tags(html)
        remitente = settings.EMAIL_HOST_USER or settings.DEFAULT_FROM_EMAIL
        sent = send_mail(subject, text, remitente, [to_email], html_message=html, fail_silently=False)
        log.status = 'sent' if sent else 'error'
        log.sent_at = timezone.now()
        log.save(update_fields=['status', 'sent_at'])
        return sent
    except Exception as exc:
        log.status = 'error'
        log.error_message = str(exc)
        log.save(update_fields=['status', 'error_message'])
        raise