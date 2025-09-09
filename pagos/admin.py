from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import (
    ConfiguracionPagos, Pago, LogPago, Reembolso, Factura,
    EstadoPago, MetodoPago
)

@admin.register(ConfiguracionPagos)
class ConfiguracionPagosAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Stripe', {
            'fields': ('stripe_activo', 'stripe_public_key', 'stripe_secret_key', 'stripe_webhook_secret'),
            'classes': ['collapse']
        }),
        ('PayPal', {
            'fields': ('paypal_activo', 'paypal_sandbox', 'paypal_client_id', 'paypal_client_secret'),
            'classes': ['collapse']
        }),
        ('MercadoPago', {
            'fields': ('mercadopago_activo', 'mercadopago_sandbox', 'mercadopago_access_token', 'mercadopago_public_key'),
            'classes': ['collapse']
        }),
        ('Configuraciones Generales', {
            'fields': ('comision_tarjeta', 'comision_paypal', 'pago_minimo', 'pago_maximo_efectivo')
        }),
        ('Datos de Facturación', {
            'fields': ('razon_social', 'rfc_cuit', 'direccion_fiscal', 'telefono_facturacion', 'email_facturacion')
        }),
        ('Facturación Automática', {
            'fields': ('facturacion_automatica', 'incluir_iva', 'porcentaje_iva')
        })
    )
    
    def has_add_permission(self, request):
        # Solo permitir una configuración
        return not ConfiguracionPagos.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False

class LogPagoInline(admin.TabularInline):
    model = LogPago
    extra = 0
    readonly_fields = ['fecha_evento']
    fields = ['evento', 'descripcion', 'fecha_evento']
    ordering = ['-fecha_evento']

class ReembolsoInline(admin.TabularInline):
    model = Reembolso
    extra = 0
    readonly_fields = ['numero_reembolso', 'fecha_solicitud']
    fields = ['numero_reembolso', 'monto_reembolsado', 'motivo', 'estado', 'fecha_solicitud']

@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = [
        'numero_corto', 'usuario', 'referencia_display', 'metodo_pago', 
        'total', 'estado_badge', 'fecha_creacion'
    ]
    list_filter = [
        'estado', 'metodo_pago', 'tipo_pago', 'fecha_creacion',
        'requiere_factura', 'factura_generada'
    ]
    search_fields = [
        'numero_pago', 'usuario__username', 'usuario__email',
        'transaction_id', 'numero_factura'
    ]
    readonly_fields = [
        'numero_pago', 'fecha_creacion', 'numero_referencia',
        'puede_reembolsar', 'tiempo_para_vencimiento'
    ]
    date_hierarchy = 'fecha_creacion'
    ordering = ['-fecha_creacion']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('numero_pago', 'tipo_pago', 'usuario', 'pedido', 'reserva')
        }),
        ('Detalles del Pago', {
            'fields': ('metodo_pago', 'estado', 'subtotal', 'impuestos', 'comision', 'descuento', 'total')
        }),
        ('Información del Procesador', {
            'fields': ('payment_intent_id', 'paypal_payment_id', 'mercadopago_payment_id', 'transaction_id'),
            'classes': ['collapse']
        }),
        ('Fechas', {
            'fields': (
                'fecha_creacion', 'fecha_procesamiento', 'fecha_completado', 
                'fecha_vencimiento', 'tiempo_para_vencimiento'
            ),
            'classes': ['collapse']
        }),
        ('Facturación', {
            'fields': ('requiere_factura', 'factura_generada', 'numero_factura', 'datos_facturacion'),
            'classes': ['collapse']
        }),
        ('Información Adicional', {
            'fields': ('descripcion', 'notas_internas', 'ip_cliente', 'user_agent'),
            'classes': ['collapse']
        }),
        ('Control', {
            'fields': ('puede_reembolsar', 'numero_referencia'),
            'classes': ['collapse']
        })
    )
    
    inlines = [LogPagoInline, ReembolsoInline]
    actions = ['marcar_completado', 'generar_facturas', 'enviar_facturas']
    
    def numero_corto(self, obj):
        return f"#{str(obj.numero_pago)[:8]}"
    numero_corto.short_description = 'Número'
    
    def referencia_display(self, obj):
        if obj.pedido:
            return format_html(
                '<a href="{}">{}</a>',
                reverse('admin:pedidos_pedido_change', args=[obj.pedido.pk]),
                f"Pedido #{str(obj.pedido.numero_pedido)[:8]}"
            )
        elif obj.reserva:
            return format_html(
                '<a href="{}">{}</a>',
                reverse('admin:reservas_reserva_change', args=[obj.reserva.pk]),
                f"Reserva #{str(obj.reserva.codigo_reserva)[:8]}"
            )
        return "Sin referencia"
    referencia_display.short_description = 'Referencia'
    
    def estado_badge(self, obj):
        colores = {
            EstadoPago.PENDIENTE: 'orange',
            EstadoPago.PROCESANDO: 'blue',
            EstadoPago.COMPLETADO: 'green',
            EstadoPago.FALLIDO: 'red',
            EstadoPago.CANCELADO: 'gray',
            EstadoPago.REEMBOLSADO: 'purple',
        }
        color = colores.get(obj.estado, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_estado_display()
        )
    estado_badge.short_description = 'Estado'
    
    def marcar_completado(self, request, queryset):
        count = 0
        for pago in queryset.filter(estado=EstadoPago.PROCESANDO):
            pago.marcar_completado()
            count += 1
        self.message_user(request, f'{count} pagos marcados como completados.')
    marcar_completado.short_description = 'Marcar como completado'
    
    def generar_facturas(self, request, queryset):
        count = 0
        for pago in queryset.filter(requiere_factura=True, factura_generada=False):
            if pago.generar_factura():
                count += 1
        self.message_user(request, f'{count} facturas generadas.')
    generar_facturas.short_description = 'Generar facturas'

@admin.register(LogPago)
class LogPagoAdmin(admin.ModelAdmin):
    list_display = ['pago', 'evento', 'descripcion', 'fecha_evento']
    list_filter = ['evento', 'fecha_evento']
    search_fields = ['pago__numero_pago', 'evento', 'descripcion']
    readonly_fields = ['fecha_evento']
    ordering = ['-fecha_evento']

@admin.register(Reembolso)
class ReembolsoAdmin(admin.ModelAdmin):
    list_display = [
        'numero_corto', 'pago_original', 'monto_reembolsado', 
        'estado_badge', 'procesado_por', 'fecha_solicitud'
    ]
    list_filter = ['estado', 'fecha_solicitud']
    search_fields = ['numero_reembolso', 'pago_original__numero_pago', 'motivo']
    readonly_fields = ['numero_reembolso', 'fecha_solicitud']
    ordering = ['-fecha_solicitud']
    
    fieldsets = (
        ('Información del Reembolso', {
            'fields': ('numero_reembolso', 'pago_original', 'monto_reembolsado', 'motivo')
        }),
        ('Estado y Procesamiento', {
            'fields': ('estado', 'procesado_por', 'refund_id')
        }),
        ('Fechas', {
            'fields': ('fecha_solicitud', 'fecha_procesamiento', 'fecha_completado'),
            'classes': ['collapse']
        })
    )
    
    def numero_corto(self, obj):
        return f"#{str(obj.numero_reembolso)[:8]}"
    numero_corto.short_description = 'Número'
    
    def estado_badge(self, obj):
        colores = {
            'pendiente': 'orange',
            'procesando': 'blue',
            'completado': 'green',
            'fallido': 'red',
        }
        color = colores.get(obj.estado, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_estado_display()
        )
    estado_badge.short_description = 'Estado'

@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    list_display = [
        'numero_factura', 'cliente_nombre', 'total', 
        'fecha_emision', 'enviada_badge'
    ]
    list_filter = ['fecha_emision', 'enviada_por_email']
    search_fields = [
        'numero_factura', 'cliente_nombre', 'cliente_email',
        'pago__numero_pago'
    ]
    readonly_fields = ['fecha_emision']
    date_hierarchy = 'fecha_emision'
    ordering = ['-fecha_emision']
    
    fieldsets = (
        ('Información de la Factura', {
            'fields': ('numero_factura', 'pago', 'fecha_emision', 'fecha_vencimiento')
        }),
        ('Datos del Cliente', {
            'fields': ('cliente_nombre', 'cliente_email', 'cliente_telefono', 'cliente_direccion', 'cliente_rfc_cuit')
        }),
        ('Datos de la Empresa', {
            'fields': ('empresa_nombre', 'empresa_rfc_cuit', 'empresa_direccion')
        }),
        ('Montos', {
            'fields': ('subtotal', 'iva', 'total')
        }),
        ('Detalles', {
            'fields': ('items_factura', 'notas'),
            'classes': ['collapse']
        }),
        ('Control de Envío', {
            'fields': ('enviada_por_email', 'fecha_envio_email'),
            'classes': ['collapse']
        })
    )
    
    actions = ['enviar_por_email']
    
    def enviada_badge(self, obj):
        if obj.enviada_por_email:
            return format_html(
                '<span style="background-color: green; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">Enviada</span>'
            )
        else:
            return format_html(
                '<span style="background-color: orange; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">Pendiente</span>'
            )
    enviada_badge.short_description = 'Estado Envío'
    
    def enviar_por_email(self, request, queryset):
        count = 0
        for factura in queryset.filter(enviada_por_email=False):
            if factura.enviar_por_email():
                count += 1
        self.message_user(request, f'{count} facturas enviadas por email.')
    enviar_por_email.short_description = 'Enviar por email'
