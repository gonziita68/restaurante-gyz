from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from datetime import datetime

def enviar_email_reserva_confirmada(reserva):
    """Envía email de confirmación de reserva exitosa"""
    try:
        subject = f'✅ Reserva Confirmada - Restaurante GYZ #{str(reserva.codigo_reserva)[:8]}'
        
        # Contexto para el template
        context = {
            'reserva': reserva,
            'fecha_reserva': reserva.fecha_reserva.strftime('%d/%m/%Y'),
            'hora_reserva': reserva.hora_reserva.strftime('%H:%M'),
            'codigo_corto': str(reserva.codigo_reserva)[:8],
            'fecha_actual': timezone.now().strftime('%d/%m/%Y %H:%M'),
        }
        
        # Renderizar template HTML
        html_message = render_to_string('emails/reserva_confirmada.html', context)
        
        # Mensaje de texto plano como fallback
        plain_message = f"""
        ¡Reserva Confirmada!
        
        Hola {reserva.nombre_cliente},
        
        Tu reserva ha sido confirmada exitosamente.
        
        📅 Fecha: {reserva.fecha_reserva.strftime('%d/%m/%Y')}
        🕐 Hora: {reserva.hora_reserva.strftime('%H:%M')}
        👥 Comensales: {reserva.numero_comensales} persona{'s' if reserva.numero_comensales > 1 else ''}
        🪑 Mesa: {reserva.mesa.numero} ({reserva.mesa.tipo_mesa.nombre})
        📍 Ubicación: {reserva.mesa.get_ubicacion_display()}
        🔢 Código: {str(reserva.codigo_reserva)[:8]}
        
        ¡Te esperamos en Restaurante GYZ!
        
        Para consultar tu reserva: http://localhost:8000/reservas/consultar/
        
        Saludos,
        Equipo Restaurante GYZ
        """
        
        # Enviar email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[reserva.email_cliente],
            html_message=html_message,
            fail_silently=False,
        )
        
        return True
        
    except Exception as e:
        print(f"Error enviando email de reserva: {e}")
        return False

def enviar_email_reserva_cancelada(reserva):
    """Envía email de cancelación de reserva"""
    try:
        subject = f'❌ Reserva Cancelada - Restaurante GYZ #{str(reserva.codigo_reserva)[:8]}'
        
        context = {
            'reserva': reserva,
            'fecha_cancelacion': timezone.now().strftime('%d/%m/%Y %H:%M'),
        }
        
        html_message = render_to_string('emails/reserva_cancelada.html', context)
        
        plain_message = f"""
        Reserva Cancelada
        
        Hola {reserva.nombre_cliente},
        
        Tu reserva ha sido cancelada exitosamente.
        
        📅 Fecha de la reserva: {reserva.fecha_reserva.strftime('%d/%m/%Y')}
        🕐 Hora: {reserva.hora_reserva.strftime('%H:%M')}
        🔢 Código: {str(reserva.codigo_reserva)[:8]}
        ⏰ Cancelada el: {timezone.now().strftime('%d/%m/%Y %H:%M')}
        
        Si tienes alguna pregunta, no dudes en contactarnos.
        
        Saludos,
        Equipo Restaurante GYZ
        """
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[reserva.email_cliente],
            html_message=html_message,
            fail_silently=False,
        )
        
        return True
        
    except Exception as e:
        print(f"Error enviando email de cancelación: {e}")
        return False
