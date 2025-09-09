from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from menu.models import PlatoMenu, OpcionPersonalizacion
from decimal import Decimal
import uuid

User = get_user_model()

class CarritoCompras(models.Model):
    """Carrito de compras del usuario"""
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carritos')
    session_key = models.CharField(max_length=40, blank=True, null=True, help_text="Para usuarios no autenticados")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Carrito de Compras"
        verbose_name_plural = "Carritos de Compras"
        ordering = ['-fecha_actualizacion']
    
    def __str__(self):
        if self.usuario:
            return f"Carrito de {self.usuario.username}"
        return f"Carrito anónimo {self.session_key}"
    
    @property
    def total_items(self):
        """Total de items en el carrito"""
        return sum(item.cantidad for item in self.items.all())
    
    @property
    def subtotal(self):
        """Subtotal sin impuestos ni delivery"""
        return sum(item.total for item in self.items.all())
    
    @property
    def total_impuestos(self):
        """Impuestos (ejemplo: 10%)"""
        return self.subtotal * Decimal('0.10')
    
    @property
    def costo_delivery(self):
        """Costo de delivery"""
        if self.subtotal >= 50:  # Delivery gratis por compras mayores a $50
            return Decimal('0.00')
        return Decimal('5.00')
    
    @property
    def total_final(self):
        """Total final a pagar"""
        return self.subtotal + self.total_impuestos + self.costo_delivery
    
    def limpiar_carrito(self):
        """Limpia todos los items del carrito"""
        self.items.all().delete()

class ItemCarrito(models.Model):
    """Item individual en el carrito"""
    
    carrito = models.ForeignKey(CarritoCompras, on_delete=models.CASCADE, related_name='items')
    plato = models.ForeignKey(PlatoMenu, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    precio_unitario = models.DecimalField(
        max_digits=8, 
        decimal_places=2,
        help_text="Precio del plato al momento de agregarlo al carrito"
    )
    opciones_personalizacion = models.ManyToManyField(
        OpcionPersonalizacion, 
        blank=True,
        related_name='items_carrito'
    )
    instrucciones_especiales = models.TextField(
        blank=True,
        max_length=500,
        help_text="Instrucciones especiales para la preparación"
    )
    fecha_agregado = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Item del Carrito"
        verbose_name_plural = "Items del Carrito"
        ordering = ['fecha_agregado']
        unique_together = ['carrito', 'plato']  # Un plato por carrito (se aumenta cantidad)
    
    def __str__(self):
        return f"{self.cantidad}x {self.plato.nombre}"
    
    @property
    def precio_opciones(self):
        """Precio total de las opciones de personalización"""
        return sum(opcion.precio_adicional for opcion in self.opciones_personalizacion.all())
    
    @property
    def precio_total_unitario(self):
        """Precio unitario incluyendo opciones"""
        return self.precio_unitario + self.precio_opciones
    
    @property
    def total(self):
        """Total para este item (precio unitario + opciones) * cantidad"""
        return self.precio_total_unitario * self.cantidad

class EstadoPedido(models.TextChoices):
    """Estados posibles de un pedido"""
    PENDIENTE = 'pendiente', 'Pendiente'
    CONFIRMADO = 'confirmado', 'Confirmado'
    EN_PREPARACION = 'en_preparacion', 'En Preparación'
    LISTO = 'listo', 'Listo'
    EN_CAMINO = 'en_camino', 'En Camino'
    ENTREGADO = 'entregado', 'Entregado'
    CANCELADO = 'cancelado', 'Cancelado'

class TipoEntrega(models.TextChoices):
    """Tipos de entrega"""
    DELIVERY = 'delivery', 'Delivery'
    RECOGIDA = 'recogida', 'Recogida en local'
    MESA = 'mesa', 'Servicio en mesa'

class Pedido(models.Model):
    """Pedido realizado por un cliente"""
    
    # Identificación
    numero_pedido = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pedidos')
    
    # Estado y tipo
    estado = models.CharField(
        max_length=20,
        choices=EstadoPedido.choices,
        default=EstadoPedido.PENDIENTE
    )
    tipo_entrega = models.CharField(
        max_length=20,
        choices=TipoEntrega.choices,
        default=TipoEntrega.DELIVERY
    )
    
    # Información de entrega
    direccion_entrega = models.TextField(blank=True, null=True)
    telefono_contacto = models.CharField(max_length=15)
    notas_entrega = models.TextField(blank=True, max_length=500)
    numero_mesa = models.PositiveIntegerField(blank=True, null=True)
    
    # Precios
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    impuestos = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    costo_delivery = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Tiempos
    fecha_pedido = models.DateTimeField(auto_now_add=True)
    tiempo_estimado_preparacion = models.PositiveIntegerField(
        help_text="Tiempo estimado en minutos",
        default=30
    )
    fecha_confirmacion = models.DateTimeField(blank=True, null=True)
    fecha_listo = models.DateTimeField(blank=True, null=True)
    fecha_entrega = models.DateTimeField(blank=True, null=True)
    
    # Método de pago
    metodo_pago = models.CharField(
        max_length=20,
        choices=[
            ('efectivo', 'Efectivo'),
            ('tarjeta', 'Tarjeta de Crédito/Débito'),
            ('transferencia', 'Transferencia Bancaria'),
            ('online', 'Pago Online'),
        ],
        default='efectivo'
    )
    pago_completado = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        ordering = ['-fecha_pedido']
    
    def __str__(self):
        return f"Pedido #{str(self.numero_pedido)[:8]} - {self.usuario.username}"
    
    @property
    def tiempo_restante_estimado(self):
        """Tiempo restante estimado en minutos"""
        if self.estado in [EstadoPedido.ENTREGADO, EstadoPedido.CANCELADO]:
            return 0
        
        tiempo_transcurrido = timezone.now() - self.fecha_pedido
        tiempo_transcurrido_minutos = tiempo_transcurrido.total_seconds() / 60
        tiempo_restante = max(0, self.tiempo_estimado_preparacion - tiempo_transcurrido_minutos)
        return int(tiempo_restante)
    
    @property
    def puede_cancelar(self):
        """Verifica si el pedido puede ser cancelado"""
        return self.estado in [EstadoPedido.PENDIENTE, EstadoPedido.CONFIRMADO]
    
    def confirmar_pedido(self):
        """Confirma el pedido"""
        self.estado = EstadoPedido.CONFIRMADO
        self.fecha_confirmacion = timezone.now()
        self.save()
    
    def marcar_en_preparacion(self):
        """Marca el pedido como en preparación"""
        self.estado = EstadoPedido.EN_PREPARACION
        self.save()
    
    def marcar_listo(self):
        """Marca el pedido como listo"""
        self.estado = EstadoPedido.LISTO
        self.fecha_listo = timezone.now()
        self.save()
    
    def marcar_entregado(self):
        """Marca el pedido como entregado"""
        self.estado = EstadoPedido.ENTREGADO
        self.fecha_entrega = timezone.now()
        self.save()
    
    def cancelar_pedido(self):
        """Cancela el pedido"""
        if self.puede_cancelar:
            self.estado = EstadoPedido.CANCELADO
            self.save()
            return True
        return False

class ItemPedido(models.Model):
    """Item individual de un pedido"""
    
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='items')
    plato = models.ForeignKey(PlatoMenu, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=8, decimal_places=2)
    precio_opciones = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    opciones_seleccionadas = models.JSONField(
        default=list,
        help_text="Lista de opciones de personalización seleccionadas"
    )
    instrucciones_especiales = models.TextField(blank=True, max_length=500)
    
    class Meta:
        verbose_name = "Item del Pedido"
        verbose_name_plural = "Items del Pedido"
        ordering = ['id']
    
    def __str__(self):
        return f"{self.cantidad}x {self.plato.nombre}"
    
    @property
    def total(self):
        """Total para este item"""
        return (self.precio_unitario + self.precio_opciones) * self.cantidad

class SeguimientoPedido(models.Model):
    """Historial de cambios de estado del pedido"""
    
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='seguimiento')
    estado_anterior = models.CharField(max_length=20, choices=EstadoPedido.choices)
    estado_nuevo = models.CharField(max_length=20, choices=EstadoPedido.choices)
    fecha_cambio = models.DateTimeField(auto_now_add=True)
    usuario_responsable = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Usuario que realizó el cambio de estado"
    )
    comentario = models.TextField(blank=True, max_length=200)
    
    class Meta:
        verbose_name = "Seguimiento de Pedido"
        verbose_name_plural = "Seguimientos de Pedidos"
        ordering = ['-fecha_cambio']
    
    def __str__(self):
        return f"Pedido #{str(self.pedido.numero_pedido)[:8]} - {self.estado_anterior} → {self.estado_nuevo}"
