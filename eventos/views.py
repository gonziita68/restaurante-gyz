from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count
from django.utils import timezone
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime, timedelta
from decimal import Decimal
import json

from .models import (
    Evento, TipoEvento, MenuEvento, ServicioAdicional, 
    Catering, CotizacionEvento, PresupuestoEvento
)
from .forms import (
    SolicitudEventoForm, SeleccionTipoEventoForm, SeleccionMenuForm,
    ServiciosAdicionalesForm, CateringForm, CotizacionForm,
    BusquedaEventosForm, FiltroEventosForm, ActualizarEstadoEventoForm,
    PresupuestoEventoForm
)

@login_required
def solicitar_evento(request):
    """Vista para solicitar un nuevo evento"""
    if request.method == 'POST':
        form = SolicitudEventoForm(request.POST)
        if form.is_valid():
            evento = form.save(commit=False)
            evento.cliente = request.user
            evento.save()
            
            messages.success(request, 'Solicitud de evento enviada correctamente. Te contactaremos pronto.')
            return redirect('eventos:mis_eventos')
    else:
        form = SolicitudEventoForm()
    
    return render(request, 'eventos/solicitar_evento.html', {
        'form': form,
        'tipos_evento': TipoEvento.objects.filter(activo=True)
    })

@login_required
def solicitar_evento_paso2(request, evento_id):
    """Segundo paso: seleccionar tipo de evento"""
    evento = get_object_or_404(Evento, id=evento_id, cliente=request.user)
    
    if request.method == 'POST':
        form = SeleccionTipoEventoForm(request.POST)
        if form.is_valid():
            evento.tipo_evento = form.cleaned_data['tipo_evento']
            evento.save()
            return redirect('eventos:solicitar_evento_paso3', evento_id=evento.id)
    else:
        form = SeleccionTipoEventoForm()
    
    return render(request, 'eventos/solicitar_evento_paso2.html', {
        'form': form,
        'evento': evento
    })

@login_required
def solicitar_evento_paso3(request, evento_id):
    """Tercer paso: seleccionar menú"""
    evento = get_object_or_404(Evento, id=evento_id, cliente=request.user)
    
    if request.method == 'POST':
        form = SeleccionMenuForm(request.POST)
        if form.is_valid():
            evento.menu_evento = form.cleaned_data['menu_evento']
            evento.save()
            return redirect('eventos:solicitar_evento_paso4', evento_id=evento.id)
    else:
        form = SeleccionMenuForm()
    
    return render(request, 'eventos/solicitar_evento_paso3.html', {
        'form': form,
        'evento': evento,
        'menus': MenuEvento.objects.filter(activo=True)
    })

@login_required
def solicitar_evento_paso4(request, evento_id):
    """Cuarto paso: servicios adicionales"""
    evento = get_object_or_404(Evento, id=evento_id, cliente=request.user)
    
    if request.method == 'POST':
        form = ServiciosAdicionalesForm(request.POST)
        if form.is_valid():
            evento.servicios_adicionales.set(form.cleaned_data['servicios'])
            evento.decoracion_especial = form.cleaned_data['decoracion_especial']
            evento.musica_especial = form.cleaned_data['musica_especial']
            evento.fotografo = form.cleaned_data['fotografo']
            evento.save()
            
            messages.success(request, 'Evento solicitado correctamente. Te enviaremos una cotización pronto.')
            return redirect('eventos:mis_eventos')
    else:
        form = ServiciosAdicionalesForm()
    
    return render(request, 'eventos/solicitar_evento_paso4.html', {
        'form': form,
        'evento': evento,
        'servicios': ServicioAdicional.objects.filter(activo=True)
    })

@login_required
def mis_eventos(request):
    """Vista para ver los eventos del usuario"""
    eventos = Evento.objects.filter(cliente=request.user).order_by('-fecha_evento')
    
    # Filtros
    form = BusquedaEventosForm(request.GET)
    if form.is_valid():
        if form.cleaned_data.get('fecha_desde'):
            eventos = eventos.filter(fecha_evento__gte=form.cleaned_data['fecha_desde'])
        if form.cleaned_data.get('fecha_hasta'):
            eventos = eventos.filter(fecha_evento__lte=form.cleaned_data['fecha_hasta'])
        if form.cleaned_data.get('estado'):
            eventos = eventos.filter(estado=form.cleaned_data['estado'])
        if form.cleaned_data.get('categoria'):
            eventos = eventos.filter(categoria=form.cleaned_data['categoria'])
    
    # Paginación
    paginator = Paginator(eventos, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'eventos/mis_eventos.html', {
        'page_obj': page_obj,
        'form': form
    })

@login_required
def detalle_evento(request, evento_id):
    """Vista para ver el detalle de un evento"""
    evento = get_object_or_404(Evento, id=evento_id, cliente=request.user)
    
    return render(request, 'eventos/detalle_evento.html', {
        'evento': evento
    })

@login_required
def cancelar_evento(request, evento_id):
    """Vista para cancelar un evento"""
    evento = get_object_or_404(Evento, id=evento_id, cliente=request.user)
    
    if request.method == 'POST':
        evento.estado = 'cancelado'
        evento.save()
        
        # Enviar email de cancelación
        try:
            enviar_email_evento_cancelado(evento)
        except Exception as e:
            print(f"Error enviando email de cancelación: {e}")
        
        messages.success(request, 'Evento cancelado correctamente.')
        return redirect('eventos:mis_eventos')
    
    return render(request, 'eventos/cancelar_evento.html', {
        'evento': evento
    })

# Vistas para el personal del restaurante
@login_required
def dashboard_eventos(request):
    """Dashboard para gestionar eventos"""
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('eventos:mis_eventos')
    
    # Estadísticas
    eventos_hoy = Evento.objects.filter(fecha_evento=timezone.now().date())
    eventos_semana = Evento.objects.filter(
        fecha_evento__gte=timezone.now().date(),
        fecha_evento__lte=timezone.now().date() + timedelta(days=7)
    )
    eventos_pendientes = Evento.objects.filter(estado='solicitado').count()
    eventos_confirmados = Evento.objects.filter(estado='confirmado').count()
    
    # Filtros
    form = FiltroEventosForm(request.GET)
    eventos = Evento.objects.all().order_by('-fecha_evento')
    
    if form.is_valid():
        if form.cleaned_data.get('estado'):
            eventos = eventos.filter(estado=form.cleaned_data['estado'])
        if form.cleaned_data.get('categoria'):
            eventos = eventos.filter(categoria=form.cleaned_data['categoria'])
        if form.cleaned_data.get('fecha'):
            eventos = eventos.filter(fecha_evento=form.cleaned_data['fecha'])
    
    # Paginación
    paginator = Paginator(eventos, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'eventos/dashboard_eventos.html', {
        'page_obj': page_obj,
        'form': form,
        'eventos_hoy': eventos_hoy,
        'eventos_semana': eventos_semana,
        'eventos_pendientes': eventos_pendientes,
        'eventos_confirmados': eventos_confirmados
    })

@login_required
def gestionar_evento(request, evento_id):
    """Vista para gestionar un evento específico"""
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('eventos:mis_eventos')
    
    evento = get_object_or_404(Evento, id=evento_id)
    
    if request.method == 'POST':
        form = ActualizarEstadoEventoForm(request.POST)
        if form.is_valid():
            estado_anterior = evento.estado
            evento.estado = form.cleaned_data['estado']
            evento.save()
            
            # Enviar email de actualización
            if estado_anterior != evento.estado:
                try:
                    enviar_email_estado_evento(evento, estado_anterior)
                except Exception as e:
                    print(f"Error enviando email de actualización: {e}")
            
            messages.success(request, f'Estado del evento actualizado a: {evento.get_estado_display()}')
            return redirect('eventos:gestionar_evento', evento_id=evento.id)
    else:
        form = ActualizarEstadoEventoForm(initial={'estado': evento.estado})
    
    return render(request, 'eventos/gestionar_evento.html', {
        'evento': evento,
        'form': form
    })

@login_required
def crear_cotizacion(request, evento_id):
    """Vista para crear una cotización"""
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('eventos:mis_eventos')
    
    evento = get_object_or_404(Evento, id=evento_id)
    
    if request.method == 'POST':
        form = CotizacionForm(request.POST)
        if form.is_valid():
            cotizacion = form.save(commit=False)
            cotizacion.evento = evento
            cotizacion.fecha_expiracion = timezone.now() + timedelta(days=7)
            cotizacion.save()
            
            # Enviar email con cotización
            try:
                enviar_email_cotizacion(cotizacion)
            except Exception as e:
                print(f"Error enviando email de cotización: {e}")
            
            messages.success(request, 'Cotización creada y enviada al cliente.')
            return redirect('eventos:gestionar_evento', evento_id=evento.id)
    else:
        # Calcular total automáticamente
        total = evento.calcular_total()
        form = CotizacionForm(initial={
            'subtotal': total,
            'total': total
        })
    
    return render(request, 'eventos/crear_cotizacion.html', {
        'form': form,
        'evento': evento
    })

@login_required
def crear_presupuesto(request, evento_id):
    """Vista para crear un presupuesto detallado"""
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('eventos:mis_eventos')
    
    evento = get_object_or_404(Evento, id=evento_id)
    
    if request.method == 'POST':
        form = PresupuestoEventoForm(request.POST)
        if form.is_valid():
            # Obtener la última versión del presupuesto
            ultima_version = PresupuestoEvento.objects.filter(evento=evento).count()
            
            presupuesto = PresupuestoEvento(
                evento=evento,
                version=ultima_version + 1,
                costo_menu=form.cleaned_data['costo_menu'],
                costo_servicios=form.cleaned_data['costo_servicios'],
                costo_decoracion=form.cleaned_data['costo_decoracion'],
                costo_personal=form.cleaned_data['costo_personal'],
                costo_equipamiento=form.cleaned_data['costo_equipamiento'],
                costo_transporte=form.cleaned_data['costo_transporte'],
                descuento=form.cleaned_data.get('descuento', 0),
                notas=form.cleaned_data.get('notas', '')
            )
            
            # Calcular totales
            presupuesto.subtotal = (
                presupuesto.costo_menu + presupuesto.costo_servicios + 
                presupuesto.costo_decoracion + presupuesto.costo_personal + 
                presupuesto.costo_equipamiento + presupuesto.costo_transporte
            )
            presupuesto.impuestos = presupuesto.subtotal * Decimal('0.21')  # 21% IVA
            presupuesto.total = presupuesto.subtotal + presupuesto.impuestos - presupuesto.descuento
            
            presupuesto.save()
            
            messages.success(request, f'Presupuesto v{presupuesto.version} creado correctamente.')
            return redirect('eventos:gestionar_evento', evento_id=evento.id)
    else:
        form = PresupuestoEventoForm()
    
    return render(request, 'eventos/crear_presupuesto.html', {
        'form': form,
        'evento': evento
    })

# Vistas para catering
@login_required
def solicitar_catering(request):
    """Vista para solicitar servicios de catering"""
    if request.method == 'POST':
        form = CateringForm(request.POST)
        if form.is_valid():
            # Primero crear el evento base
            evento = Evento.objects.create(
                cliente=request.user,
                categoria='catering',
                nombre_evento=request.POST.get('nombre_evento', 'Servicio de Catering'),
                descripcion=request.POST.get('descripcion', ''),
                fecha_evento=request.POST.get('fecha_evento'),
                hora_inicio=request.POST.get('hora_inicio'),
                hora_fin=request.POST.get('hora_fin'),
                numero_invitados=request.POST.get('numero_invitados', 1),
                tipo_ubicacion='domicilio'
            )
            
            # Luego crear el catering
            catering = form.save(commit=False)
            catering.evento = evento
            catering.save()
            
            messages.success(request, 'Solicitud de catering enviada correctamente.')
            return redirect('eventos:mis_eventos')
    else:
        form = CateringForm()
    
    return render(request, 'eventos/solicitar_catering.html', {
        'form': form
    })

# Funciones auxiliares para emails
def enviar_email_evento_cancelado(evento):
    """Envía email de confirmación de cancelación"""
    subject = f'Evento Cancelado: {evento.nombre_evento}'
    html_message = render_to_string('eventos/emails/evento_cancelado.html', {
        'evento': evento
    })
    
    send_mail(
        subject=subject,
        message='',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[evento.cliente.email],
        html_message=html_message
    )

def enviar_email_estado_evento(evento, estado_anterior):
    """Envía email de actualización de estado"""
    subject = f'Actualización de Evento: {evento.nombre_evento}'
    html_message = render_to_string('eventos/emails/estado_actualizado.html', {
        'evento': evento,
        'estado_anterior': estado_anterior
    })
    
    send_mail(
        subject=subject,
        message='',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[evento.cliente.email],
        html_message=html_message
    )

def enviar_email_cotizacion(cotizacion):
    """Envía email con cotización"""
    subject = f'Cotización para: {cotizacion.evento.nombre_evento}'
    html_message = render_to_string('eventos/emails/cotizacion.html', {
        'cotizacion': cotizacion
    })
    
    send_mail(
        subject=subject,
        message='',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[cotizacion.evento.cliente.email],
        html_message=html_message
    )

# Vistas AJAX
@login_required
def calcular_precio_evento(request):
    """Calcula el precio de un evento en tiempo real"""
    if request.method == 'POST':
        data = json.loads(request.body)
        
        try:
            tipo_evento_id = data.get('tipo_evento_id')
            menu_evento_id = data.get('menu_evento_id')
            numero_invitados = int(data.get('numero_invitados', 1))
            servicios_ids = data.get('servicios_ids', [])
            
            total = Decimal('0')
            
            # Precio base del tipo de evento
            if tipo_evento_id:
                tipo_evento = TipoEvento.objects.get(id=tipo_evento_id)
                total += tipo_evento.precio_base
            
            # Precio del menú por persona
            if menu_evento_id:
                menu_evento = MenuEvento.objects.get(id=menu_evento_id)
                total += menu_evento.precio_por_persona * numero_invitados
            
            # Servicios adicionales
            for servicio_id in servicios_ids:
                servicio = ServicioAdicional.objects.get(id=servicio_id)
                if servicio.precio_por_persona:
                    total += servicio.precio * numero_invitados
                else:
                    total += servicio.precio
            
            return JsonResponse({
                'success': True,
                'total': float(total),
                'total_formatted': f'${total:,.2f}'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})
