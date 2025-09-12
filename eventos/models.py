from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal
from config.media_settings import validate_evento_image

Usuario = get_user_model()

class TipoEvento(models.Model):
    """Tipos de eventos disponibles"""
    
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio_base = models.DecimalField(max_digits=10, decimal_places=2)
    capacidad_minima = models.PositiveIntegerField(default=10)
    capacidad_maxima = models.PositiveIntegerField(default=100)
    duracion_estimada = models.PositiveIntegerField(help_text="Duración en horas")
    imagen = models.ImageField(upload_to='eventos/tipos/', blank=True, null=True, help_text="Imagen representativa del tipo de evento")
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Tipo de Evento"
        verbose_name_plural = "Tipos de Eventos"
    
    def __str__(self):
        return self.nombre

class ServicioAdicional(models.Model):
    """Servicios adicionales para eventos"""
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    precio_por_persona = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Servicio Adicional"
        verbose_name_plural = "Servicios Adicionales"
    
    def __str__(self):
        return self.nombre

class MenuEvento(models.Model):
    """Menús especiales para eventos"""
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio_por_persona = models.DecimalField(max_digits=10, decimal_places=2)
    platos = models.TextField(help_text="Lista de platos incluidos")
    imagen = models.ImageField(upload_to='eventos/menus/', blank=True, null=True, help_text="Imagen del menú")
    bebidas_incluidas = models.BooleanField(default=False)
    postre_incluido = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Menú de Evento"
        verbose_name_plural = "Menús de Eventos"
    
    def __str__(self):
        return self.nombre

class Evento(models.Model):
    """Modelo principal para eventos"""
    ESTADOS_EVENTO = [
        ('solicitado', 'Solicitado'),
        ('confirmado', 'Confirmado'),
        ('en_preparacion', 'En Preparación'),
        ('en_curso', 'En Curso'),
        ('completado', 'Completado'),
        ('cancelado', 'Cancelado'),
    ]
    
    TIPOS_EVENTO = [
        ('evento_social', 'Evento Social'),
        ('evento_corporativo', 'Evento Corporativo'),
        ('catering', 'Catering'),
        ('celebracion', 'Celebración Especial'),
    ]
    
    # Información básica
    cliente = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='eventos')
    tipo_evento = models.ForeignKey(TipoEvento, on_delete=models.PROTECT)
    menu_evento = models.ForeignKey(MenuEvento, on_delete=models.PROTECT, null=True, blank=True)
    nombre_evento = models.CharField(max_length=200)
    descripcion = models.TextField()
    
    # Fechas y horarios
    fecha_evento = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    
    # Ubicación
    tipo_ubicacion = models.CharField(max_length=50, choices=[
        ('restaurante', 'En el Restaurante'),
        ('domicilio', 'En Domicilio'),
        ('exterior', 'Lugar Exterior'),
    ])
    direccion_evento = models.TextField(blank=True)
    instrucciones_ubicacion = models.TextField(blank=True)
    
    # Capacidad y asistencia
    numero_invitados = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    numero_confirmados = models.PositiveIntegerField(default=0)
    
    # Servicios adicionales
    servicios_adicionales = models.ManyToManyField(ServicioAdicional, blank=True)
    decoracion_especial = models.TextField(blank=True)
    musica_especial = models.BooleanField(default=False)
    fotografo = models.BooleanField(default=False)
    
    # Estado y seguimiento
    estado = models.CharField(max_length=20, choices=ESTADOS_EVENTO, default='solicitado')
    categoria = models.CharField(max_length=20, choices=TIPOS_EVENTO)
    
    # Costos
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    descuento = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Información adicional
    notas_especiales = models.TextField(blank=True)
    alergias_especiales = models.TextField(blank=True)
    preferencias_dieteticas = models.TextField(blank=True)
    
    # Timestamps
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Evento"
        verbose_name_plural = "Eventos"
        ordering = ['-fecha_evento', '-hora_inicio']
    
    def __str__(self):
        return f"{self.nombre_evento} - {self.cliente.get_full_name()} - {self.fecha_evento}"
    
    def calcular_total(self):
        """Calcula el total del evento"""
        # Precio base del tipo de evento
        total = self.tipo_evento.precio_base
        
        # Agregar costo del menú por persona
        if self.menu_evento:
            total += self.menu_evento.precio_por_persona * self.numero_invitados
        
        # Agregar servicios adicionales (solo si el objeto ya está guardado)
        if self.pk:
            for servicio in self.servicios_adicionales.all():
                if servicio.precio_por_persona:
                    total += servicio.precio * self.numero_invitados
                else:
                    total += servicio.precio
        
        # Aplicar descuento
        total -= self.descuento
        
        return max(total, Decimal('0'))
    
    def save(self, *args, **kwargs):
        self.total = self.calcular_total()
        super().save(*args, **kwargs)

class CotizacionEvento(models.Model):
    """Cotizaciones para eventos"""
    ESTADOS_COTIZACION = [
        ('pendiente', 'Pendiente'),
        ('enviada', 'Enviada'),
        ('aceptada', 'Aceptada'),
        ('rechazada', 'Rechazada'),
        ('expirada', 'Expirada'),
    ]
    
    evento = models.OneToOneField(Evento, on_delete=models.CASCADE)
    estado = models.CharField(max_length=20, choices=ESTADOS_COTIZACION, default='pendiente')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_expiracion = models.DateTimeField()
    fecha_respuesta = models.DateTimeField(null=True, blank=True)
    
    # Detalles de la cotización
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    descuento = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Notas
    notas_cliente = models.TextField(blank=True)
    notas_internas = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Cotización de Evento"
        verbose_name_plural = "Cotizaciones de Eventos"
    
    def __str__(self):
        return f"Cotización {self.evento.nombre_evento} - {self.estado}"
    
    def esta_expirada(self):
        return timezone.now() > self.fecha_expiracion

class Catering(models.Model):
    """Servicios de catering específicos"""
    TIPOS_CATERING = [
        ('empresarial', 'Catering Empresarial'),
        ('social', 'Catering Social'),
        ('institucional', 'Catering Institucional'),
        ('especial', 'Catering Especial'),
    ]
    
    evento = models.OneToOneField(Evento, on_delete=models.CASCADE)
    tipo_catering = models.CharField(max_length=20, choices=TIPOS_CATERING)
    
    # Detalles específicos del catering
    incluye_servicio_mesa = models.BooleanField(default=True)
    incluye_equipamiento = models.BooleanField(default=False)
    incluye_personal = models.BooleanField(default=False)
    
    # Personal requerido
    numero_meseros = models.PositiveIntegerField(default=0)
    numero_chefs = models.PositiveIntegerField(default=0)
    
    # Equipamiento
    equipamiento_requerido = models.TextField(blank=True)
    mesas_sillas = models.BooleanField(default=False)
    manteleria = models.BooleanField(default=False)
    vajilla = models.BooleanField(default=False)
    
    # Horarios de servicio
    hora_entrega = models.TimeField()
    hora_recogida = models.TimeField()
    
    class Meta:
        verbose_name = "Catering"
        verbose_name_plural = "Catering"
    
    def __str__(self):
        return f"Catering {self.evento.nombre_evento} - {self.tipo_catering}"

class PresupuestoEvento(models.Model):
    """Presupuestos detallados para eventos"""
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name='presupuestos')
    version = models.PositiveIntegerField(default=1)
    
    # Desglose de costos
    costo_menu = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    costo_servicios = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    costo_decoracion = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    costo_personal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    costo_equipamiento = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    costo_transporte = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Totales
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    impuestos = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    descuento = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Información adicional
    notas = models.TextField(blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    aprobado = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Presupuesto de Evento"
        verbose_name_plural = "Presupuestos de Eventos"
        unique_together = ['evento', 'version']
    
    def __str__(self):
        return f"Presupuesto v{self.version} - {self.evento.nombre_evento}"
