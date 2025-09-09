from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db import transaction
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q, Count
from datetime import datetime, timedelta, date
import json

from .models import (
    ConfiguracionRestaurante, TipoMesa, Mesa, Reserva, 
    HistorialReserva, BloqueoMesa, EstadoReserva
)
from .utils import enviar_email_reserva_confirmada, enviar_email_reserva_cancelada

def disponibilidad_mesas(request):
    """Vista principal para ver disponibilidad y hacer reservas"""
    config = ConfiguracionRestaurante.objects.first()
    tipos_mesa = TipoMesa.objects.filter(activo=True).order_by('capacidad_minima')
    
    # Fecha por defecto (hoy o mañana si ya pasó la hora)
    fecha_default = timezone.now().date()
    if timezone.now().time() > (config.hora_cierre if config else timezone.now().time()):
        fecha_default = fecha_default + timedelta(days=1)
    
    context = {
        'config': config,
        'tipos_mesa': tipos_mesa,
        'fecha_default': fecha_default,
    }
    
    return render(request, 'reservas/disponibilidad.html', context)

def buscar_disponibilidad(request):
    """API para buscar mesas disponibles"""
    try:
        fecha_str = request.GET.get('fecha')
        hora_str = request.GET.get('hora')
        comensales = int(request.GET.get('comensales', 2))
        
        if not fecha_str or not hora_str:
            return JsonResponse({'error': 'Fecha y hora son requeridas'}, status=400)
        
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        hora = datetime.strptime(hora_str, '%H:%M').time()
        
        # Validaciones básicas
        config = ConfiguracionRestaurante.objects.first()
        if config:
            # Validar fecha
            fecha_limite_min = timezone.now() + timedelta(hours=config.tiempo_minimo_reserva_horas)
            fecha_limite_max = timezone.now() + timedelta(days=config.tiempo_maximo_reserva_dias)
            
            fecha_hora_solicitada = timezone.make_aware(datetime.combine(fecha, hora))
            
            if fecha_hora_solicitada < fecha_limite_min:
                return JsonResponse({
                    'error': f'La reserva debe ser con al menos {config.tiempo_minimo_reserva_horas} horas de anticipación'
                }, status=400)
            
            if fecha_hora_solicitada > fecha_limite_max:
                return JsonResponse({
                    'error': f'No se pueden hacer reservas con más de {config.tiempo_maximo_reserva_dias} días de anticipación'
                }, status=400)
            
            # Validar horarios
            if hora < config.hora_apertura or hora > config.hora_cierre:
                return JsonResponse({
                    'error': f'El horario debe estar entre {config.hora_apertura} y {config.hora_cierre}'
                }, status=400)
        
        # Buscar mesas disponibles
        mesas_disponibles = []
        
        # Obtener mesas que pueden acomodar a los comensales
        mesas_candidatas = Mesa.objects.filter(
            activa=True,
            tipo_mesa__capacidad_minima__lte=comensales,
            tipo_mesa__capacidad_maxima__gte=comensales
        ).select_related('tipo_mesa')
        
        for mesa in mesas_candidatas:
            # Verificar si la mesa está bloqueada
            fecha_hora = timezone.make_aware(datetime.combine(fecha, hora))
            bloqueos_activos = BloqueoMesa.objects.filter(
                mesa=mesa,
                activo=True,
                fecha_inicio__lte=fecha_hora,
                fecha_fin__gte=fecha_hora
            )
            
            if bloqueos_activos.exists():
                continue
            
            # Verificar reservas existentes
            duracion_estimada = config.duracion_turno_minutos if config else 120
            hora_fin = (datetime.combine(fecha, hora) + timedelta(minutes=duracion_estimada)).time()
            
            reservas_conflicto = Reserva.objects.filter(
                mesa=mesa,
                fecha_reserva=fecha,
                estado__in=[EstadoReserva.CONFIRMADA, EstadoReserva.EN_CURSO, EstadoReserva.PENDIENTE]
            ).filter(
                Q(hora_reserva__lt=hora_fin) & 
                Q(hora_reserva__gte=hora) |
                Q(hora_reserva__lte=hora) &
                Q(hora_reserva__gte=(datetime.combine(fecha, hora) - timedelta(minutes=duracion_estimada)).time())
            )
            
            if not reservas_conflicto.exists():
                mesas_disponibles.append({
                    'id': mesa.id,
                    'numero': mesa.numero,
                    'tipo': mesa.tipo_mesa.nombre,
                    'capacidad_min': mesa.tipo_mesa.capacidad_minima,
                    'capacidad_max': mesa.tipo_mesa.capacidad_maxima,
                    'ubicacion': mesa.get_ubicacion_display(),
                    'precio_base': str(mesa.tipo_mesa.precio_base),
                })
        
        return JsonResponse({
            'mesas_disponibles': mesas_disponibles,
            'fecha': fecha_str,
            'hora': hora_str,
            'comensales': comensales
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def crear_reserva(request):
    """Crear una nueva reserva"""
    if request.method == 'POST':
        try:
            with transaction.atomic():
                data = json.loads(request.body)
                
                mesa = get_object_or_404(Mesa, id=data['mesa_id'])
                fecha = datetime.strptime(data['fecha'], '%Y-%m-%d').date()
                hora = datetime.strptime(data['hora'], '%H:%M').time()
                
                # Verificar disponibilidad una vez más
                fecha_hora = timezone.make_aware(datetime.combine(fecha, hora))
                reservas_existentes = Reserva.objects.filter(
                    mesa=mesa,
                    fecha_reserva=fecha,
                    hora_reserva=hora,
                    estado__in=[EstadoReserva.CONFIRMADA, EstadoReserva.EN_CURSO, EstadoReserva.PENDIENTE]
                )
                
                if reservas_existentes.exists():
                    return JsonResponse({'error': 'La mesa ya no está disponible'}, status=400)
                
                # Crear la reserva
                reserva = Reserva.objects.create(
                    usuario=request.user,
                    mesa=mesa,
                    fecha_reserva=fecha,
                    hora_reserva=hora,
                    numero_comensales=data['comensales'],
                    nombre_cliente=data.get('nombre_cliente', ''),
                    telefono_cliente=data.get('telefono_cliente', ''),
                    email_cliente=data.get('email_cliente', request.user.email),
                    ocasion_especial=data.get('ocasion_especial', ''),
                    preferencia_ubicacion=data.get('preferencia_ubicacion', 'cualquiera'),
                    solicitudes_especiales=data.get('solicitudes_especiales', ''),
                )
                
                # Crear historial
                HistorialReserva.objects.create(
                    reserva=reserva,
                    estado_anterior='',
                    estado_nuevo=EstadoReserva.PENDIENTE,
                    usuario_responsable=request.user,
                    comentario='Reserva creada'
                )
                
                # Enviar email de confirmación
                try:
                    enviar_email_reserva_confirmada(reserva)
                except Exception as e:
                    print(f"Error enviando email de reserva: {e}")
                
                return JsonResponse({
                    'success': True,
                    'mensaje': 'Reserva creada exitosamente',
                    'codigo_reserva': str(reserva.codigo_reserva),
                    'reserva_id': reserva.id
                })
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)

@login_required
def mis_reservas(request):
    """Lista de reservas del usuario"""
    reservas_list = Reserva.objects.filter(
        usuario=request.user
    ).select_related('mesa', 'mesa__tipo_mesa').order_by('-fecha_reserva', '-hora_reserva')
    
    # Filtros
    estado_filtro = request.GET.get('estado')
    if estado_filtro:
        reservas_list = reservas_list.filter(estado=estado_filtro)
    
    # Paginación
    paginator = Paginator(reservas_list, 10)
    page_number = request.GET.get('page')
    reservas = paginator.get_page(page_number)
    
    context = {
        'reservas': reservas,
        'estados': EstadoReserva.choices,
        'estado_filtro': estado_filtro,
    }
    
    return render(request, 'reservas/mis_reservas.html', context)

@login_required
def detalle_reserva(request, reserva_id):
    """Detalle de una reserva específica"""
    reserva = get_object_or_404(
        Reserva.objects.select_related('mesa', 'usuario', 'usuario_confirmacion'),
        id=reserva_id,
        usuario=request.user
    )
    
    historial = reserva.historial.select_related('usuario_responsable').order_by('fecha_cambio')
    
    context = {
        'reserva': reserva,
        'historial': historial,
        'puede_cancelar': reserva.puede_cancelar,
    }
    
    return render(request, 'reservas/detalle_reserva.html', context)

@login_required
@require_POST
def cancelar_reserva(request, reserva_id):
    """Cancelar una reserva"""
    reserva = get_object_or_404(Reserva, id=reserva_id, usuario=request.user)
    
    if reserva.cancelar():
        # Crear historial
        HistorialReserva.objects.create(
            reserva=reserva,
            estado_anterior=EstadoReserva.CONFIRMADA,  # Estado anterior aproximado
            estado_nuevo=EstadoReserva.CANCELADA,
            usuario_responsable=request.user,
            comentario='Cancelada por el cliente'
        )
        
        # Enviar email de cancelación
        try:
            enviar_email_reserva_cancelada(reserva)
        except Exception as e:
            print(f"Error enviando email de cancelación: {e}")
        
        messages.success(request, 'Reserva cancelada exitosamente.')
    else:
        messages.error(request, 'No se puede cancelar esta reserva.')
    
    return redirect('reservas:detalle_reserva', reserva_id=reserva.id)

def consultar_reserva(request):
    """Consulta pública de reserva por código"""
    codigo = request.GET.get('codigo', '').strip()
    reserva = None
    
    if codigo:
        try:
            reserva = Reserva.objects.select_related('mesa', 'mesa__tipo_mesa').get(
                codigo_reserva=codigo
            )
        except Reserva.DoesNotExist:
            messages.error(request, 'Código de reserva no encontrado.')
    
    context = {
        'reserva': reserva,
        'codigo_busqueda': codigo,
    }
    
    return render(request, 'reservas/consultar_reserva.html', context)

def horarios_disponibles(request):
    """API para obtener horarios disponibles en una fecha específica"""
    try:
        fecha_str = request.GET.get('fecha')
        comensales = int(request.GET.get('comensales', 2))
        
        if not fecha_str:
            return JsonResponse({'error': 'Fecha requerida'}, status=400)
        
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        config = ConfiguracionRestaurante.objects.first()
        
        if not config:
            return JsonResponse({'error': 'Configuración del restaurante no encontrada'}, status=500)
        
        # Generar horarios posibles
        horarios = []
        hora_actual = config.hora_apertura
        hora_cierre = config.hora_cierre
        
        while hora_actual < hora_cierre:
            # Verificar si hay mesas disponibles en este horario
            mesas_disponibles = Mesa.objects.filter(
                activa=True,
                tipo_mesa__capacidad_minima__lte=comensales,
                tipo_mesa__capacidad_maxima__gte=comensales
            ).exclude(
                # Excluir mesas con reservas en conflicto
                reservas__fecha_reserva=fecha,
                reservas__hora_reserva=hora_actual,
                reservas__estado__in=[EstadoReserva.CONFIRMADA, EstadoReserva.EN_CURSO, EstadoReserva.PENDIENTE]
            ).exclude(
                # Excluir mesas bloqueadas
                bloqueos__activo=True,
                bloqueos__fecha_inicio__lte=timezone.make_aware(datetime.combine(fecha, hora_actual)),
                bloqueos__fecha_fin__gte=timezone.make_aware(datetime.combine(fecha, hora_actual))
            )
            
            if mesas_disponibles.exists():
                horarios.append({
                    'hora': hora_actual.strftime('%H:%M'),
                    'mesas_disponibles': mesas_disponibles.count()
                })
            
            # Incrementar por intervalos de 30 minutos
            hora_actual = (datetime.combine(fecha, hora_actual) + timedelta(minutes=30)).time()
        
        return JsonResponse({'horarios': horarios})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def calendario_reservas(request):
    """Vista de calendario con reservas (para staff)"""
    fecha_str = request.GET.get('fecha', timezone.now().date().isoformat())
    try:
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
    except ValueError:
        fecha = timezone.now().date()
    
    # Obtener reservas del día
    reservas = Reserva.objects.filter(
        fecha_reserva=fecha
    ).select_related('mesa', 'usuario').order_by('hora_reserva')
    
    # Obtener configuración
    config = ConfiguracionRestaurante.objects.first()
    
    # Organizar reservas por horario
    reservas_por_hora = {}
    for reserva in reservas:
        hora_key = reserva.hora_reserva.strftime('%H:%M')
        if hora_key not in reservas_por_hora:
            reservas_por_hora[hora_key] = []
        reservas_por_hora[hora_key].append(reserva)
    
    context = {
        'fecha': fecha,
        'reservas': reservas,
        'reservas_por_hora': reservas_por_hora,
        'config': config,
        'fecha_anterior': fecha - timedelta(days=1),
        'fecha_siguiente': fecha + timedelta(days=1),
    }
    
    return render(request, 'reservas/calendario.html', context)
