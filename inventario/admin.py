from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from django.db.models import Sum, Count
from .models import (
    Proveedor, CategoriaInventario, ProductoInventario, 
    MovimientoInventario, OrdenCompra, ItemOrdenCompra,
    AlertaInventario, RecetaConsumo, TipoMovimiento, EstadoOrden
)

@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = [
        'nombre', 'empresa', 'telefono', 'email', 
        'dias_entrega', 'monto_minimo_pedido', 'activo_badge'
    ]
    list_filter = ['activo', 'ciudad', 'dias_entrega']
    search_fields = ['nombre', 'empresa', 'email', 'telefono']
    readonly_fields = ['fecha_registro', 'total_ordenes', 'monto_total_compras']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'empresa', 'activo')
        }),
        ('Contacto', {
            'fields': ('email', 'telefono', 'direccion', 'ciudad', 'codigo_postal')
        }),
        ('Información Fiscal', {
            'fields': ('rfc_cuit', 'razon_social'),
            'classes': ['collapse']
        }),
        ('Términos Comerciales', {
            'fields': ('dias_entrega', 'monto_minimo_pedido', 'descuento_volumen')
        }),
        ('Estadísticas', {
            'fields': ('total_ordenes', 'monto_total_compras'),
            'classes': ['collapse']
        }),
        ('Notas', {
            'fields': ('notas', 'fecha_registro'),
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

@admin.register(CategoriaInventario)
class CategoriaInventarioAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'descripcion', 'color_preview', 'productos_count', 'activo']
    list_filter = ['activo']
    search_fields = ['nombre', 'descripcion']
    
    def color_preview(self, obj):
        return format_html(
            '<div style="width: 20px; height: 20px; background-color: {}; border-radius: 50%; display: inline-block;"></div>',
            obj.color
        )
    color_preview.short_description = 'Color'
    
    def productos_count(self, obj):
        return obj.productos.count()
    productos_count.short_description = 'Productos'

class MovimientoInventarioInline(admin.TabularInline):
    model = MovimientoInventario
    extra = 0
    readonly_fields = ['numero_movimiento', 'stock_anterior', 'stock_nuevo', 'valor_total', 'fecha']
    fields = [
        'tipo_movimiento', 'cantidad', 'costo_unitario', 'valor_total',
        'motivo', 'referencia', 'fecha'
    ]
    ordering = ['-fecha']

@admin.register(ProductoInventario)
class ProductoInventarioAdmin(admin.ModelAdmin):
    list_display = [
        'codigo_producto', 'ingrediente', 'categoria_inventario', 
        'stock_badge', 'unidad_medida', 'costo_unitario', 
        'valor_total_stock', 'nivel_stock_badge'
    ]
    list_filter = [
        'categoria_inventario', 'unidad_medida', 'activo',
        'proveedor_principal'
    ]
    search_fields = [
        'codigo_producto', 'ingrediente__nombre', 
        'categoria_inventario__nombre'
    ]
    readonly_fields = [
        'codigo_producto', 'necesita_reposicion', 'nivel_stock',
        'valor_total_stock', 'rotacion_mensual', 'fecha_creacion', 'fecha_actualizacion'
    ]
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('ingrediente', 'categoria_inventario', 'codigo_producto', 'unidad_medida', 'activo')
        }),
        ('Stock', {
            'fields': ('stock_actual', 'stock_minimo', 'stock_maximo', 'necesita_reposicion', 'nivel_stock')
        }),
        ('Costos', {
            'fields': ('costo_unitario', 'precio_promedio', 'valor_total_stock')
        }),
        ('Proveedor y Vencimiento', {
            'fields': ('proveedor_principal', 'dias_vencimiento')
        }),
        ('Estadísticas', {
            'fields': ('rotacion_mensual',),
            'classes': ['collapse']
        }),
        ('Control', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ['collapse']
        })
    )
    
    inlines = [MovimientoInventarioInline]
    actions = ['generar_alertas_stock', 'actualizar_precios_promedio']
    
    def stock_badge(self, obj):
        return f"{obj.stock_actual} {obj.get_unidad_medida_display()}"
    stock_badge.short_description = 'Stock Actual'
    
    def nivel_stock_badge(self, obj):
        nivel = obj.nivel_stock
        colores = {
            'bajo': 'red',
            'medio': 'orange', 
            'alto': 'green'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            colores[nivel], nivel.title()
        )
    nivel_stock_badge.short_description = 'Nivel'
    
    def generar_alertas_stock(self, request, queryset):
        count = 0
        for producto in queryset:
            if producto.necesita_reposicion:
                AlertaInventario.objects.get_or_create(
                    producto=producto,
                    tipo_alerta='stock_bajo',
                    activa=True,
                    defaults={
                        'mensaje': f'El stock de {producto.ingrediente.nombre} está por debajo del mínimo ({producto.stock_minimo})'
                    }
                )
                count += 1
        self.message_user(request, f'{count} alertas de stock generadas.')
    generar_alertas_stock.short_description = 'Generar alertas de stock bajo'

@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):
    list_display = [
        'numero_corto', 'producto', 'tipo_badge', 'cantidad',
        'costo_unitario', 'valor_total', 'usuario', 'fecha'
    ]
    list_filter = ['tipo_movimiento', 'fecha', 'producto__categoria_inventario']
    search_fields = [
        'numero_movimiento', 'producto__ingrediente__nombre',
        'motivo', 'referencia'
    ]
    readonly_fields = [
        'numero_movimiento', 'stock_anterior', 'stock_nuevo', 'valor_total'
    ]
    date_hierarchy = 'fecha'
    ordering = ['-fecha']
    
    fieldsets = (
        ('Información del Movimiento', {
            'fields': ('numero_movimiento', 'producto', 'tipo_movimiento')
        }),
        ('Cantidades', {
            'fields': ('cantidad', 'costo_unitario', 'valor_total')
        }),
        ('Stock', {
            'fields': ('stock_anterior', 'stock_nuevo')
        }),
        ('Detalles', {
            'fields': ('motivo', 'referencia', 'lote', 'fecha_vencimiento')
        }),
        ('Control', {
            'fields': ('usuario', 'fecha')
        })
    )
    
    def numero_corto(self, obj):
        return f"#{str(obj.numero_movimiento)[:8]}"
    numero_corto.short_description = 'Número'
    
    def tipo_badge(self, obj):
        colores = {
            'entrada': 'green',
            'salida': 'red',
            'ajuste': 'blue',
            'merma': 'orange',
            'devolucion': 'purple'
        }
        color = colores.get(obj.tipo_movimiento, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color, obj.get_tipo_movimiento_display()
        )
    tipo_badge.short_description = 'Tipo'

class ItemOrdenCompraInline(admin.TabularInline):
    model = ItemOrdenCompra
    extra = 0
    readonly_fields = ['total']
    fields = ['producto', 'cantidad', 'precio_unitario', 'total', 'descripcion', 'fecha_vencimiento']

@admin.register(OrdenCompra)
class OrdenCompraAdmin(admin.ModelAdmin):
    list_display = [
        'numero_corto', 'proveedor', 'estado_badge', 'total',
        'fecha_creacion', 'fecha_entrega_estimada', 'creado_por'
    ]
    list_filter = ['estado', 'fecha_creacion', 'proveedor']
    search_fields = ['numero_orden', 'proveedor__nombre', 'notas']
    readonly_fields = [
        'numero_orden', 'fecha_creacion', 'fecha_envio', 'fecha_entrega_real',
        'puede_enviar', 'puede_confirmar', 'puede_recibir'
    ]
    date_hierarchy = 'fecha_creacion'
    ordering = ['-fecha_creacion']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('numero_orden', 'proveedor', 'estado', 'creado_por')
        }),
        ('Fechas', {
            'fields': (
                'fecha_creacion', 'fecha_envio', 'fecha_entrega_estimada', 
                'fecha_entrega_real'
            )
        }),
        ('Montos', {
            'fields': ('subtotal', 'descuento', 'impuestos', 'total')
        }),
        ('Estados', {
            'fields': ('puede_enviar', 'puede_confirmar', 'puede_recibir'),
            'classes': ['collapse']
        }),
        ('Notas', {
            'fields': ('notas', 'terminos_condiciones'),
            'classes': ['collapse']
        })
    )
    
    inlines = [ItemOrdenCompraInline]
    actions = ['enviar_ordenes', 'confirmar_ordenes', 'recibir_ordenes']
    
    def numero_corto(self, obj):
        return f"OC-{str(obj.numero_orden)[:8]}"
    numero_corto.short_description = 'Número'
    
    def estado_badge(self, obj):
        colores = {
            'borrador': 'gray',
            'enviada': 'blue',
            'confirmada': 'orange',
            'recibida': 'green',
            'cancelada': 'red'
        }
        color = colores.get(obj.estado, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color, obj.get_estado_display()
        )
    estado_badge.short_description = 'Estado'
    
    def enviar_ordenes(self, request, queryset):
        count = 0
        for orden in queryset.filter(estado=EstadoOrden.BORRADOR):
            if orden.puede_enviar:
                orden.enviar()
                count += 1
        self.message_user(request, f'{count} órdenes enviadas.')
    enviar_ordenes.short_description = 'Enviar órdenes'
    
    def confirmar_ordenes(self, request, queryset):
        count = 0
        for orden in queryset.filter(estado=EstadoOrden.ENVIADA):
            orden.confirmar()
            count += 1
        self.message_user(request, f'{count} órdenes confirmadas.')
    confirmar_ordenes.short_description = 'Confirmar órdenes'
    
    def recibir_ordenes(self, request, queryset):
        count = 0
        for orden in queryset.filter(estado=EstadoOrden.CONFIRMADA):
            orden.recibir()
            count += 1
        self.message_user(request, f'{count} órdenes recibidas y stock actualizado.')
    recibir_ordenes.short_description = 'Recibir órdenes'

@admin.register(AlertaInventario)
class AlertaInventarioAdmin(admin.ModelAdmin):
    list_display = [
        'producto', 'tipo_badge', 'mensaje_corto', 'activa_badge',
        'fecha_creacion', 'resuelto_por'
    ]
    list_filter = ['tipo_alerta', 'activa', 'fecha_creacion']
    search_fields = ['producto__ingrediente__nombre', 'mensaje']
    readonly_fields = ['fecha_creacion', 'fecha_resolucion']
    actions = ['resolver_alertas']
    
    def tipo_badge(self, obj):
        colores = {
            'stock_bajo': 'orange',
            'stock_agotado': 'red',
            'vencimiento_proximo': 'yellow',
            'vencimiento_hoy': 'orange',
            'producto_vencido': 'red',
            'rotacion_baja': 'blue'
        }
        color = colores.get(obj.tipo_alerta, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_tipo_alerta_display()
        )
    tipo_badge.short_description = 'Tipo'
    
    def mensaje_corto(self, obj):
        return obj.mensaje[:50] + '...' if len(obj.mensaje) > 50 else obj.mensaje
    mensaje_corto.short_description = 'Mensaje'
    
    def activa_badge(self, obj):
        if obj.activa:
            return format_html(
                '<span style="background-color: red; color: white; padding: 3px 8px; border-radius: 3px;">Activa</span>'
            )
        else:
            return format_html(
                '<span style="background-color: green; color: white; padding: 3px 8px; border-radius: 3px;">Resuelta</span>'
            )
    activa_badge.short_description = 'Estado'
    
    def resolver_alertas(self, request, queryset):
        count = 0
        for alerta in queryset.filter(activa=True):
            alerta.resolver(request.user)
            count += 1
        self.message_user(request, f'{count} alertas resueltas.')
    resolver_alertas.short_description = 'Resolver alertas'

@admin.register(RecetaConsumo)
class RecetaConsumoAdmin(admin.ModelAdmin):
    list_display = ['plato', 'producto', 'cantidad_necesaria', 'unidad_medida']
    list_filter = ['plato__categoria', 'producto__categoria_inventario']
    search_fields = ['plato__nombre', 'producto__ingrediente__nombre']
    
    def unidad_medida(self, obj):
        return obj.producto.get_unidad_medida_display()
    unidad_medida.short_description = 'Unidad'
