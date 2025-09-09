from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from django.db.models import Avg, Count, Sum
from .models import (
    Departamento, Puesto, Empleado, Horario, RegistroAsistencia,
    Evaluacion, Capacitacion, ParticipacionCapacitacion, Nomina,
    EstadoEmpleado, TipoEmpleado
)

@admin.register(Departamento)
class DepartamentoAdmin(admin.ModelAdmin):
    list_display = [
        'nombre', 'responsable', 'total_empleados', 'costo_nomina_mensual', 
        'presupuesto_mensual', 'activo_badge'
    ]
    list_filter = ['activo']
    search_fields = ['nombre', 'descripcion']
    readonly_fields = ['total_empleados', 'costo_nomina_mensual', 'fecha_creacion']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'descripcion', 'activo')
        }),
        ('Gestión', {
            'fields': ('responsable', 'presupuesto_mensual')
        }),
        ('Estadísticas', {
            'fields': ('total_empleados', 'costo_nomina_mensual'),
            'classes': ['collapse']
        }),
        ('Control', {
            'fields': ('fecha_creacion',),
            'classes': ['collapse']
        })
    )
    
    def activo_badge(self, obj):
        if obj.activo:
            return format_html(
                '<span style="background-color: green; color: white; padding: 3px 8px; border-radius: 3px;">Activo</span>'
            )
        else:
            return format_html(
                '<span style="background-color: red; color: white; padding: 3px 8px; border-radius: 3px;">Inactivo</span>'
            )
    activo_badge.short_description = 'Estado'

@admin.register(Puesto)
class PuestoAdmin(admin.ModelAdmin):
    list_display = [
        'nombre', 'departamento', 'tipo_empleado', 'salario_range', 
        'experiencia_minima', 'empleados_count', 'activo'
    ]
    list_filter = ['departamento', 'tipo_empleado', 'activo']
    search_fields = ['nombre', 'descripcion']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'departamento', 'tipo_empleado', 'descripcion', 'activo')
        }),
        ('Requisitos', {
            'fields': ('experiencia_minima', 'educacion_requerida', 'habilidades_requeridas')
        }),
        ('Salario', {
            'fields': ('salario_minimo', 'salario_maximo')
        })
    )
    
    def salario_range(self, obj):
        return f"${obj.salario_minimo} - ${obj.salario_maximo}"
    salario_range.short_description = 'Rango Salarial'
    
    def empleados_count(self, obj):
        return obj.empleados.filter(estado=EstadoEmpleado.ACTIVO).count()
    empleados_count.short_description = 'Empleados Activos'

class HorarioInline(admin.TabularInline):
    model = Horario
    extra = 0
    fields = ['dia_semana', 'hora_entrada', 'hora_salida', 'hora_break_inicio', 'hora_break_fin', 'activo']

class EvaluacionInline(admin.TabularInline):
    model = Evaluacion
    extra = 0
    readonly_fields = ['puntaje_total', 'fecha_creacion']
    fields = [
        'fecha_evaluacion', 'evaluador', 'puntaje_total', 
        'recomendacion_aumento', 'recomendacion_promocion'
    ]
    ordering = ['-fecha_evaluacion']

@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = [
        'numero_empleado', 'nombre_completo', 'puesto', 'departamento', 
        'estado_badge', 'salario_total_mensual', 'evaluacion_badge',
        'fecha_ingreso'
    ]
    list_filter = [
        'estado', 'departamento', 'puesto__tipo_empleado', 
        'tipo_contrato', 'fecha_ingreso'
    ]
    search_fields = [
        'numero_empleado', 'usuario__first_name', 'usuario__last_name',
        'usuario__email', 'cedula'
    ]
    readonly_fields = [
        'numero_empleado', 'nombre_completo', 'edad', 'tiempo_en_empresa',
        'salario_total_mensual', 'requiere_evaluacion', 'fecha_creacion', 'fecha_actualizacion'
    ]
    date_hierarchy = 'fecha_ingreso'
    ordering = ['usuario__last_name', 'usuario__first_name']
    
    fieldsets = (
        ('Usuario del Sistema', {
            'fields': ('usuario',)
        }),
        ('Información Personal', {
            'fields': (
                'cedula', 'fecha_nacimiento', 'edad', 'telefono_personal',
                'telefono_emergencia', 'contacto_emergencia', 'direccion', 
                'ciudad', 'codigo_postal'
            )
        }),
        ('Información Laboral', {
            'fields': (
                'numero_empleado', 'puesto', 'departamento', 'fecha_ingreso',
                'fecha_salida', 'estado', 'tipo_contrato', 'tiempo_en_empresa'
            )
        }),
        ('Salario y Beneficios', {
            'fields': (
                'salario_base', 'comision_ventas', 'bonificaciones', 
                'descuentos', 'salario_total_mensual'
            )
        }),
        ('Horarios', {
            'fields': ('turno_preferido', 'horas_semanales')
        }),
        ('Información Fiscal', {
            'fields': ('nss', 'rfc', 'banco_cuenta'),
            'classes': ['collapse']
        }),
        ('Evaluaciones', {
            'fields': (
                'evaluacion_actual', 'fecha_ultima_evaluacion', 
                'fecha_proxima_evaluacion', 'requiere_evaluacion'
            ),
            'classes': ['collapse']
        }),
        ('Control', {
            'fields': ('activo', 'notas', 'fecha_creacion', 'fecha_actualizacion'),
            'classes': ['collapse']
        })
    )
    
    inlines = [HorarioInline, EvaluacionInline]
    actions = ['activar_empleados', 'desactivar_empleados', 'generar_evaluaciones']
    
    def estado_badge(self, obj):
        colores = {
            'activo': 'green',
            'inactivo': 'gray',
            'vacaciones': 'blue',
            'licencia': 'orange',
            'suspendido': 'red',
            'despedido': 'darkred'
        }
        color = colores.get(obj.estado, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_estado_display()
        )
    estado_badge.short_description = 'Estado'
    
    def evaluacion_badge(self, obj):
        if obj.evaluacion_actual >= 8:
            color = 'green'
        elif obj.evaluacion_actual >= 6:
            color = 'orange'
        else:
            color = 'red'
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}/10</span>',
            color, obj.evaluacion_actual
        )
    evaluacion_badge.short_description = 'Evaluación'
    
    def activar_empleados(self, request, queryset):
        count = queryset.update(estado=EstadoEmpleado.ACTIVO, activo=True)
        self.message_user(request, f'{count} empleados activados.')
    activar_empleados.short_description = 'Activar empleados seleccionados'
    
    def desactivar_empleados(self, request, queryset):
        count = queryset.update(estado=EstadoEmpleado.INACTIVO, activo=False)
        self.message_user(request, f'{count} empleados desactivados.')
    desactivar_empleados.short_description = 'Desactivar empleados seleccionados'

@admin.register(RegistroAsistencia)
class RegistroAsistenciaAdmin(admin.ModelAdmin):
    list_display = [
        'empleado', 'fecha', 'presente_badge', 'hora_entrada_real',
        'hora_salida_real', 'tardanza_badge', 'horas_trabajadas'
    ]
    list_filter = [
        'fecha', 'presente', 'tardanza', 'salida_temprana',
        'empleado__departamento'
    ]
    search_fields = ['empleado__usuario__first_name', 'empleado__usuario__last_name']
    date_hierarchy = 'fecha'
    ordering = ['-fecha', 'empleado']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('empleado', 'fecha')
        }),
        ('Horarios Programados', {
            'fields': ('hora_entrada_programada', 'hora_salida_programada')
        }),
        ('Horarios Reales', {
            'fields': ('hora_entrada_real', 'hora_salida_real')
        }),
        ('Break/Almuerzo', {
            'fields': ('hora_break_inicio', 'hora_break_fin')
        }),
        ('Estado del Día', {
            'fields': (
                'presente', 'tardanza', 'minutos_tardanza',
                'salida_temprana', 'minutos_salida_temprana'
            )
        }),
        ('Observaciones', {
            'fields': ('observaciones', 'justificacion', 'aprobado_por')
        })
    )
    
    def presente_badge(self, obj):
        if obj.presente:
            return format_html(
                '<span style="background-color: green; color: white; padding: 3px 8px; border-radius: 3px;">Presente</span>'
            )
        else:
            return format_html(
                '<span style="background-color: red; color: white; padding: 3px 8px; border-radius: 3px;">Ausente</span>'
            )
    presente_badge.short_description = 'Asistencia'
    
    def tardanza_badge(self, obj):
        if obj.tardanza:
            return format_html(
                '<span style="background-color: orange; color: white; padding: 3px 8px; border-radius: 3px;">+{} min</span>',
                obj.minutos_tardanza
            )
        else:
            return format_html(
                '<span style="background-color: green; color: white; padding: 3px 8px; border-radius: 3px;">Puntual</span>'
            )
    tardanza_badge.short_description = 'Puntualidad'

@admin.register(Evaluacion)
class EvaluacionAdmin(admin.ModelAdmin):
    list_display = [
        'empleado', 'fecha_evaluacion', 'evaluador', 'puntaje_badge',
        'recomendacion_aumento', 'recomendacion_promocion'
    ]
    list_filter = [
        'fecha_evaluacion', 'evaluador', 'recomendacion_aumento',
        'recomendacion_promocion', 'empleado__departamento'
    ]
    search_fields = ['empleado__usuario__first_name', 'empleado__usuario__last_name']
    readonly_fields = ['puntaje_total']
    date_hierarchy = 'fecha_evaluacion'
    ordering = ['-fecha_evaluacion']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('empleado', 'evaluador', 'fecha_evaluacion')
        }),
        ('Período Evaluado', {
            'fields': ('periodo_inicio', 'periodo_fin')
        }),
        ('Criterios de Evaluación', {
            'fields': (
                'puntualidad', 'calidad_trabajo', 'productividad',
                'trabajo_equipo', 'iniciativa', 'atencion_cliente'
            )
        }),
        ('Resultado', {
            'fields': ('puntaje_total',)
        }),
        ('Comentarios', {
            'fields': (
                'fortalezas', 'areas_mejora', 'objetivos_siguientes',
                'comentarios_generales'
            ),
            'classes': ['collapse']
        }),
        ('Recomendaciones', {
            'fields': (
                'recomendacion_aumento', 'recomendacion_promocion',
                'recomendacion_capacitacion'
            )
        })
    )
    
    def puntaje_badge(self, obj):
        if obj.puntaje_total >= 8:
            color = 'green'
            nivel = 'Excelente'
        elif obj.puntaje_total >= 6:
            color = 'orange'
            nivel = 'Bueno'
        else:
            color = 'red'
            nivel = 'Necesita Mejora'
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{:.1f} - {}</span>',
            color, obj.puntaje_total, nivel
        )
    puntaje_badge.short_description = 'Puntaje'

class ParticipacionCapacitacionInline(admin.TabularInline):
    model = ParticipacionCapacitacion
    extra = 0
    fields = [
        'empleado', 'asistio', 'horas_asistidas', 
        'calificacion', 'aprobado', 'certificado'
    ]

@admin.register(Capacitacion)
class CapacitacionAdmin(admin.ModelAdmin):
    list_display = [
        'nombre', 'tipo', 'fecha_inicio', 'fecha_fin',
        'total_participantes', 'costo', 'activa'
    ]
    list_filter = ['tipo', 'fecha_inicio', 'modalidad', 'activa']
    search_fields = ['nombre', 'descripcion', 'instructor']
    date_hierarchy = 'fecha_inicio'
    ordering = ['-fecha_inicio']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'descripcion', 'tipo', 'instructor', 'activa')
        }),
        ('Fechas y Duración', {
            'fields': ('fecha_inicio', 'fecha_fin', 'horas_duracion')
        }),
        ('Logística', {
            'fields': ('costo', 'ubicacion', 'modalidad')
        })
    )
    
    inlines = [ParticipacionCapacitacionInline]

@admin.register(Nomina)
class NominaAdmin(admin.ModelAdmin):
    list_display = [
        'empleado', 'mes_año', 'salario_base', 'total_ingresos',
        'total_deducciones', 'salario_neto', 'procesada_badge'
    ]
    list_filter = ['año', 'mes', 'procesada', 'empleado__departamento']
    search_fields = ['empleado__usuario__first_name', 'empleado__usuario__last_name']
    readonly_fields = ['total_ingresos', 'total_deducciones', 'salario_neto']
    ordering = ['-año', '-mes', 'empleado']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('empleado', 'mes', 'año')
        }),
        ('Ingresos', {
            'fields': ('salario_base', 'horas_extra', 'comisiones', 'bonificaciones', 'total_ingresos')
        }),
        ('Deducciones', {
            'fields': ('impuestos', 'seguro_social', 'otras_deducciones', 'total_deducciones')
        }),
        ('Total', {
            'fields': ('salario_neto',)
        }),
        ('Control', {
            'fields': ('procesada', 'fecha_procesamiento', 'procesada_por'),
            'classes': ['collapse']
        })
    )
    
    actions = ['procesar_nominas']
    
    def mes_año(self, obj):
        return f"{obj.mes:02d}/{obj.año}"
    mes_año.short_description = 'Período'
    
    def procesada_badge(self, obj):
        if obj.procesada:
            return format_html(
                '<span style="background-color: green; color: white; padding: 3px 8px; border-radius: 3px;">Procesada</span>'
            )
        else:
            return format_html(
                '<span style="background-color: orange; color: white; padding: 3px 8px; border-radius: 3px;">Pendiente</span>'
            )
    procesada_badge.short_description = 'Estado'
    
    def procesar_nominas(self, request, queryset):
        count = 0
        for nomina in queryset.filter(procesada=False):
            nomina.procesada = True
            nomina.fecha_procesamiento = timezone.now()
            nomina.procesada_por = request.user
            nomina.save()
            count += 1
        self.message_user(request, f'{count} nóminas procesadas.')
    procesar_nominas.short_description = 'Procesar nóminas seleccionadas'
