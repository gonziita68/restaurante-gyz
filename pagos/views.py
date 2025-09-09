from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.utils import timezone
from django.conf import settings
from decimal import Decimal
import json
import stripe

from .models import ConfiguracionPagos, Pago, LogPago, EstadoPago, MetodoPago, TipoPago
from pedidos.models import Pedido
from reservas.models import Reserva
from .forms import PagoTarjetaForm
from .utils import procesar_pago_tarjeta

def obtener_configuracion():
    """Obtiene la configuración de pagos"""
    return ConfiguracionPagos.objects.first()

@login_required
def procesar_pago(request, pedido_id=None, reserva_id=None):
    """Vista principal para procesar pagos"""
    config = obtener_configuracion()
    
    # Determinar el objeto a pagar
    objeto_pago = None
    tipo_pago = TipoPago.PEDIDO
    
    if pedido_id:
        objeto_pago = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
        tipo_pago = TipoPago.PEDIDO
    elif reserva_id:
        objeto_pago = get_object_or_404(Reserva, id=reserva_id, usuario=request.user)
        tipo_pago = TipoPago.RESERVA
    else:
        messages.error(request, 'No se especificó qué pagar.')
        return redirect('usuarios:index')
    
    # Verificar si ya hay un pago completado
    pagos_existentes = Pago.objects.filter(
        **{tipo_pago.lower(): objeto_pago},
        estado=EstadoPago.COMPLETADO
    )
    
    if pagos_existentes.exists():
        messages.info(request, 'Este objeto ya tiene un pago completado.')
        return redirect('usuarios:index')
    
    # Calcular montos
    if tipo_pago == TipoPago.PEDIDO:
        subtotal = objeto_pago.subtotal
        impuestos = objeto_pago.impuestos
        total = objeto_pago.total
    else:  # Reserva
        subtotal = objeto_pago.mesa.tipo_mesa.precio_base
        impuestos = subtotal * Decimal('0.16') if config and config.incluir_iva else Decimal('0')
        total = subtotal + impuestos
    
    # Métodos de pago disponibles
    metodos_disponibles = []
    
    # Efectivo siempre disponible
    if total <= (config.pago_maximo_efectivo if config else Decimal('1000')):
        metodos_disponibles.append({
            'codigo': MetodoPago.EFECTIVO,
            'nombre': 'Efectivo',
            'descripcion': 'Pago en efectivo al recibir',
            'icon': 'fas fa-money-bill-wave',
            'comision': 0
        })
    
    # Stripe
    if config and config.stripe_activo:
        metodos_disponibles.append({
            'codigo': MetodoPago.STRIPE,
            'nombre': 'Tarjeta de Crédito/Débito',
            'descripcion': 'Pago seguro con tarjeta',
            'icon': 'fas fa-credit-card',
            'comision': total * (config.comision_tarjeta / 100)
        })
    
    # PayPal
    if config and config.paypal_activo:
        metodos_disponibles.append({
            'codigo': MetodoPago.PAYPAL,
            'nombre': 'PayPal',
            'descripcion': 'Pago con PayPal',
            'icon': 'fab fa-paypal',
            'comision': total * (config.comision_paypal / 100)
        })
    
    context = {
        'objeto_pago': objeto_pago,
        'tipo_pago': tipo_pago,
        'subtotal': subtotal,
        'impuestos': impuestos,
        'total': total,
        'metodos_disponibles': metodos_disponibles,
        'config': config,
        'stripe_public_key': config.stripe_public_key if config else '',
    }
    
    return render(request, 'pagos/procesar_pago.html', context)

@login_required
@require_POST
def crear_pago(request):
    """Crea un nuevo pago"""
    try:
        data = json.loads(request.body)
        
        tipo_pago = data.get('tipo_pago')
        objeto_id = data.get('objeto_id')
        metodo_pago = data.get('metodo_pago')
        
        # Obtener objeto a pagar
        objeto_pago = None
        if tipo_pago == TipoPago.PEDIDO:
            objeto_pago = get_object_or_404(Pedido, id=objeto_id, usuario=request.user)
        elif tipo_pago == TipoPago.RESERVA:
            objeto_pago = get_object_or_404(Reserva, id=objeto_id, usuario=request.user)
        
        # Calcular montos
        config = obtener_configuracion()
        
        if tipo_pago == TipoPago.PEDIDO:
            subtotal = objeto_pago.subtotal
            impuestos = objeto_pago.impuestos
            total = objeto_pago.total
        else:
            subtotal = objeto_pago.mesa.tipo_mesa.precio_base
            impuestos = subtotal * Decimal('0.16') if config and config.incluir_iva else Decimal('0')
            total = subtotal + impuestos
        
        # Calcular comisión
        comision = Decimal('0')
        if metodo_pago == MetodoPago.TARJETA and config:
            comision = total * (config.comision_tarjeta / 100)
        elif metodo_pago == MetodoPago.PAYPAL and config:
            comision = total * (config.comision_paypal / 100)
        
        # Crear el pago
        kwargs_pago = {
            'usuario': request.user,
            'tipo_pago': tipo_pago,
            'metodo_pago': metodo_pago,
            'subtotal': subtotal,
            'impuestos': impuestos,
            'comision': comision,
            'total': total + comision,
            'ip_cliente': get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
        }
        
        # Agregar la referencia específica
        if tipo_pago == TipoPago.PEDIDO:
            kwargs_pago['pedido'] = objeto_pago
        else:
            kwargs_pago['reserva'] = objeto_pago
        
        # Datos de facturación si se requiere
        if data.get('requiere_factura'):
            kwargs_pago['requiere_factura'] = True
            kwargs_pago['datos_facturacion'] = data.get('datos_facturacion', {})
        
        pago = Pago.objects.create(**kwargs_pago)
        
        # Log del evento
        LogPago.objects.create(
            pago=pago,
            evento='pago_creado',
            descripcion=f'Pago creado para {tipo_pago}',
            ip_origen=get_client_ip(request)
        )
        
        # Procesar según el método de pago
        if metodo_pago == MetodoPago.EFECTIVO:
            # Para efectivo, solo crear el pago pendiente
            return JsonResponse({
                'success': True,
                'pago_id': pago.id,
                'numero_pago': str(pago.numero_pago),
                'metodo': 'efectivo'
            })
        
        elif metodo_pago == MetodoPago.STRIPE:
            return procesar_pago_stripe(request, pago)
        
        elif metodo_pago == MetodoPago.PAYPAL:
            return procesar_pago_paypal(request, pago)
        
        else:
            return JsonResponse({'error': 'Método de pago no soportado'}, status=400)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def procesar_pago_stripe(request, pago):
    """Procesa pago con Stripe"""
    try:
        config = obtener_configuracion()
        stripe.api_key = config.stripe_secret_key
        
        # Crear Payment Intent
        intent = stripe.PaymentIntent.create(
            amount=int(pago.total * 100),  # Stripe usa centavos
            currency='usd',
            metadata={
                'pago_id': pago.id,
                'numero_pago': str(pago.numero_pago),
                'usuario_id': pago.usuario.id,
            }
        )
        
        # Guardar el payment intent ID
        pago.payment_intent_id = intent.id
        pago.save()
        
        # Log del evento
        LogPago.objects.create(
            pago=pago,
            evento='stripe_intent_created',
            descripcion=f'Payment Intent creado: {intent.id}',
            datos_adicionales={'intent_id': intent.id}
        )
        
        return JsonResponse({
            'success': True,
            'pago_id': pago.id,
            'client_secret': intent.client_secret,
            'metodo': 'stripe'
        })
        
    except Exception as e:
        pago.marcar_fallido(f'Error en Stripe: {str(e)}')
        return JsonResponse({'error': f'Error procesando pago: {str(e)}'}, status=500)

def procesar_pago_paypal(request, pago):
    """Procesa pago con PayPal"""
    # Aquí implementarías la lógica de PayPal
    # Por ahora retornamos un placeholder
    return JsonResponse({
        'success': True,
        'pago_id': pago.id,
        'metodo': 'paypal',
        'redirect_url': f'/pagos/paypal/{pago.id}/'
    })

@csrf_exempt
def webhook_stripe(request):
    """Webhook para eventos de Stripe"""
    config = obtener_configuracion()
    if not config or not config.stripe_webhook_secret:
        return JsonResponse({'error': 'Webhook no configurado'}, status=400)
    
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, config.stripe_webhook_secret
        )
    except ValueError:
        return JsonResponse({'error': 'Invalid payload'}, status=400)
    except stripe.error.SignatureVerificationError:
        return JsonResponse({'error': 'Invalid signature'}, status=400)
    
    # Manejar el evento
    if event['type'] == 'payment_intent.succeeded':
        intent = event['data']['object']
        
        try:
            pago = Pago.objects.get(payment_intent_id=intent['id'])
            pago.marcar_completado(intent['id'])
            
            LogPago.objects.create(
                pago=pago,
                evento='stripe_payment_succeeded',
                descripcion='Pago completado exitosamente en Stripe',
                datos_adicionales=intent
            )
            
        except Pago.DoesNotExist:
            pass
    
    elif event['type'] == 'payment_intent.payment_failed':
        intent = event['data']['object']
        
        try:
            pago = Pago.objects.get(payment_intent_id=intent['id'])
            pago.marcar_fallido('Pago fallido en Stripe')
            
            LogPago.objects.create(
                pago=pago,
                evento='stripe_payment_failed',
                descripcion='Pago fallido en Stripe',
                datos_adicionales=intent
            )
            
        except Pago.DoesNotExist:
            pass
    
    return JsonResponse({'status': 'success'})

@login_required
def confirmar_pago_efectivo(request, pago_id):
    """Confirma un pago en efectivo (para staff)"""
    pago = get_object_or_404(Pago, id=pago_id, metodo_pago=MetodoPago.EFECTIVO)
    
    if request.method == 'POST':
        if request.user.is_staff:
            pago.marcar_completado()
            
            LogPago.objects.create(
                pago=pago,
                evento='efectivo_confirmado',
                descripcion=f'Pago en efectivo confirmado por {request.user.username}',
                ip_origen=get_client_ip(request)
            )
            
            messages.success(request, 'Pago en efectivo confirmado.')
        else:
            messages.error(request, 'No tienes permisos para confirmar pagos.')
    
    return redirect('admin:pagos_pago_change', pago.id)

@login_required
def historial_pagos(request):
    """Historial de pagos del usuario"""
    pagos = Pago.objects.filter(usuario=request.user).order_by('-fecha_creacion')
    
    context = {
        'pagos': pagos,
    }
    
    return render(request, 'pagos/historial_pagos.html', context)

def estado_pago(request, numero_pago):
    """Consulta pública del estado de un pago"""
    try:
        pago = Pago.objects.get(numero_pago=numero_pago)
        
        return JsonResponse({
            'numero_pago': str(pago.numero_pago)[:8],
            'estado': pago.estado,
            'estado_display': pago.get_estado_display(),
            'total': str(pago.total),
            'metodo_pago': pago.get_metodo_pago_display(),
            'fecha_creacion': pago.fecha_creacion.isoformat(),
        })
        
    except Pago.DoesNotExist:
        return JsonResponse({'error': 'Pago no encontrado'}, status=404)

def get_client_ip(request):
    """Obtiene la IP del cliente"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@login_required
def pago_tarjeta(request):
    """Vista para procesar pago con tarjeta de crédito"""
    
    if request.method == 'POST':
        form = PagoTarjetaForm(request.POST)
        
        if form.is_valid():
            # Obtener datos del formulario
            numero_tarjeta = form.cleaned_data['numero_tarjeta']
            fecha_vencimiento = form.cleaned_data['fecha_vencimiento']
            cvv = form.cleaned_data['cvv']
            monto = form.cleaned_data['monto']
            email = form.cleaned_data['email']
            descripcion = form.cleaned_data['descripcion']
            
            # Procesar el pago
            resultado = procesar_pago_tarjeta(
                numero_tarjeta=numero_tarjeta,
                fecha_vencimiento=fecha_vencimiento,
                cvv=cvv,
                monto=monto,
                email_cliente=email,
                descripcion=descripcion
            )
            
            if resultado['exitoso']:
                messages.success(request, f"¡Pago exitoso! Número de transacción: {resultado['numero_transaccion']}")
                return redirect('pagos:confirmacion_pago', transaccion_id=resultado['numero_transaccion'])
            else:
                messages.error(request, f"Error en el pago: {resultado['mensaje']}")
                return render(request, 'pagos/pago_tarjeta.html', {'form': form, 'monto': monto})
    else:
        # Obtener monto desde GET o session
        monto = request.GET.get('monto') or request.session.get('monto_pago', 0)
        descripcion = request.GET.get('descripcion', 'Pago Restaurante GYZ')
        
        # Pre-llenar el formulario
        initial_data = {
            'monto': monto,
            'descripcion': descripcion,
            'email': request.user.email if request.user.is_authenticated else ''
        }
        
        form = PagoTarjetaForm(initial=initial_data)
    
    context = {
        'form': form,
        'monto': monto,
        'descripcion': descripcion
    }
    
    return render(request, 'pagos/pago_tarjeta.html', context)

@login_required
def confirmacion_pago(request, transaccion_id):
    """Vista de confirmación de pago exitoso"""
    context = {
        'transaccion_id': transaccion_id,
        'fecha': request.session.get('fecha_pago'),
        'monto': request.session.get('monto_pago')
    }
    
    return render(request, 'pagos/confirmacion_pago.html', context)

@csrf_exempt
@require_POST
def procesar_pago_ajax(request):
    """API para procesar pagos vía AJAX"""
    try:
        data = json.loads(request.body)
        
        # Validar datos requeridos
        required_fields = ['numero_tarjeta', 'fecha_vencimiento', 'cvv', 'monto', 'email']
        for field in required_fields:
            if field not in data:
                return JsonResponse({
                    'exitoso': False,
                    'mensaje': f'Campo requerido faltante: {field}'
                }, status=400)
        
        # Procesar el pago
        resultado = procesar_pago_tarjeta(
            numero_tarjeta=data['numero_tarjeta'],
            fecha_vencimiento=data['fecha_vencimiento'],
            cvv=data['cvv'],
            monto=float(data['monto']),
            email_cliente=data['email'],
            descripcion=data.get('descripcion', 'Pago Restaurante GYZ')
        )
        
        return JsonResponse(resultado)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'exitoso': False,
            'mensaje': 'Datos JSON inválidos'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'exitoso': False,
            'mensaje': f'Error interno: {str(e)}'
        }, status=500)
