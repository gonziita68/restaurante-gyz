from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse


def enviar_correo_registro_exitoso(usuario):
    """
    Envía un correo de bienvenida cuando un usuario se registra exitosamente
    """
    try:
        asunto = 'Bienvenido a Restaurante GYZ - Registro Exitoso'
        
        # Renderizar el template HTML
        mensaje_html = render_to_string('usuarios/emails/registro_exitoso.html', {
            'usuario': usuario,
            'nombre_restaurante': 'Restaurante GYZ'
        })
        
        # Versión en texto plano
        mensaje_texto = strip_tags(mensaje_html)
        
        # Enviar el correo
        remitente = settings.EMAIL_HOST_USER or settings.DEFAULT_FROM_EMAIL
        send_mail(
            asunto,
            mensaje_texto,
            remitente,
            [usuario.email],
            html_message=mensaje_html,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error enviando correo de registro: {e}")
        return False


def enviar_correo_recuperacion_password(usuario, request):
    """
    Envía un correo para recuperación de contraseña
    """
    try:
        # Generar token para el reset
        token = default_token_generator.make_token(usuario)
        uid = urlsafe_base64_encode(force_bytes(usuario.pk))
        
        # Construir la URL de reset
        reset_url = request.build_absolute_uri(
            reverse('usuarios:password_reset_confirm', kwargs={
                'uidb64': uid,
                'token': token
            })
        )
        
        asunto = 'Recuperación de Contraseña - Restaurante GYZ'
        
        # Renderizar el template HTML
        mensaje_html = render_to_string('usuarios/emails/recuperacion_password.html', {
            'usuario': usuario,
            'reset_url': reset_url,
            'nombre_restaurante': 'Restaurante GYZ'
        })
        
        # Versión en texto plano
        mensaje_texto = strip_tags(mensaje_html)
        
        # Enviar el correo
        remitente = settings.EMAIL_HOST_USER or settings.DEFAULT_FROM_EMAIL
        send_mail(
            asunto,
            mensaje_texto,
            remitente,
            [usuario.email],
            html_message=mensaje_html,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error enviando correo de recuperación: {e}")
        return False


def enviar_correo_password_cambiado(usuario):
    """
    Envía un correo confirmando que la contraseña fue cambiada exitosamente
    """
    try:
        asunto = 'Contraseña Cambiada Exitosamente - Restaurante GYZ'
        
        # Renderizar el template HTML
        mensaje_html = render_to_string('usuarios/emails/password_cambiado.html', {
            'usuario': usuario,
            'nombre_restaurante': 'Restaurante GYZ'
        })
        
        # Versión en texto plano
        mensaje_texto = strip_tags(mensaje_html)
        
        # Enviar el correo
        remitente = settings.EMAIL_HOST_USER or settings.DEFAULT_FROM_EMAIL
        send_mail(
            asunto,
            mensaje_texto,
            remitente,
            [usuario.email],
            html_message=mensaje_html,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error enviando correo de confirmación: {e}")
        return False 