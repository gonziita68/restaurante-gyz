from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
import uuid

User = get_user_model()

class ConfiguracionRestaurante(models.Model):
    """Configuración general del restaurante para reservas"""
    
    nombre = models.CharField(max_length=200, default="Restaurante GYZ")
    hora_apertura = models.TimeField(default="12:00")
    hora_cierre = models.TimeField(default="22:00")
    duracion_turno_minutos = models.PositiveIntegerField(
        default=120, 
        help_text="Duración de cada turno en minutos"
    )
    tiempo_minimo_reserva_horas = models.PositiveIntegerField(
        default=2,
        help_text="Horas mínimas de anticipación para reservar"
    )
    tiempo_maximo_reserva_dias = models.PositiveIntegerField(
        default=30,
        help_text="Días máximos de anticipación para reservar"
    )
    dias_cerrado = models.CharField(
        max_length=20,
        blank=True,
        help_text="Días de la semana cerrado (ej: lunes,martes)"
    )
    telefono_contacto = models.CharField(max_length=15, blank=True)
    email_contacto = models.EmailField(blank=True)
    permite_cancelacion_horas = models.PositiveIntegerField(
        default=4,
        help_text="Horas mínimas antes de la reserva para poder cancelar"
    )
    
    class Meta:
        verbose_name = "Configuración del Restaurante"
        verbose_name_plural = "Configuración del Restaurante"
    
    def __str__(self):
        return self.nombre
    
    def save(self, *args, **kwargs):
        # Solo permitir una instancia de configuración
        if not self.pk and ConfiguracionRestaurante.objects.exists():
            raise ValidationError('Solo puede existir una configuración del restaurante')
        super().save(*args, **kwargs)

class TipoMesa(models.Model):
    """Tipos de mesa disponibles en el restaurante"""
    
    nombre = models.CharField(max_length=100, unique=True)
    capacidad_minima = models.PositiveIntegerField()
    capacidad_maxima = models.PositiveIntegerField()
    descripcion = models.TextField(blank=True)
    precio_base = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        default=0,
        help_text="Precio base por reserva (si aplica)"
    )
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Tipo de Mesa"
        verbose_name_plural = "Tipos de Mesa"
        ordering = ['capacidad_minima']
    
    def __str__(self):
        return f"{self.nombre} ({self.capacidad_minima}-{self.capacidad_maxima} personas)"
    
    def clean(self):
        if self.capacidad_minima > self.capacidad_maxima:
            raise ValidationError('La capacidad mínima no puede ser mayor que la máxima')

class Mesa(models.Model):
    """Mesas físicas del restaurante"""
    
    numero = models.CharField(max_length=10, unique=True)
    tipo_mesa = models.ForeignKey(TipoMesa, on_delete=models.CASCADE, related_name='mesas')
    ubicacion = models.CharField(
        max_length=50,
        choices=[
            ('interior', 'Interior'),
            ('terraza', 'Terraza'),
            ('ventana', 'Junto a ventana'),
            ('privado', 'Área privada'),
            ('barra', 'Barra'),
        ],
        default='interior'
    )
    descripcion = models.TextField(blank=True)
    activa = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Mesa"
        verbose_name_plural = "Mesas"
        ordering = ['numero']
    
    def __str__(self):
        return f"Mesa {self.numero} - {self.tipo_mesa.nombre}"
    
    @property
    def capacidad_maxima(self):
        return self.tipo_mesa.capacidad_maxima
    
    @property
    def capacidad_minima(self):
        return self.tipo_mesa.capacidad_minima

class EstadoReserva(models.TextChoices):
    """Estados posibles de una reserva"""
    PENDIENTE = 'pendiente', 'Pendiente'
    CONFIRMADA = 'confirmada', 'Confirmada'
    EN_CURSO = 'en_curso', 'En Curso'
    COMPLETADA = 'completada', 'Completada'
    CANCELADA = 'cancelada', 'Cancelada'
    NO_SHOW = 'no_show', 'No Show'

class Reserva(models.Model):
    """Reserva de mesa realizada por un cliente"""
    
    # Identificación
    codigo_reserva = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    usuario = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='reservas',
        null=True,
        blank=True,
        help_text="Usuario que realizó la reserva (puede ser null para reservas telefónicas)"
    )
    
    # Información del cliente
    nombre_cliente = models.CharField(max_length=100)
    telefono_cliente = models.CharField(max_length=15)
    email_cliente = models.EmailField(blank=True)
    
    # Detalles de la reserva
    mesa = models.ForeignKey(Mesa, on_delete=models.CASCADE, related_name='reservas')
    fecha_reserva = models.DateField()
    hora_reserva = models.TimeField()
    numero_comensales = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(20)]
    )
    duracion_estimada = models.PositiveIntegerField(
        default=120,
        help_text="Duración estimada en minutos"
    )
    
    # Estado y gestión
    estado = models.CharField(
        max_length=20,
        choices=EstadoReserva.choices,
        default=EstadoReserva.PENDIENTE
    )
    
    # Información adicional
    ocasion_especial = models.CharField(
        max_length=50,
        choices=[
            ('', 'Ninguna'),
            ('cumpleanos', 'Cumpleaños'),
            ('aniversario', 'Aniversario'),
            ('cita', 'Cita romántica'),
            ('negocios', 'Comida de negocios'),
            ('celebracion', 'Celebración'),
            ('otro', 'Otro'),
        ],
        blank=True
    )
    solicitudes_especiales = models.TextField(
        blank=True,
        max_length=500,
        help_text="Solicitudes especiales del cliente"
    )
    
    # Preferencias
    preferencia_ubicacion = models.CharField(
        max_length=50,
        choices=[
            ('cualquiera', 'Cualquiera'),
            ('ventana', 'Junto a ventana'),
            ('tranquilo', 'Área tranquila'),
            ('animado', 'Área animada'),
        ],
        default='cualquiera'
    )
    
    # Fechas de control
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_confirmacion = models.DateTimeField(null=True, blank=True)
    fecha_llegada = models.DateTimeField(null=True, blank=True)
    fecha_salida = models.DateTimeField(null=True, blank=True)
    fecha_cancelacion = models.DateTimeField(null=True, blank=True)
    
    # Personal responsable
    usuario_confirmacion = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reservas_confirmadas',
        help_text="Usuario del staff que confirmó la reserva"
    )
    
    # Notas internas
    notas_internas = models.TextField(blank=True, help_text="Notas para el personal")
    
    class Meta:
        verbose_name = "Reserva"
        verbose_name_plural = "Reservas"
        ordering = ['-fecha_reserva', '-hora_reserva']
        unique_together = ['mesa', 'fecha_reserva', 'hora_reserva']
    
    def __str__(self):
        return f"Reserva {str(self.codigo_reserva)[:8]} - {self.nombre_cliente} - {self.fecha_reserva} {self.hora_reserva}"
    
    def clean(self):
        # Validar que la fecha no sea en el pasado
        if self.fecha_reserva and self.fecha_reserva < timezone.now().date():
            raise ValidationError('No se puede reservar en fechas pasadas')
        
        # Validar capacidad de la mesa
        if self.numero_comensales:
            if self.mesa and (self.numero_comensales < self.mesa.capacidad_minima or 
                            self.numero_comensales > self.mesa.capacidad_maxima):
                raise ValidationError(
                    f'El número de comensales debe estar entre {self.mesa.capacidad_minima} '
                    f'y {self.mesa.capacidad_maxima} para esta mesa'
                )
        
        # Validar horarios de operación
        config = ConfiguracionRestaurante.objects.first()
        if config and self.hora_reserva:
            if self.hora_reserva < config.hora_apertura or self.hora_reserva > config.hora_cierre:
                raise ValidationError(
                    f'La reserva debe estar entre {config.hora_apertura} y {config.hora_cierre}'
                )
    
    def save(self, *args, **kwargs):
        # Auto-llenar información del usuario si está disponible
        if self.usuario and not self.nombre_cliente:
            self.nombre_cliente = f"{self.usuario.first_name} {self.usuario.last_name}".strip() or self.usuario.username
            self.telefono_cliente = self.usuario.telefono or ''
            self.email_cliente = self.usuario.email or ''
        
        self.clean()
        super().save(*args, **kwargs)
    
    @property
    def fecha_hora_reserva(self):
        """Combina fecha y hora de la reserva"""
        return timezone.make_aware(
            datetime.combine(self.fecha_reserva, self.hora_reserva)
        )
    
    @property
    def puede_cancelar(self):
        """Verifica si la reserva puede ser cancelada"""
        if self.estado in [EstadoReserva.CANCELADA, EstadoReserva.COMPLETADA, EstadoReserva.NO_SHOW]:
            return False
        
        config = ConfiguracionRestaurante.objects.first()
        if not config:
            return True
        
        tiempo_limite = self.fecha_hora_reserva - timedelta(hours=config.permite_cancelacion_horas)
        return timezone.now() < tiempo_limite
    
    @property
    def tiempo_para_reserva(self):
        """Tiempo restante hasta la reserva"""
        return self.fecha_hora_reserva - timezone.now()
    
    @property
    def esta_activa(self):
        """Verifica si la reserva está activa (no cancelada ni completada)"""
        return self.estado not in [EstadoReserva.CANCELADA, EstadoReserva.COMPLETADA, EstadoReserva.NO_SHOW]
    
    def confirmar(self, usuario_confirmacion=None):
        """Confirma la reserva"""
        self.estado = EstadoReserva.CONFIRMADA
        self.fecha_confirmacion = timezone.now()
        self.usuario_confirmacion = usuario_confirmacion
        self.save()
    
    def marcar_en_curso(self):
        """Marca la reserva como en curso (cliente llegó)"""
        self.estado = EstadoReserva.EN_CURSO
        self.fecha_llegada = timezone.now()
        self.save()
    
    def marcar_completada(self):
        """Marca la reserva como completada"""
        self.estado = EstadoReserva.COMPLETADA
        self.fecha_salida = timezone.now()
        self.save()
    
    def cancelar(self):
        """Cancela la reserva"""
        if self.puede_cancelar:
            self.estado = EstadoReserva.CANCELADA
            self.fecha_cancelacion = timezone.now()
            self.save()
            return True
        return False
    
    def marcar_no_show(self):
        """Marca la reserva como no show"""
        self.estado = EstadoReserva.NO_SHOW
        self.save()

class HistorialReserva(models.Model):
    """Historial de cambios de estado de las reservas"""
    
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE, related_name='historial')
    estado_anterior = models.CharField(max_length=20, choices=EstadoReserva.choices)
    estado_nuevo = models.CharField(max_length=20, choices=EstadoReserva.choices)
    fecha_cambio = models.DateTimeField(auto_now_add=True)
    usuario_responsable = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Usuario que realizó el cambio"
    )
    comentario = models.TextField(blank=True, max_length=200)
    
    class Meta:
        verbose_name = "Historial de Reserva"
        verbose_name_plural = "Historiales de Reservas"
        ordering = ['-fecha_cambio']
    
    def __str__(self):
        return f"Reserva {str(self.reserva.codigo_reserva)[:8]} - {self.estado_anterior} → {self.estado_nuevo}"

class BloqueoMesa(models.Model):
    """Bloqueos temporales de mesas para mantenimiento, eventos, etc."""
    
    mesa = models.ForeignKey(Mesa, on_delete=models.CASCADE, related_name='bloqueos')
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    motivo = models.CharField(
        max_length=50,
        choices=[
            ('mantenimiento', 'Mantenimiento'),
            ('evento_privado', 'Evento Privado'),
            ('limpieza', 'Limpieza'),
            ('reparacion', 'Reparación'),
            ('otro', 'Otro'),
        ]
    )
    descripcion = models.TextField(blank=True)
    usuario_creacion = models.ForeignKey(User, on_delete=models.CASCADE)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Bloqueo de Mesa"
        verbose_name_plural = "Bloqueos de Mesas"
        ordering = ['-fecha_inicio']
    
    def __str__(self):
        return f"Bloqueo Mesa {self.mesa.numero} - {self.fecha_inicio.date()} - {self.motivo}"
    
    def clean(self):
        if self.fecha_inicio and self.fecha_fin and self.fecha_inicio >= self.fecha_fin:
            raise ValidationError('La fecha de inicio debe ser anterior a la fecha de fin')
    
    @property
    def esta_activo(self):
        """Verifica si el bloqueo está activo en este momento"""
        if not self.activo:
            return False
        now = timezone.now()
        return self.fecha_inicio <= now <= self.fecha_fin
