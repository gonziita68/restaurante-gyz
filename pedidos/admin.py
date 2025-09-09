from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import (
    CarritoCompras, ItemCarrito, Pedido, ItemPedido, 
    SeguimientoPedido, EstadoPedido
)

class ItemCarritoInline(admin.TabularInline):
    model = ItemCarrito
    extra = 0
    readonly_fields = ['fecha_agregado', 'total']
    fields = ['plato', 'cantidad', 'precio_unitario', 'opciones_personalizacion', 'total']
    filter_horizontal = ['opciones_personalizacion']

@admin.register(CarritoCompras)
class CarritoComprasAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'usuario', 'total_items', 'subtotal', 'fecha_actualizacion', 'activo']
    list_filter = ['activo', 'fecha_creacion']
    search_fields = ['usuario__username', 'usuario__email', 'session_key']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion', 'total_items', 'subtotal', 'total_final']
    
    inlines = [ItemCarritoInline]
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('usuario', 'session_key', 'activo')
        }),
        ('Resumen', {
            'fields': ('total_items', 'subtotal', 'total_final'),
            'classes': ['collapse']
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ['collapse']
        })
    )

class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 0
    readonly_fields = ['total']
    fields = ['plato', 'cantidad', 'precio_unitario', 'precio_opciones', 'total', 'instrucciones_especiales']

class SeguimientoPedidoInline(admin.TabularInline):
    model = SeguimientoPedido
    extra = 0
    readonly_fields = ['fecha_cambio']
    fields = ['estado_anterior', 'estado_nuevo', 'usuario_responsable', 'comentario', 'fecha_cambio']

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = [
        'numero_pedido_corto', 'usuario', 'estado_badge', 'tipo_entrega', 
        'total', 'fecha_pedido', 'tiempo_restante', 'pago_completado'
    ]
    list_filter = ['estado', 'tipo_entrega', 'metodo_pago', 'pago_completado', 'fecha_pedido']
    search_fields = ['numero_pedido', 'usuario__username', 'usuario__email', 'telefono_contacto']
    readonly_fields = [
        'numero_pedido', 'fecha_pedido', 'tiempo_restante_estimado',
        'puede_cancelar'
    ]
    
    fieldsets = (
        ('Información del Pedido', {
            'fields': ('numero_pedido', 'usuario', 'estado', 'tipo_entrega')
        }),
        ('Información de Entrega', {
            'fields': ('direccion_entrega', 'telefono_contacto', 'numero_mesa', 'notas_entrega')
        }),
        ('Precios', {
            'fields': ('subtotal', 'impuestos', 'costo_delivery', 'total')
        }),
        ('Pago', {
            'fields': ('metodo_pago', 'pago_completado')
        }),
        ('Tiempos', {
            'fields': (
                'fecha_pedido', 'tiempo_estimado_preparacion', 'tiempo_restante_estimado',
                'fecha_confirmacion', 'fecha_listo', 'fecha_entrega'
            ),
            'classes': ['collapse']
        }),
        ('Estado', {
            'fields': ('puede_cancelar',),
            'classes': ['collapse']
        })
    )
    
    inlines = [ItemPedidoInline, SeguimientoPedidoInline]
    
    actions = ['confirmar_pedidos', 'marcar_en_preparacion', 'marcar_listo', 'marcar_entregado']
    
    def numero_pedido_corto(self, obj):
        return f"#{str(obj.numero_pedido)[:8]}..."
    numero_pedido_corto.short_description = 'Número de Pedido'
    
    def estado_badge(self, obj):
        colores = {
            EstadoPedido.PENDIENTE: 'orange',
            EstadoPedido.CONFIRMADO: 'blue',
            EstadoPedido.EN_PREPARACION: 'purple',
            EstadoPedido.LISTO: 'green',
            EstadoPedido.EN_CAMINO: 'teal',
            EstadoPedido.ENTREGADO: 'darkgreen',
            EstadoPedido.CANCELADO: 'red',
        }
        color = colores.get(obj.estado, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_estado_display()
        )
    estado_badge.short_description = 'Estado'
    
    def tiempo_restante(self, obj):
        tiempo = obj.tiempo_restante_estimado
        if tiempo > 0:
            return f"{tiempo} min"
        elif obj.estado == EstadoPedido.ENTREGADO:
            return "Entregado"
        elif obj.estado == EstadoPedido.CANCELADO:
            return "Cancelado"
        else:
            return "Retrasado"
    tiempo_restante.short_description = 'Tiempo Restante'
    
    def confirmar_pedidos(self, request, queryset):
        count = 0
        for pedido in queryset:
            if pedido.estado == EstadoPedido.PENDIENTE:
                pedido.confirmar_pedido()
                count += 1
        self.message_user(request, f'{count} pedidos confirmados.')
    confirmar_pedidos.short_description = 'Confirmar pedidos seleccionados'
    
    def marcar_en_preparacion(self, request, queryset):
        count = 0
        for pedido in queryset:
            if pedido.estado == EstadoPedido.CONFIRMADO:
                pedido.marcar_en_preparacion()
                count += 1
        self.message_user(request, f'{count} pedidos marcados en preparación.')
    marcar_en_preparacion.short_description = 'Marcar en preparación'
    
    def marcar_listo(self, request, queryset):
        count = 0
        for pedido in queryset:
            if pedido.estado == EstadoPedido.EN_PREPARACION:
                pedido.marcar_listo()
                count += 1
        self.message_user(request, f'{count} pedidos marcados como listos.')
    marcar_listo.short_description = 'Marcar como listo'
    
    def marcar_entregado(self, request, queryset):
        count = 0
        for pedido in queryset:
            if pedido.estado in [EstadoPedido.LISTO, EstadoPedido.EN_CAMINO]:
                pedido.marcar_entregado()
                count += 1
        self.message_user(request, f'{count} pedidos marcados como entregados.')
    marcar_entregado.short_description = 'Marcar como entregado'

@admin.register(ItemCarrito)
class ItemCarritoAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'carrito', 'precio_unitario', 'cantidad', 'total', 'fecha_agregado']
    list_filter = ['fecha_agregado', 'plato__categoria']
    search_fields = ['plato__nombre', 'carrito__usuario__username']
    readonly_fields = ['fecha_agregado', 'total']
    filter_horizontal = ['opciones_personalizacion']

@admin.register(ItemPedido)
class ItemPedidoAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'pedido', 'precio_unitario', 'cantidad', 'total']
    list_filter = ['pedido__fecha_pedido', 'plato__categoria']
    search_fields = ['plato__nombre', 'pedido__numero_pedido', 'pedido__usuario__username']
    readonly_fields = ['total']

@admin.register(SeguimientoPedido)
class SeguimientoPedidoAdmin(admin.ModelAdmin):
    list_display = ['pedido', 'estado_anterior', 'estado_nuevo', 'fecha_cambio', 'usuario_responsable']
    list_filter = ['estado_anterior', 'estado_nuevo', 'fecha_cambio']
    search_fields = ['pedido__numero_pedido', 'pedido__usuario__username']
    readonly_fields = ['fecha_cambio']
