from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.utils import timezone
from pedidos.models import Pedido
from reservas.models import Reserva
from decimal import Decimal
import uuid

User = get_user_model()

class MetodoPago(models.TextChoices):
    """Métodos de pago disponibles"""
    EFECTIVO = 'efectivo', 'Efectivo'
    TARJETA = 'tarjeta', 'Tarjeta de Crédito/Débito'
    STRIPE = 'stripe', 'Stripe'
    PAYPAL = 'paypal', 'PayPal'
    TRANSFERENCIA = 'transferencia', 'Transferencia Bancaria'
    MERCADOPAGO = 'mercadopago', 'MercadoPago'

class EstadoPago(models.TextChoices):
    """Estados posibles de un pago"""
    PENDIENTE = 'pendiente', 'Pendiente'
    PROCESANDO = 'procesando', 'Procesando'
    COMPLETADO = 'completado', 'Completado'
    FALLIDO = 'fallido', 'Fallido'
    CANCELADO = 'cancelado', 'Cancelado'
    REEMBOLSADO = 'reembolsado', 'Reembolsado'

class TipoPago(models.TextChoices):
    """Tipos de pago según el origen"""
    PEDIDO = 'pedido', 'Pago de Pedido'
    RESERVA = 'reserva', 'Pago de Reserva'
    OTRO = 'otro', 'Otro'

class ConfiguracionPagos(models.Model):
    """Configuración general del sistema de pagos"""
    
    # Stripe
    stripe_public_key = models.CharField(max_length=200, blank=True)
    stripe_secret_key = models.CharField(max_length=200, blank=True)
    stripe_webhook_secret = models.CharField(max_length=200, blank=True)
    stripe_activo = models.BooleanField(default=False)
    
    # PayPal
    paypal_client_id = models.CharField(max_length=200, blank=True)
    paypal_client_secret = models.CharField(max_length=200, blank=True)
    paypal_sandbox = models.BooleanField(default=True, help_text="Usar sandbox de PayPal")
    paypal_activo = models.BooleanField(default=False)
    
    # MercadoPago
    mercadopago_access_token = models.CharField(max_length=200, blank=True)
    mercadopago_public_key = models.CharField(max_length=200, blank=True)
    mercadopago_sandbox = models.BooleanField(default=True)
    mercadopago_activo = models.BooleanField(default=False)
    
    # Configuraciones generales
    comision_tarjeta = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=Decimal('3.50'),
        help_text="Comisión por pago con tarjeta (%)"
    )
    comision_paypal = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=Decimal('3.49'),
        help_text="Comisión de PayPal (%)"
    )
    
    # Límites
    pago_minimo = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('5.00'),
        help_text="Monto mínimo para procesar pagos"
    )
    pago_maximo_efectivo = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('1000.00'),
        help_text="Monto máximo permitido en efectivo"
    )
    
    # Facturación
    razon_social = models.CharField(max_length=200, default="Restaurante GYZ S.A.")
    rfc_cuit = models.CharField(max_length=20, blank=True, help_text="RFC/CUIT para facturación")
    direccion_fiscal = models.TextField(blank=True)
    telefono_facturacion = models.CharField(max_length=15, blank=True)
    email_facturacion = models.EmailField(blank=True)
    
    # Configuración de facturación automática
    facturacion_automatica = models.BooleanField(default=True)
    incluir_iva = models.BooleanField(default=True)
    porcentaje_iva = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=Decimal('16.00'),
        help_text="Porcentaje de IVA (%)"
    )
    
    class Meta:
        verbose_name = "Configuración de Pagos"
        verbose_name_plural = "Configuración de Pagos"
    
    def __str__(self):
        return "Configuración del Sistema de Pagos"
    
    def save(self, *args, **kwargs):
        # Solo permitir una instancia
        if not self.pk and ConfiguracionPagos.objects.exists():
            raise ValueError('Solo puede existir una configuración de pagos')
        super().save(*args, **kwargs)

class Pago(models.Model):
    """Registro de pagos realizados"""
    
    # Identificación
    numero_pago = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    
    # Relaciones
    pedido = models.ForeignKey(
        Pedido, 
        on_delete=models.CASCADE, 
        related_name='pagos',
        null=True, 
        blank=True
    )
    reserva = models.ForeignKey(
        Reserva, 
        on_delete=models.CASCADE, 
        related_name='pagos',
        null=True, 
        blank=True
    )
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pagos')
    
    # Información del pago
    tipo_pago = models.CharField(max_length=20, choices=TipoPago.choices, default=TipoPago.PEDIDO)
    metodo_pago = models.CharField(max_length=20, choices=MetodoPago.choices)
    estado = models.CharField(max_length=20, choices=EstadoPago.choices, default=EstadoPago.PENDIENTE)
    
    # Montos
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    impuestos = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    comision = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    descuento = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Información del procesador de pagos
    payment_intent_id = models.CharField(max_length=200, blank=True, help_text="ID del payment intent (Stripe)")
    paypal_payment_id = models.CharField(max_length=200, blank=True, help_text="ID del pago de PayPal")
    mercadopago_payment_id = models.CharField(max_length=200, blank=True, help_text="ID de MercadoPago")
    transaction_id = models.CharField(max_length=200, blank=True, help_text="ID de transacción del procesador")
    
    # Fechas
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_procesamiento = models.DateTimeField(null=True, blank=True)
    fecha_completado = models.DateTimeField(null=True, blank=True)
    fecha_vencimiento = models.DateTimeField(null=True, blank=True)
    
    # Información adicional
    descripcion = models.TextField(blank=True)
    notas_internas = models.TextField(blank=True)
    ip_cliente = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Facturación
    requiere_factura = models.BooleanField(default=False)
    datos_facturacion = models.JSONField(default=dict, blank=True)
    factura_generada = models.BooleanField(default=False)
    numero_factura = models.CharField(max_length=50, blank=True)
    
    class Meta:
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"Pago #{str(self.numero_pago)[:8]} - {self.get_metodo_pago_display()} - ${self.total}"
    
    def clean(self):
        # Al menos uno de pedido o reserva debe estar presente
        if not self.pedido and not self.reserva:
            raise ValueError('El pago debe estar asociado a un pedido o una reserva')
    
    @property
    def referencia_objeto(self):
        """Retorna el objeto asociado al pago"""
        if self.pedido:
            return self.pedido
        elif self.reserva:
            return self.reserva
        return None
    
    @property
    def numero_referencia(self):
        """Número de referencia del objeto asociado"""
        if self.pedido:
            return str(self.pedido.numero_pedido)[:8]
        elif self.reserva:
            return str(self.reserva.codigo_reserva)[:8]
        return ""
    
    @property
    def puede_reembolsar(self):
        """Verifica si el pago puede ser reembolsado"""
        return self.estado == EstadoPago.COMPLETADO and self.metodo_pago != MetodoPago.EFECTIVO
    
    @property
    def tiempo_para_vencimiento(self):
        """Tiempo restante para el vencimiento"""
        if self.fecha_vencimiento:
            return self.fecha_vencimiento - timezone.now()
        return None
    
    def marcar_procesando(self):
        """Marca el pago como procesando"""
        self.estado = EstadoPago.PROCESANDO
        self.fecha_procesamiento = timezone.now()
        self.save()
    
    def marcar_completado(self, transaction_id=None):
        """Marca el pago como completado"""
        self.estado = EstadoPago.COMPLETADO
        self.fecha_completado = timezone.now()
        if transaction_id:
            self.transaction_id = transaction_id
        self.save()
        
        # Actualizar estado del pedido/reserva
        if self.pedido:
            self.pedido.pago_completado = True
            self.pedido.save()
        
        # Generar factura si es necesario
        if self.requiere_factura and not self.factura_generada:
            self.generar_factura()
    
    def marcar_fallido(self, descripcion=""):
        """Marca el pago como fallido"""
        self.estado = EstadoPago.FALLIDO
        if descripcion:
            self.descripcion = descripcion
        self.save()
    
    def cancelar(self):
        """Cancela el pago"""
        self.estado = EstadoPago.CANCELADO
        self.save()
    
    def generar_factura(self):
        """Genera la factura para este pago"""
        try:
            # Crear número de factura
            ultimo_numero = Pago.objects.filter(
                factura_generada=True,
                numero_factura__isnull=False
            ).exclude(numero_factura='').count()
            
            self.numero_factura = f"F-{timezone.now().year}-{ultimo_numero + 1:06d}"
            self.factura_generada = True
            self.save()
            
            return True
        except Exception as e:
            print(f"Error generando factura: {e}")
            return False

class LogPago(models.Model):
    """Log de eventos del sistema de pagos"""
    
    pago = models.ForeignKey(Pago, on_delete=models.CASCADE, related_name='logs')
    evento = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True)
    datos_adicionales = models.JSONField(default=dict, blank=True)
    fecha_evento = models.DateTimeField(auto_now_add=True)
    ip_origen = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Log de Pago"
        verbose_name_plural = "Logs de Pagos"
        ordering = ['-fecha_evento']
    
    def __str__(self):
        return f"Log {self.evento} - Pago #{str(self.pago.numero_pago)[:8]}"

class Reembolso(models.Model):
    """Reembolsos procesados"""
    
    pago_original = models.ForeignKey(Pago, on_delete=models.CASCADE, related_name='reembolsos')
    numero_reembolso = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    
    monto_reembolsado = models.DecimalField(max_digits=10, decimal_places=2)
    motivo = models.TextField()
    estado = models.CharField(
        max_length=20,
        choices=[
            ('pendiente', 'Pendiente'),
            ('procesando', 'Procesando'),
            ('completado', 'Completado'),
            ('fallido', 'Fallido'),
        ],
        default='pendiente'
    )
    
    # Información del procesador
    refund_id = models.CharField(max_length=200, blank=True)
    
    # Usuario que procesó el reembolso
    procesado_por = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='reembolsos_procesados'
    )
    
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_procesamiento = models.DateTimeField(null=True, blank=True)
    fecha_completado = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Reembolso"
        verbose_name_plural = "Reembolsos"
        ordering = ['-fecha_solicitud']
    
    def __str__(self):
        return f"Reembolso #{str(self.numero_reembolso)[:8]} - ${self.monto_reembolsado}"

class Factura(models.Model):
    """Facturas generadas"""
    
    pago = models.OneToOneField(Pago, on_delete=models.CASCADE, related_name='factura')
    numero_factura = models.CharField(max_length=50, unique=True)
    
    # Datos del cliente
    cliente_nombre = models.CharField(max_length=200)
    cliente_email = models.EmailField(blank=True)
    cliente_telefono = models.CharField(max_length=15, blank=True)
    cliente_direccion = models.TextField(blank=True)
    cliente_rfc_cuit = models.CharField(max_length=20, blank=True)
    
    # Datos de la empresa
    empresa_nombre = models.CharField(max_length=200)
    empresa_rfc_cuit = models.CharField(max_length=20, blank=True)
    empresa_direccion = models.TextField(blank=True)
    
    # Montos
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    iva = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Detalles
    items_factura = models.JSONField(default=list)
    notas = models.TextField(blank=True)
    
    fecha_emision = models.DateTimeField(auto_now_add=True)
    fecha_vencimiento = models.DateField(null=True, blank=True)
    
    # Control
    enviada_por_email = models.BooleanField(default=False)
    fecha_envio_email = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Factura"
        verbose_name_plural = "Facturas"
        ordering = ['-fecha_emision']
    
    def __str__(self):
        return f"Factura {self.numero_factura} - {self.cliente_nombre}"
    
    def enviar_por_email(self):
        """Envía la factura por email al cliente"""
        try:
            # Aquí implementarías la lógica de envío de email
            # Por ahora solo marcamos como enviada
            self.enviada_por_email = True
            self.fecha_envio_email = timezone.now()
            self.save()
            return True
        except Exception as e:
            print(f"Error enviando factura: {e}")
            return False
