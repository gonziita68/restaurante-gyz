import re
import random
from datetime import datetime, timedelta
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone

class TarjetaCredito:
    """Clase para validar y procesar pagos con tarjeta de crédito"""
    
    @staticmethod
    def validar_numero_tarjeta(numero):
        """Valida número de tarjeta usando algoritmo de Luhn"""
        if not numero or len(numero) < 13 or len(numero) > 19:
            return False
        
        # Eliminar espacios y guiones
        numero = re.sub(r'[\s-]', '', numero)
        
        if not numero.isdigit():
            return False
        
        # Algoritmo de Luhn
        suma = 0
        alternar = False
        
        for digito in reversed(numero):
            digito = int(digito)
            if alternar:
                digito *= 2
                if digito > 9:
                    digito = (digito % 10) + 1
            suma += digito
            alternar = not alternar
        
        return suma % 10 == 0
    
    @staticmethod
    def validar_fecha_vencimiento(mes, año):
        """Valida fecha de vencimiento"""
        try:
            mes = int(mes)
            año = int(año)
            
            if mes < 1 or mes > 12:
                return False
            
            # Año actual
            año_actual = datetime.now().year
            
            # Si el año tiene 2 dígitos, convertirlo a 4
            if año < 100:
                año += 2000
            
            # Verificar que no esté vencida
            if año < año_actual:
                return False
            elif año == año_actual and mes < datetime.now().month:
                return False
            
            return True
            
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validar_cvv(cvv):
        """Valida código CVV"""
        if not cvv or len(cvv) < 3 or len(cvv) > 4:
            return False
        return cvv.isdigit()
    
    @staticmethod
    def identificar_tipo_tarjeta(numero):
        """Identifica el tipo de tarjeta basado en el número"""
        numero = re.sub(r'[\s-]', '', numero)
        
        # Visa: empieza con 4
        if numero.startswith('4'):
            return 'Visa'
        
        # Mastercard: empieza con 51-55 o 2221-2720
        elif re.match(r'^5[1-5]', numero) or re.match(r'^2[2-7][2-9][0-9]', numero):
            return 'Mastercard'
        
        # American Express: empieza con 34 o 37
        elif re.match(r'^3[47]', numero):
            return 'American Express'
        
        # Discover: empieza con 6011, 622126-622925, 644-649, 65
        elif (numero.startswith('6011') or 
              re.match(r'^622(12[6-9]|1[3-9][0-9]|[2-8][0-9][0-9]|9[0-1][0-9]|92[0-5])', numero) or
              re.match(r'^64[4-9]', numero) or
              numero.startswith('65')):
            return 'Discover'
        
        else:
            return 'Desconocida'

def procesar_pago_tarjeta(numero_tarjeta, fecha_vencimiento, cvv, monto, email_cliente, descripcion):
    """Procesa un pago con tarjeta de crédito (simulado)"""
    
    # Validaciones
    if not TarjetaCredito.validar_numero_tarjeta(numero_tarjeta):
        return {
            'exitoso': False,
            'mensaje': 'Número de tarjeta inválido',
            'codigo_error': 'TARJETA_INVALIDA'
        }
    
    # Extraer mes y año de la fecha de vencimiento
    try:
        mes, año = fecha_vencimiento.split('/')
        if not TarjetaCredito.validar_fecha_vencimiento(mes, año):
            return {
                'exitoso': False,
                'mensaje': 'Fecha de vencimiento inválida o tarjeta vencida',
                'codigo_error': 'FECHA_VENCIDA'
            }
    except:
        return {
            'exitoso': False,
            'mensaje': 'Formato de fecha inválido (MM/YY)',
            'codigo_error': 'FECHA_INVALIDA'
        }
    
    if not TarjetaCredito.validar_cvv(cvv):
        return {
            'exitoso': False,
            'mensaje': 'Código CVV inválido',
            'codigo_error': 'CVV_INVALIDO'
        }
    
    # Simular procesamiento del pago
    # En un entorno real, aquí se conectaría con un gateway de pago
    
    # Simular éxito (90% de probabilidad)
    if random.random() < 0.9:
        # Generar número de transacción
        numero_transaccion = f"TXN{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(1000, 9999)}"
        
        # Generar código de autorización
        codigo_autorizacion = f"{random.randint(100000, 999999)}"
        
        # Crear respuesta exitosa
        resultado = {
            'exitoso': True,
            'mensaje': 'Pago procesado exitosamente',
            'numero_transaccion': numero_transaccion,
            'codigo_autorizacion': codigo_autorizacion,
            'monto': monto,
            'fecha_procesamiento': timezone.now(),
            'tipo_tarjeta': TarjetaCredito.identificar_tipo_tarjeta(numero_tarjeta),
            'ultimos_digitos': numero_tarjeta[-4:],
            'email_cliente': email_cliente,
            'descripcion': descripcion
        }
        
        # Enviar email de confirmación de pago
        enviar_email_pago_exitoso(resultado)
        
        return resultado
    
    else:
        # Simular fallo
        return {
            'exitoso': False,
            'mensaje': 'Pago rechazado por el banco',
            'codigo_error': 'PAGO_RECHAZADO'
        }

def enviar_email_pago_exitoso(resultado_pago):
    """Envía email de confirmación de pago exitoso"""
    try:
        subject = f'💳 Pago Exitoso - Restaurante GYZ #{resultado_pago["numero_transaccion"]}'
        
        context = {
            'pago': resultado_pago,
            'fecha_procesamiento': resultado_pago['fecha_procesamiento'].strftime('%d/%m/%Y %H:%M:%S'),
        }
        
        html_message = render_to_string('emails/pago_exitoso.html', context)
        
        plain_message = f"""
        ¡Pago Procesado Exitosamente!
        
        Hola,
        
        Tu pago ha sido procesado exitosamente.
        
        💳 Tipo de tarjeta: {resultado_pago['tipo_tarjeta']}
        🔢 Últimos dígitos: **** **** **** {resultado_pago['ultimos_digitos']}
        💰 Monto: ${resultado_pago['monto']:.2f}
        📝 Descripción: {resultado_pago['descripcion']}
        🔢 Número de transacción: {resultado_pago['numero_transaccion']}
        ✅ Código de autorización: {resultado_pago['codigo_autorizacion']}
        📅 Fecha: {resultado_pago['fecha_procesamiento'].strftime('%d/%m/%Y %H:%M:%S')}
        
        Gracias por tu compra.
        
        Saludos,
        Equipo Restaurante GYZ
        """
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[resultado_pago['email_cliente']],
            html_message=html_message,
            fail_silently=False,
        )
        
        return True
        
    except Exception as e:
        print(f"Error enviando email de pago: {e}")
        return False
