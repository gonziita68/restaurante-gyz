from django.contrib import admin
from django.utils.html import format_html
from .models import (
    TipoEvento, ServicioAdicional, MenuEvento, Evento, 
    Catering, CotizacionEvento, PresupuestoEvento
)

@admin.register(TipoEvento)
class TipoEventoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'precio_base', 'capacidad_minima', 'capacidad_maxima', 'duracion_estimada', 'imagen_preview', 'activo']
    list_filter = ['activo', 'capacidad_minima', 'capacidad_maxima']
    search_fields = ['nombre', 'descripcion']
    list_editable = ['activo', 'precio_base']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'descripcion', 'imagen')
        }),
        ('Configuración', {
            'fields': ('precio_base', 'capacidad_minima', 'capacidad_maxima', 'duracion_estimada')
        }),
        ('Estado', {
            'fields': ('activo',)
        })
    )
    
    def imagen_preview(self, obj):
        if obj.imagen:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 5px;">',
                obj.imagen.url
            )
        return "Sin imagen"
    imagen_preview.short_description = 'Vista Previa'

@admin.register(ServicioAdicional)
class ServicioAdicionalAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'precio', 'precio_por_persona', 'activo']
    list_filter = ['activo', 'precio_por_persona']
    search_fields = ['nombre', 'descripcion']
    list_editable = ['activo', 'precio']

@admin.register(MenuEvento)
class MenuEventoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'precio_por_persona', 'bebidas_incluidas', 'postre_incluido', 'imagen_preview', 'activo']
    list_filter = ['activo', 'bebidas_incluidas', 'postre_incluido']
    search_fields = ['nombre', 'descripcion', 'platos']
    list_editable = ['activo', 'precio_por_persona']
    
    fieldsets = (
        ('Información del Menú', {
            'fields': ('nombre', 'descripcion', 'imagen')
        }),
        ('Detalles', {
            'fields': ('platos', 'precio_por_persona')
        }),
        ('Incluye', {
            'fields': ('bebidas_incluidas', 'postre_incluido')
        }),
        ('Estado', {
            'fields': ('activo',)
        })
    )
    
    def imagen_preview(self, obj):
        if obj.imagen:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 5px;">',
                obj.imagen.url
            )
        return "Sin imagen"
    imagen_preview.short_description = 'Vista Previa'

@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = [
        'nombre_evento', 'cliente', 'fecha_evento', 'hora_inicio', 
        'numero_invitados', 'estado', 'categoria', 'total'
    ]
    list_filter = [
        'estado', 'categoria', 'tipo_ubicacion', 'fecha_evento', 
        'tipo_evento', 'menu_evento'
    ]
    search_fields = ['nombre_evento', 'cliente__email', 'cliente__first_name', 'cliente__last_name']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion', 'total']
    date_hierarchy = 'fecha_evento'
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('cliente', 'nombre_evento', 'descripcion', 'categoria')
        }),
        ('Fechas y Horarios', {
            'fields': ('fecha_evento', 'hora_inicio', 'hora_fin', 'fecha_solicitud')
        }),
        ('Ubicación', {
            'fields': ('tipo_ubicacion', 'direccion_evento', 'instrucciones_ubicacion')
        }),
        ('Capacidad', {
            'fields': ('numero_invitados', 'numero_confirmados')
        }),
        ('Servicios', {
            'fields': ('tipo_evento', 'menu_evento', 'servicios_adicionales')
        }),
        ('Servicios Especiales', {
            'fields': ('decoracion_especial', 'musica_especial', 'fotografo')
        }),
        ('Estado y Costos', {
            'fields': ('estado', 'subtotal', 'descuento', 'total')
        }),
        ('Información Adicional', {
            'fields': ('notas_especiales', 'alergias_especiales', 'preferencias_dieteticas')
        }),
        ('Timestamps', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Catering)
class CateringAdmin(admin.ModelAdmin):
    list_display = [
        'evento', 'tipo_catering', 'incluye_servicio_mesa', 
        'incluye_equipamiento', 'incluye_personal'
    ]
    list_filter = [
        'tipo_catering', 'incluye_servicio_mesa', 'incluye_equipamiento', 
        'incluye_personal', 'mesas_sillas', 'manteleria', 'vajilla'
    ]
    search_fields = ['evento__nombre_evento', 'evento__cliente__email']
    
    fieldsets = (
        ('Información del Evento', {
            'fields': ('evento', 'tipo_catering')
        }),
        ('Servicios Incluidos', {
            'fields': ('incluye_servicio_mesa', 'incluye_equipamiento', 'incluye_personal')
        }),
        ('Personal Requerido', {
            'fields': ('numero_meseros', 'numero_chefs')
        }),
        ('Equipamiento', {
            'fields': ('equipamiento_requerido', 'mesas_sillas', 'manteleria', 'vajilla')
        }),
        ('Horarios', {
            'fields': ('hora_entrega', 'hora_recogida')
        }),
    )

@admin.register(CotizacionEvento)
class CotizacionEventoAdmin(admin.ModelAdmin):
    list_display = [
        'evento', 'estado', 'fecha_creacion', 'fecha_expiracion', 
        'subtotal', 'descuento', 'total'
    ]
    list_filter = ['estado', 'fecha_creacion', 'fecha_expiracion']
    search_fields = ['evento__nombre_evento', 'evento__cliente__email']
    readonly_fields = ['fecha_creacion']
    
    fieldsets = (
        ('Información del Evento', {
            'fields': ('evento', 'estado')
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_expiracion', 'fecha_respuesta')
        }),
        ('Costos', {
            'fields': ('subtotal', 'descuento', 'total')
        }),
        ('Notas', {
            'fields': ('notas_cliente', 'notas_internas')
        }),
    )

@admin.register(PresupuestoEvento)
class PresupuestoEventoAdmin(admin.ModelAdmin):
    list_display = [
        'evento', 'version', 'subtotal', 'impuestos', 'descuento', 
        'total', 'aprobado', 'fecha_creacion'
    ]
    list_filter = ['aprobado', 'fecha_creacion', 'version']
    search_fields = ['evento__nombre_evento', 'evento__cliente__email']
    readonly_fields = ['fecha_creacion']
    
    fieldsets = (
        ('Información del Evento', {
            'fields': ('evento', 'version', 'aprobado')
        }),
        ('Desglose de Costos', {
            'fields': (
                'costo_menu', 'costo_servicios', 'costo_decoracion',
                'costo_personal', 'costo_equipamiento', 'costo_transporte'
            )
        }),
        ('Totales', {
            'fields': ('subtotal', 'impuestos', 'descuento', 'total')
        }),
        ('Información Adicional', {
            'fields': ('notas', 'fecha_creacion')
        }),
    )
