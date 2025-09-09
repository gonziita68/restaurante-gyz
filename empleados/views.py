from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Avg, Count, Sum, Q
from django.utils import timezone
from django.core.paginator import Paginator
from datetime import datetime, timedelta
import json

from .models import (
    Empleado, Departamento, Puesto, RegistroAsistencia, Evaluacion,
    Capacitacion, ParticipacionCapacitacion, Nomina, Horario,
    EstadoEmpleado, TipoEmpleado
)

def es_gerente(user):
    """Verifica si el usuario es gerente o administrador"""
    return user.is_staff or (
        hasattr(user, 'empleado') and 
        user.empleado.puesto.tipo_empleado in ['gerente', 'subgerente']
    )

@login_required
@user_passes_test(es_gerente)
def dashboard_empleados(request):
    """Dashboard principal de gestión de empleados"""
    
    # Estadísticas generales
    total_empleados = Empleado.objects.filter(activo=True).count()
    empleados_activos = Empleado.objects.filter(estado=EstadoEmpleado.ACTIVO).count()
    empleados_nuevos_mes = Empleado.objects.filter(
        fecha_ingreso__gte=timezone.now().replace(day=1)
    ).count()
    
    # Costo total de nómina
    costo_nomina_total = Empleado.objects.filter(
        estado=EstadoEmpleado.ACTIVO
    ).aggregate(
        total=Sum('salario_base')
    )['total'] or 0
    
    # Empleados por departamento
    empleados_por_depto = Departamento.objects.filter(
        activo=True
    ).annotate(
        cantidad_empleados=Count(
            'empleados', 
            filter=Q(empleados__estado=EstadoEmpleado.ACTIVO)
        )
    ).order_by('-cantidad_empleados')
    
    # Evaluaciones pendientes
    evaluaciones_pendientes = Empleado.objects.filter(
        estado=EstadoEmpleado.ACTIVO
    ).filter(
        Q(fecha_proxima_evaluacion__isnull=True) |
        Q(fecha_proxima_evaluacion__lte=timezone.now().date()) |
        Q(evaluacion_actual__lte=5)
    ).count()
    
    # Cumpleaños del mes
    mes_actual = timezone.now().month
    cumpleanos_mes = Empleado.objects.filter(
        estado=EstadoEmpleado.ACTIVO,
        fecha_nacimiento__month=mes_actual
    ).select_related('usuario')[:5]
    
    # Asistencia de hoy
    hoy = timezone.now().date()
    asistencia_hoy = RegistroAsistencia.objects.filter(fecha=hoy).aggregate(
        presentes=Count('id', filter=Q(presente=True)),
        ausentes=Count('id', filter=Q(presente=False)),
        tardanzas=Count('id', filter=Q(tardanza=True))
    )
    
    # Empleados destacados (mejor evaluación)
    empleados_destacados = Empleado.objects.filter(
        estado=EstadoEmpleado.ACTIVO,
        evaluacion_actual__gt=0
    ).order_by('-evaluacion_actual')[:5]
    
    context = {
        'total_empleados': total_empleados,
        'empleados_activos': empleados_activos,
        'empleados_nuevos_mes': empleados_nuevos_mes,
        'costo_nomina_total': costo_nomina_total,
        'empleados_por_depto': empleados_por_depto,
        'evaluaciones_pendientes': evaluaciones_pendientes,
        'cumpleanos_mes': cumpleanos_mes,
        'asistencia_hoy': asistencia_hoy,
        'empleados_destacados': empleados_destacados,
    }
    
    return render(request, 'empleados/dashboard.html', context)

@login_required
@user_passes_test(es_gerente)
def lista_empleados(request):
    """Lista de empleados con filtros"""
    
    empleados = Empleado.objects.select_related(
        'usuario', 'puesto', 'departamento'
    ).filter(activo=True)
    
    # Filtros
    departamento = request.GET.get('departamento')
    estado = request.GET.get('estado')
    puesto = request.GET.get('puesto')
    buscar = request.GET.get('buscar')
    
    if departamento:
        empleados = empleados.filter(departamento_id=departamento)
    
    if estado:
        empleados = empleados.filter(estado=estado)
    
    if puesto:
        empleados = empleados.filter(puesto_id=puesto)
    
    if buscar:
        empleados = empleados.filter(
            Q(usuario__first_name__icontains=buscar) |
            Q(usuario__last_name__icontains=buscar) |
            Q(numero_empleado__icontains=buscar) |
            Q(cedula__icontains=buscar)
        )
    
    # Paginación
    paginator = Paginator(empleados, 20)
    page = request.GET.get('page')
    empleados = paginator.get_page(page)
    
    # Datos para filtros
    departamentos = Departamento.objects.filter(activo=True)
    puestos = Puesto.objects.filter(activo=True)
    
    context = {
        'empleados': empleados,
        'departamentos': departamentos,
        'puestos': puestos,
        'estados': EstadoEmpleado.choices,
        'departamento_actual': departamento,
        'estado_actual': estado,
        'puesto_actual': puesto,
        'buscar_actual': buscar,
    }
    
    return render(request, 'empleados/lista_empleados.html', context)

@login_required
@user_passes_test(es_gerente)
def detalle_empleado(request, empleado_id):
    """Detalle de un empleado específico"""
    
    empleado = get_object_or_404(
        Empleado.objects.select_related(
            'usuario', 'puesto', 'departamento'
        ),
        id=empleado_id
    )
    
    # Horarios del empleado
    horarios = empleado.horarios.filter(activo=True).order_by('dia_semana')
    
    # Últimas evaluaciones
    evaluaciones = empleado.evaluaciones.select_related('evaluador').order_by('-fecha_evaluacion')[:5]
    
    # Asistencia del mes actual
    primer_dia_mes = timezone.now().replace(day=1).date()
    asistencia_mes = RegistroAsistencia.objects.filter(
        empleado=empleado,
        fecha__gte=primer_dia_mes
    ).order_by('-fecha')[:10]
    
    # Capacitaciones
    capacitaciones = ParticipacionCapacitacion.objects.filter(
        empleado=empleado
    ).select_related('capacitacion').order_by('-capacitacion__fecha_inicio')[:5]
    
    # Estadísticas del empleado
    stats = {
        'total_evaluaciones': empleado.evaluaciones.count(),
        'promedio_evaluacion': empleado.evaluaciones.aggregate(
            promedio=Avg('puntaje_total')
        )['promedio'] or 0,
        'capacitaciones_completadas': ParticipacionCapacitacion.objects.filter(
            empleado=empleado, aprobado=True
        ).count(),
        'dias_trabajados_mes': RegistroAsistencia.objects.filter(
            empleado=empleado,
            fecha__gte=primer_dia_mes,
            presente=True
        ).count(),
    }
    
    context = {
        'empleado': empleado,
        'horarios': horarios,
        'evaluaciones': evaluaciones,
        'asistencia_mes': asistencia_mes,
        'capacitaciones': capacitaciones,
        'stats': stats,
    }
    
    return render(request, 'empleados/detalle_empleado.html', context)

@login_required
@user_passes_test(es_gerente)
def asistencia_diaria(request):
    """Registro de asistencia diaria"""
    
    # Fecha seleccionada (hoy por defecto)
    fecha_str = request.GET.get('fecha')
    if fecha_str:
        try:
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        except:
            fecha = timezone.now().date()
    else:
        fecha = timezone.now().date()
    
    # Obtener o crear registros de asistencia para todos los empleados activos
    empleados_activos = Empleado.objects.filter(estado=EstadoEmpleado.ACTIVO)
    
    registros = []
    for empleado in empleados_activos:
        # Obtener horario del día
        dias_semana = {
            0: 'lunes', 1: 'martes', 2: 'miercoles', 3: 'jueves',
            4: 'viernes', 5: 'sabado', 6: 'domingo'
        }
        dia_nombre = dias_semana[fecha.weekday()]
        
        try:
            horario = empleado.horarios.get(dia_semana=dia_nombre, activo=True)
            
            # Obtener o crear registro de asistencia
            registro, created = RegistroAsistencia.objects.get_or_create(
                empleado=empleado,
                fecha=fecha,
                defaults={
                    'hora_entrada_programada': horario.hora_entrada,
                    'hora_salida_programada': horario.hora_salida,
                }
            )
            registros.append(registro)
            
        except Horario.DoesNotExist:
            # Empleado no tiene horario para este día
            continue
    
    # Resumen del día
    resumen = {
        'total_empleados': len(registros),
        'presentes': sum(1 for r in registros if r.presente),
        'ausentes': sum(1 for r in registros if not r.presente),
        'tardanzas': sum(1 for r in registros if r.tardanza),
    }
    
    context = {
        'fecha': fecha,
        'registros': registros,
        'resumen': resumen,
    }
    
    return render(request, 'empleados/asistencia_diaria.html', context)

@login_required
@user_passes_test(es_gerente)
@require_POST
def marcar_asistencia(request):
    """Marca la asistencia de un empleado"""
    
    try:
        data = json.loads(request.body)
        registro_id = data.get('registro_id')
        presente = data.get('presente', False)
        hora_entrada = data.get('hora_entrada')
        hora_salida = data.get('hora_salida')
        observaciones = data.get('observaciones', '')
        
        registro = get_object_or_404(RegistroAsistencia, id=registro_id)
        
        # Actualizar registro
        registro.presente = presente
        registro.observaciones = observaciones
        
        if hora_entrada:
            try:
                registro.hora_entrada_real = datetime.strptime(hora_entrada, '%H:%M').time()
                
                # Calcular tardanza
                entrada_programada = datetime.combine(registro.fecha, registro.hora_entrada_programada)
                entrada_real = datetime.combine(registro.fecha, registro.hora_entrada_real)
                
                if entrada_real > entrada_programada:
                    registro.tardanza = True
                    registro.minutos_tardanza = int((entrada_real - entrada_programada).total_seconds() / 60)
                else:
                    registro.tardanza = False
                    registro.minutos_tardanza = 0
                    
            except ValueError:
                pass
        
        if hora_salida:
            try:
                registro.hora_salida_real = datetime.strptime(hora_salida, '%H:%M').time()
                
                # Calcular salida temprana
                salida_programada = datetime.combine(registro.fecha, registro.hora_salida_programada)
                salida_real = datetime.combine(registro.fecha, registro.hora_salida_real)
                
                if salida_real < salida_programada:
                    registro.salida_temprana = True
                    registro.minutos_salida_temprana = int((salida_programada - salida_real).total_seconds() / 60)
                else:
                    registro.salida_temprana = False
                    registro.minutos_salida_temprana = 0
                    
            except ValueError:
                pass
        
        registro.save()
        
        return JsonResponse({
            'success': True,
            'horas_trabajadas': registro.horas_trabajadas
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@user_passes_test(es_gerente)
def evaluaciones_pendientes(request):
    """Lista de empleados que requieren evaluación"""
    
    empleados = Empleado.objects.filter(
        estado=EstadoEmpleado.ACTIVO
    ).filter(
        Q(fecha_proxima_evaluacion__isnull=True) |
        Q(fecha_proxima_evaluacion__lte=timezone.now().date()) |
        Q(evaluacion_actual__lte=5)
    ).select_related('usuario', 'puesto', 'departamento')
    
    context = {
        'empleados': empleados,
    }
    
    return render(request, 'empleados/evaluaciones_pendientes.html', context)

@login_required
@user_passes_test(es_gerente)
def capacitaciones(request):
    """Lista de capacitaciones"""
    
    capacitaciones = Capacitacion.objects.filter(activa=True).order_by('-fecha_inicio')
    
    # Filtros
    tipo = request.GET.get('tipo')
    if tipo:
        capacitaciones = capacitaciones.filter(tipo=tipo)
    
    # Paginación
    paginator = Paginator(capacitaciones, 10)
    page = request.GET.get('page')
    capacitaciones = paginator.get_page(page)
    
    context = {
        'capacitaciones': capacitaciones,
        'tipos': Capacitacion.TIPOS_CAPACITACION,
        'tipo_actual': tipo,
    }
    
    return render(request, 'empleados/capacitaciones.html', context)

@login_required
@user_passes_test(es_gerente)
def reporte_nomina(request):
    """Reporte de nómina mensual"""
    
    # Mes y año actual por defecto
    mes = int(request.GET.get('mes', timezone.now().month))
    año = int(request.GET.get('año', timezone.now().year))
    
    # Obtener nóminas del período
    nominas = Nomina.objects.filter(
        mes=mes,
        año=año
    ).select_related('empleado__usuario', 'empleado__departamento')
    
    # Resumen por departamento
    resumen_departamentos = {}
    for nomina in nominas:
        depto = nomina.empleado.departamento.nombre
        if depto not in resumen_departamentos:
            resumen_departamentos[depto] = {
                'empleados': 0,
                'total_ingresos': 0,
                'total_deducciones': 0,
                'total_neto': 0,
            }
        
        resumen_departamentos[depto]['empleados'] += 1
        resumen_departamentos[depto]['total_ingresos'] += nomina.total_ingresos
        resumen_departamentos[depto]['total_deducciones'] += nomina.total_deducciones
        resumen_departamentos[depto]['total_neto'] += nomina.salario_neto
    
    # Totales generales
    totales = nominas.aggregate(
        total_empleados=Count('id'),
        total_ingresos=Sum('total_ingresos'),
        total_deducciones=Sum('total_deducciones'),
        total_neto=Sum('salario_neto')
    )
    
    context = {
        'nominas': nominas,
        'resumen_departamentos': resumen_departamentos,
        'totales': totales,
        'mes': mes,
        'año': año,
        'mes_nombre': [
            '', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
            'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
        ][mes],
    }
    
    return render(request, 'empleados/reporte_nomina.html', context)

@login_required
def mi_perfil_empleado(request):
    """Perfil del empleado actual"""
    
    try:
        empleado = request.user.empleado
    except Empleado.DoesNotExist:
        messages.error(request, 'No tienes un perfil de empleado.')
        return redirect('usuarios:index')
    
    # Horarios
    horarios = empleado.horarios.filter(activo=True).order_by('dia_semana')
    
    # Última evaluación
    ultima_evaluacion = empleado.evaluaciones.order_by('-fecha_evaluacion').first()
    
    # Asistencia del mes
    primer_dia_mes = timezone.now().replace(day=1).date()
    asistencia_mes = RegistroAsistencia.objects.filter(
        empleado=empleado,
        fecha__gte=primer_dia_mes
    ).order_by('-fecha')
    
    # Capacitaciones
    capacitaciones = ParticipacionCapacitacion.objects.filter(
        empleado=empleado
    ).select_related('capacitacion').order_by('-capacitacion__fecha_inicio')[:5]
    
    context = {
        'empleado': empleado,
        'horarios': horarios,
        'ultima_evaluacion': ultima_evaluacion,
        'asistencia_mes': asistencia_mes,
        'capacitaciones': capacitaciones,
    }
    
    return render(request, 'empleados/mi_perfil.html', context)

def api_empleados_buscar(request):
    """API para buscar empleados"""
    buscar = request.GET.get('q', '')
    
    empleados = Empleado.objects.filter(
        estado=EstadoEmpleado.ACTIVO
    )
    
    if buscar:
        empleados = empleados.filter(
            Q(usuario__first_name__icontains=buscar) |
            Q(usuario__last_name__icontains=buscar) |
            Q(numero_empleado__icontains=buscar)
        )
    
    empleados = empleados.select_related('usuario', 'puesto')[:10]
    
    data = [{
        'id': e.id,
        'nombre': e.nombre_completo,
        'numero': e.numero_empleado,
        'puesto': e.puesto.nombre,
        'departamento': e.departamento.nombre
    } for e in empleados]
    
    return JsonResponse({'empleados': data})
