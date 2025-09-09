from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal
from menu.models import Ingrediente, PlatoMenu
import uuid

User = get_user_model()

class UnidadMedida(models.TextChoices):
    """Unidades de medida para ingredientes"""
    KILOGRAMOS = 'kg', 'Kilogramos'
    GRAMOS = 'g', 'Gramos'
    LITROS = 'l', 'Litros'
    MILILITROS = 'ml', 'Mililitros'
    UNIDADES = 'unidades', 'Unidades'
    PIEZAS = 'piezas', 'Piezas'
    CAJAS = 'cajas', 'Cajas'
    BOLSAS = 'bolsas', 'Bolsas'
    LATAS = 'latas', 'Latas'

class TipoMovimiento(models.TextChoices):
    """Tipos de movimiento de inventario"""
    ENTRADA = 'entrada', 'Entrada'
    SALIDA = 'salida', 'Salida'
    AJUSTE = 'ajuste', 'Ajuste'
    MERMA = 'merma', 'Merma'
    DEVOLUCION = 'devolucion', 'Devolución'

class EstadoOrden(models.TextChoices):
    """Estados de órdenes de compra"""
    BORRADOR = 'borrador', 'Borrador'
    ENVIADA = 'enviada', 'Enviada'
    CONFIRMADA = 'confirmada', 'Confirmada'
    RECIBIDA = 'recibida', 'Recibida'
    CANCELADA = 'cancelada', 'Cancelada'

class Proveedor(models.Model):
    """Proveedores de ingredientes"""
    
    nombre = models.CharField(max_length=200)
    empresa = models.CharField(max_length=200, blank=True)
    email = models.EmailField(blank=True)
    telefono = models.CharField(max_length=15, blank=True)
    direccion = models.TextField(blank=True)
    ciudad = models.CharField(max_length=100, blank=True)
    codigo_postal = models.CharField(max_length=10, blank=True)
    
    # Información fiscal
    rfc_cuit = models.CharField(max_length=20, blank=True, verbose_name="RFC/CUIT")
    razon_social = models.CharField(max_length=200, blank=True)
    
    # Información comercial
    dias_entrega = models.PositiveIntegerField(default=3, help_text="Días promedio de entrega")
    monto_minimo_pedido = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        help_text="Monto mínimo para realizar pedido"
    )
    descuento_volumen = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0,
        help_text="Descuento por volumen (%)"
    )
    
    # Control
    activo = models.BooleanField(default=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    notas = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.nombre} - {self.empresa}" if self.empresa else self.nombre
    
    @property
    def total_ordenes(self):
        """Total de órdenes de compra"""
        return self.ordenes_compra.count()
    
    @property
    def monto_total_compras(self):
        """Monto total de compras realizadas"""
        return self.ordenes_compra.filter(
            estado=EstadoOrden.RECIBIDA
        ).aggregate(
            total=models.Sum('total')
        )['total'] or Decimal('0')

class CategoriaInventario(models.Model):
    """Categorías para organizar el inventario"""
    
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#6c757d', help_text="Color en formato hexadecimal")
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Categoría de Inventario"
        verbose_name_plural = "Categorías de Inventario"
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre

class ProductoInventario(models.Model):
    """Productos en inventario (extensión de ingredientes)"""
    
    ingrediente = models.OneToOneField(
        Ingrediente, 
        on_delete=models.CASCADE, 
        related_name='producto_inventario'
    )
    categoria_inventario = models.ForeignKey(
        CategoriaInventario, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='productos'
    )
    
    # Información básica de inventario
    codigo_producto = models.CharField(max_length=50, unique=True, blank=True)
    unidad_medida = models.CharField(max_length=20, choices=UnidadMedida.choices)
    
    # Stock
    stock_actual = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0)]
    )
    stock_minimo = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        help_text="Cantidad mínima antes de alerta"
    )
    stock_maximo = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        help_text="Cantidad máxima recomendada"
    )
    
    # Costos
    costo_unitario = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        help_text="Costo por unidad de medida"
    )
    precio_promedio = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        help_text="Precio promedio ponderado"
    )
    
    # Fechas de vencimiento
    dias_vencimiento = models.PositiveIntegerField(
        null=True, 
        blank=True,
        help_text="Días promedio hasta vencimiento"
    )
    
    # Proveedor principal
    proveedor_principal = models.ForeignKey(
        Proveedor, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='productos_principales'
    )
    
    # Control
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Producto en Inventario"
        verbose_name_plural = "Productos en Inventario"
        ordering = ['ingrediente__nombre']
    
    def __str__(self):
        return f"{self.ingrediente.nombre} ({self.stock_actual} {self.get_unidad_medida_display()})"
    
    def save(self, *args, **kwargs):
        # Generar código de producto si no existe
        if not self.codigo_producto:
            self.codigo_producto = f"INV-{self.ingrediente.id:04d}"
        super().save(*args, **kwargs)
    
    @property
    def necesita_reposicion(self):
        """Verifica si necesita reposición"""
        return self.stock_actual <= self.stock_minimo
    
    @property
    def nivel_stock(self):
        """Nivel de stock: bajo, medio, alto"""
        if self.stock_actual <= self.stock_minimo:
            return 'bajo'
        elif self.stock_actual >= self.stock_maximo:
            return 'alto'
        return 'medio'
    
    @property
    def valor_total_stock(self):
        """Valor total del stock actual"""
        return self.stock_actual * self.costo_unitario
    
    @property
    def rotacion_mensual(self):
        """Cálculo de rotación mensual promedio"""
        from django.utils import timezone
        fecha_inicio = timezone.now() - timezone.timedelta(days=30)
        
        salidas = MovimientoInventario.objects.filter(
            producto=self,
            tipo_movimiento=TipoMovimiento.SALIDA,
            fecha__gte=fecha_inicio
        ).aggregate(
            total=models.Sum('cantidad')
        )['total'] or Decimal('0')
        
        return salidas

class MovimientoInventario(models.Model):
    """Registro de movimientos de inventario"""
    
    numero_movimiento = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    producto = models.ForeignKey(
        ProductoInventario, 
        on_delete=models.CASCADE, 
        related_name='movimientos'
    )
    
    # Información del movimiento
    tipo_movimiento = models.CharField(max_length=20, choices=TipoMovimiento.choices)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    costo_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Stock antes y después
    stock_anterior = models.DecimalField(max_digits=10, decimal_places=2)
    stock_nuevo = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Información adicional
    motivo = models.CharField(max_length=200, blank=True)
    referencia = models.CharField(max_length=100, blank=True, help_text="Orden de compra, pedido, etc.")
    lote = models.CharField(max_length=50, blank=True)
    fecha_vencimiento = models.DateField(null=True, blank=True)
    
    # Usuario y fechas
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='movimientos_inventario')
    fecha = models.DateTimeField(default=timezone.now)
    
    class Meta:
        verbose_name = "Movimiento de Inventario"
        verbose_name_plural = "Movimientos de Inventario"
        ordering = ['-fecha']
    
    def __str__(self):
        signo = '+' if self.tipo_movimiento == TipoMovimiento.ENTRADA else '-'
        return f"{signo}{self.cantidad} {self.producto.ingrediente.nombre} - {self.get_tipo_movimiento_display()}"
    
    @property
    def valor_total(self):
        """Valor total del movimiento"""
        return self.cantidad * self.costo_unitario

class OrdenCompra(models.Model):
    """Órdenes de compra a proveedores"""
    
    numero_orden = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, related_name='ordenes_compra')
    
    # Estados y fechas
    estado = models.CharField(max_length=20, choices=EstadoOrden.choices, default=EstadoOrden.BORRADOR)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_envio = models.DateTimeField(null=True, blank=True)
    fecha_entrega_estimada = models.DateField(null=True, blank=True)
    fecha_entrega_real = models.DateTimeField(null=True, blank=True)
    
    # Montos
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    descuento = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    impuestos = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Usuario que creó la orden
    creado_por = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ordenes_creadas')
    
    # Información adicional
    notas = models.TextField(blank=True)
    terminos_condiciones = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Orden de Compra"
        verbose_name_plural = "Órdenes de Compra"
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"OC-{str(self.numero_orden)[:8]} - {self.proveedor.nombre}"
    
    def calcular_totales(self):
        """Calcula los totales de la orden"""
        items = self.items.all()
        self.subtotal = sum(item.total for item in items)
        self.total = self.subtotal - self.descuento + self.impuestos
        self.save()
    
    def enviar(self):
        """Marca la orden como enviada"""
        if self.estado == EstadoOrden.BORRADOR:
            self.estado = EstadoOrden.ENVIADA
            self.fecha_envio = timezone.now()
            # Calcular fecha estimada de entrega
            self.fecha_entrega_estimada = (
                timezone.now().date() + 
                timezone.timedelta(days=self.proveedor.dias_entrega)
            )
            self.save()
    
    def confirmar(self):
        """Confirma la orden (el proveedor la acepta)"""
        if self.estado == EstadoOrden.ENVIADA:
            self.estado = EstadoOrden.CONFIRMADA
            self.save()
    
    def recibir(self):
        """Marca la orden como recibida"""
        if self.estado == EstadoOrden.CONFIRMADA:
            self.estado = EstadoOrden.RECIBIDA
            self.fecha_entrega_real = timezone.now()
            self.save()
            
            # Crear movimientos de entrada en inventario
            for item in self.items.all():
                MovimientoInventario.objects.create(
                    producto=item.producto,
                    tipo_movimiento=TipoMovimiento.ENTRADA,
                    cantidad=item.cantidad,
                    costo_unitario=item.precio_unitario,
                    stock_anterior=item.producto.stock_actual,
                    stock_nuevo=item.producto.stock_actual + item.cantidad,
                    motivo=f"Orden de compra {str(self.numero_orden)[:8]}",
                    referencia=str(self.numero_orden),
                    usuario=self.creado_por,
                    fecha_vencimiento=item.fecha_vencimiento
                )
                
                # Actualizar stock del producto
                item.producto.stock_actual += item.cantidad
                item.producto.save()
    
    @property
    def puede_enviar(self):
        return self.estado == EstadoOrden.BORRADOR and self.items.exists()
    
    @property
    def puede_confirmar(self):
        return self.estado == EstadoOrden.ENVIADA
    
    @property
    def puede_recibir(self):
        return self.estado == EstadoOrden.CONFIRMADA

class ItemOrdenCompra(models.Model):
    """Items de una orden de compra"""
    
    orden = models.ForeignKey(OrdenCompra, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(ProductoInventario, on_delete=models.CASCADE)
    
    # Cantidades y precios
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Información adicional
    descripcion = models.CharField(max_length=200, blank=True)
    fecha_vencimiento = models.DateField(null=True, blank=True)
    lote = models.CharField(max_length=50, blank=True)
    
    class Meta:
        verbose_name = "Item de Orden de Compra"
        verbose_name_plural = "Items de Órdenes de Compra"
        unique_together = ['orden', 'producto']
    
    def __str__(self):
        return f"{self.cantidad} x {self.producto.ingrediente.nombre}"
    
    @property
    def total(self):
        """Total del item"""
        return self.cantidad * self.precio_unitario

class AlertaInventario(models.Model):
    """Alertas automáticas de inventario"""
    
    TIPOS_ALERTA = [
        ('stock_bajo', 'Stock Bajo'),
        ('stock_agotado', 'Stock Agotado'),
        ('vencimiento_proximo', 'Vencimiento Próximo'),
        ('vencimiento_hoy', 'Vence Hoy'),
        ('producto_vencido', 'Producto Vencido'),
        ('rotacion_baja', 'Rotación Baja'),
    ]
    
    producto = models.ForeignKey(ProductoInventario, on_delete=models.CASCADE, related_name='alertas')
    tipo_alerta = models.CharField(max_length=20, choices=TIPOS_ALERTA)
    mensaje = models.TextField()
    activa = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_resolucion = models.DateTimeField(null=True, blank=True)
    resuelto_por = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='alertas_resueltas'
    )
    
    class Meta:
        verbose_name = "Alerta de Inventario"
        verbose_name_plural = "Alertas de Inventario"
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"{self.get_tipo_alerta_display()} - {self.producto.ingrediente.nombre}"
    
    def resolver(self, usuario):
        """Marca la alerta como resuelta"""
        self.activa = False
        self.fecha_resolucion = timezone.now()
        self.resuelto_por = usuario
        self.save()

class RecetaConsumo(models.Model):
    """Relación entre platos y consumo de ingredientes"""
    
    plato = models.ForeignKey(PlatoMenu, on_delete=models.CASCADE, related_name='consumos_ingredientes')
    producto = models.ForeignKey(ProductoInventario, on_delete=models.CASCADE, related_name='consumos_platos')
    cantidad_necesaria = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Cantidad del ingrediente necesaria para preparar una porción del plato"
    )
    
    class Meta:
        verbose_name = "Consumo de Ingrediente por Receta"
        verbose_name_plural = "Consumos de Ingredientes por Recetas"
        unique_together = ['plato', 'producto']
    
    def __str__(self):
        return f"{self.plato.nombre} - {self.cantidad_necesaria} {self.producto.get_unidad_medida_display()} de {self.producto.ingrediente.nombre}"
