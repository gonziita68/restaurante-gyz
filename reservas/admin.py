from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.db.models import Q
from .models import (
    ConfiguracionRestaurante, TipoMesa, Mesa, Reserva, 
    HistorialReserva, BloqueoMesa, EstadoReserva
)

@admin.register(ConfiguracionRestaurante)
class ConfiguracionRestauranteAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Información General', {
            'fields': ('nombre', 'telefono_contacto', 'email_contacto')
        }),
        ('Horarios de Operación', {
            'fields': ('hora_apertura', 'hora_cierre', 'dias_cerrado')
        }),
        ('Configuración de Reservas', {
            'fields': (
                'duracion_turno_minutos', 'tiempo_minimo_reserva_horas',
                'tiempo_maximo_reserva_dias', 'permite_cancelacion_horas'
            )
        })
    )
    
    def has_add_permission(self, request):
        # Solo permitir una configuración
        return not ConfiguracionRestaurante.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(TipoMesa)
class TipoMesaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'capacidad_range', 'cantidad_mesas', 'precio_base', 'activo']
    list_filter = ['activo', 'capacidad_minima', 'capacidad_maxima']
    search_fields = ['nombre', 'descripcion']
    ordering = ['capacidad_minima']
    
    def capacidad_range(self, obj):
        return f"{obj.capacidad_minima}-{obj.capacidad_maxima} personas"
    capacidad_range.short_description = 'Capacidad'
    
    def cantidad_mesas(self, obj):
        return obj.mesas.filter(activa=True).count()
    cantidad_mesas.short_description = 'Mesas Activas'

@admin.register(Mesa)
class MesaAdmin(admin.ModelAdmin):
    list_display = ['numero', 'tipo_mesa', 'ubicacion', 'capacidad_display', 'activa', 'reservas_hoy']
    list_filter = ['activa', 'ubicacion', 'tipo_mesa']
    search_fields = ['numero', 'descripcion']
    ordering = ['numero']
    
    def capacidad_display(self, obj):
        return f"{obj.capacidad_minima}-{obj.capacidad_maxima}"
    capacidad_display.short_description = 'Capacidad'
    
    def reservas_hoy(self, obj):
        hoy = timezone.now().date()
        count = obj.reservas.filter(fecha_reserva=hoy, estado__in=['confirmada', 'en_curso']).count()
        return count
    reservas_hoy.short_description = 'Reservas Hoy'

class HistorialReservaInline(admin.TabularInline):
    model = HistorialReserva
    extra = 0
    readonly_fields = ['fecha_cambio']
    fields = ['estado_anterior', 'estado_nuevo', 'usuario_responsable', 'comentario', 'fecha_cambio']

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = [
        'codigo_corto', 'nombre_cliente', 'mesa', 'fecha_reserva', 
        'hora_reserva', 'numero_comensales', 'estado_badge', 'tiempo_restante'
    ]
    list_filter = [
        'estado', 'fecha_reserva', 'mesa__ubicacion', 'ocasion_especial',
        'fecha_creacion'
    ]
    search_fields = [
        'codigo_reserva', 'nombre_cliente', 'telefono_cliente', 
        'email_cliente', 'mesa__numero'
    ]
    readonly_fields = [
        'codigo_reserva', 'fecha_creacion', 'fecha_hora_reserva',
        'puede_cancelar', 'tiempo_para_reserva'
    ]
    date_hierarchy = 'fecha_reserva'
    ordering = ['-fecha_reserva', '-hora_reserva']
    
    fieldsets = (
        ('Información de la Reserva', {
            'fields': ('codigo_reserva', 'estado', 'mesa', 'fecha_reserva', 'hora_reserva', 'numero_comensales')
        }),
        ('Información del Cliente', {
            'fields': ('usuario', 'nombre_cliente', 'telefono_cliente', 'email_cliente')
        }),
        ('Detalles Adicionales', {
            'fields': ('ocasion_especial', 'preferencia_ubicacion', 'solicitudes_especiales'),
            'classes': ['collapse']
        }),
        ('Información del Sistema', {
            'fields': (
                'duracion_estimada', 'fecha_hora_reserva', 'puede_cancelar', 
                'tiempo_para_reserva', 'fecha_creacion'
            ),
            'classes': ['collapse']
        }),
        ('Gestión Interna', {
            'fields': ('usuario_confirmacion', 'notas_internas'),
            'classes': ['collapse']
        }),
        ('Fechas de Control', {
            'fields': (
                'fecha_confirmacion', 'fecha_llegada', 
                'fecha_salida', 'fecha_cancelacion'
            ),
            'classes': ['collapse']
        })
    )
    
    actions = ['confirmar_reservas', 'marcar_en_curso', 'marcar_completadas', 'cancelar_reservas']
    inlines = [HistorialReservaInline]
    
    def codigo_corto(self, obj):
        return f"#{str(obj.codigo_reserva)[:8]}"
    codigo_corto.short_description = 'Código'
    
    def estado_badge(self, obj):
        colores = {
            EstadoReserva.PENDIENTE: 'orange',
            EstadoReserva.CONFIRMADA: 'blue',
            EstadoReserva.EN_CURSO: 'green',
            EstadoReserva.COMPLETADA: 'darkgreen',
            EstadoReserva.CANCELADA: 'red',
            EstadoReserva.NO_SHOW: 'gray',
        }
        color = colores.get(obj.estado, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_estado_display()
        )
    estado_badge.short_description = 'Estado'
    
    def tiempo_restante(self, obj):
        if obj.estado in [EstadoReserva.COMPLETADA, EstadoReserva.CANCELADA, EstadoReserva.NO_SHOW]:
            return obj.get_estado_display()
        
        tiempo = obj.tiempo_para_reserva
        if tiempo.total_seconds() > 0:
            dias = tiempo.days
            horas = tiempo.seconds // 3600
            if dias > 0:
                return f"{dias}d {horas}h"
            elif horas > 0:
                return f"{horas}h"
            else:
                minutos = (tiempo.seconds % 3600) // 60
                return f"{minutos}m"
        else:
            return "Vencida"
    tiempo_restante.short_description = 'Tiempo Restante'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('mesa', 'usuario', 'usuario_confirmacion')
    
    def confirmar_reservas(self, request, queryset):
        count = 0
        for reserva in queryset.filter(estado=EstadoReserva.PENDIENTE):
            reserva.confirmar(request.user)
            count += 1
        self.message_user(request, f'{count} reservas confirmadas.')
    confirmar_reservas.short_description = 'Confirmar reservas seleccionadas'
    
    def marcar_en_curso(self, request, queryset):
        count = 0
        for reserva in queryset.filter(estado=EstadoReserva.CONFIRMADA):
            reserva.marcar_en_curso()
            count += 1
        self.message_user(request, f'{count} reservas marcadas en curso.')
    marcar_en_curso.short_description = 'Marcar como en curso'
    
    def marcar_completadas(self, request, queryset):
        count = 0
        for reserva in queryset.filter(estado=EstadoReserva.EN_CURSO):
            reserva.marcar_completada()
            count += 1
        self.message_user(request, f'{count} reservas completadas.')
    marcar_completadas.short_description = 'Marcar como completadas'
    
    def cancelar_reservas(self, request, queryset):
        count = 0
        for reserva in queryset:
            if reserva.cancelar():
                count += 1
        self.message_user(request, f'{count} reservas canceladas.')
    cancelar_reservas.short_description = 'Cancelar reservas'

@admin.register(HistorialReserva)
class HistorialReservaAdmin(admin.ModelAdmin):
    list_display = ['reserva', 'estado_anterior', 'estado_nuevo', 'fecha_cambio', 'usuario_responsable']
    list_filter = ['estado_anterior', 'estado_nuevo', 'fecha_cambio']
    search_fields = ['reserva__codigo_reserva', 'reserva__nombre_cliente']
    readonly_fields = ['fecha_cambio']
    ordering = ['-fecha_cambio']

@admin.register(BloqueoMesa)
class BloqueoMesaAdmin(admin.ModelAdmin):
    list_display = [
        'mesa', 'motivo', 'fecha_inicio', 'fecha_fin', 
        'activo_badge', 'usuario_creacion'
    ]
    list_filter = ['activo', 'motivo', 'fecha_inicio', 'mesa__ubicacion']
    search_fields = ['mesa__numero', 'descripcion']
    readonly_fields = ['fecha_creacion', 'esta_activo']
    date_hierarchy = 'fecha_inicio'
    ordering = ['-fecha_inicio']
    
    fieldsets = (
        ('Información del Bloqueo', {
            'fields': ('mesa', 'motivo', 'descripcion')
        }),
        ('Período de Bloqueo', {
            'fields': ('fecha_inicio', 'fecha_fin', 'activo')
        }),
        ('Control', {
            'fields': ('usuario_creacion', 'fecha_creacion', 'esta_activo'),
            'classes': ['collapse']
        })
    )
    
    def activo_badge(self, obj):
        if obj.esta_activo:
            return format_html(
                '<span style="background-color: red; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">Activo</span>'
            )
        elif obj.activo:
            return format_html(
                '<span style="background-color: orange; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">Programado</span>'
            )
        else:
            return format_html(
                '<span style="background-color: gray; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">Inactivo</span>'
            )
    activo_badge.short_description = 'Estado'
    
    def save_model(self, request, obj, form, change):
        if not change:  # Si es una nueva instancia
            obj.usuario_creacion = request.user
        super().save_model(request, obj, form, change)
