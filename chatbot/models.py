from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils import timezone

class Conversacion(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    session_id = models.CharField(max_length=100, unique=True)
    fecha_inicio = models.DateTimeField(default=timezone.now)
    activa = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Conversación {self.session_id} - {self.fecha_inicio}"
    
    class Meta:
        verbose_name = "Conversación"
        verbose_name_plural = "Conversaciones"

class Mensaje(models.Model):
    TIPO_CHOICES = [
        ('usuario', 'Usuario'),
        ('bot', 'Bot'),
    ]
    
    conversacion = models.ForeignKey(Conversacion, on_delete=models.CASCADE, related_name='mensajes')
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    contenido = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.tipo}: {self.contenido[:50]}..."
    
    class Meta:
        ordering = ['timestamp']
        verbose_name = "Mensaje"
        verbose_name_plural = "Mensajes"

class RespuestaAutomatica(models.Model):
    TIPO_ACCION_CHOICES = [
        ('respuesta', 'Respuesta Simple'),
        ('reserva', 'Crear Reserva'),
        ('pedido', 'Crear Pedido'),
        ('consulta_menu', 'Consultar Menú'),
        ('consulta_horario', 'Consultar Horarios'),
        ('consulta_ubicacion', 'Consultar Ubicación'),
    ]
    
    palabras_clave = models.TextField(help_text="Palabras clave separadas por comas")
    respuesta = models.TextField()
    tipo_accion = models.CharField(max_length=20, choices=TIPO_ACCION_CHOICES, default='respuesta')
    requiere_datos = models.BooleanField(default=False, help_text="Si requiere datos adicionales del usuario")
    activa = models.BooleanField(default=True)
    prioridad = models.IntegerField(default=1, help_text="Mayor número = mayor prioridad")
    
    def __str__(self):
        return f"Respuesta: {self.palabras_clave[:30]}..."
    
    class Meta:
        verbose_name = "Respuesta Automática"
        verbose_name_plural = "Respuestas Automáticas"
        ordering = ['-prioridad']

class SolicitudChatbot(models.Model):
    TIPO_SOLICITUD_CHOICES = [
        ('reserva', 'Reserva'),
        ('pedido', 'Pedido'),
        ('consulta', 'Consulta'),
    ]
    
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('procesando', 'Procesando'),
        ('completada', 'Completada'),
        ('error', 'Error'),
    ]
    
    conversacion = models.ForeignKey(Conversacion, on_delete=models.CASCADE, related_name='solicitudes')
    tipo_solicitud = models.CharField(max_length=20, choices=TIPO_SOLICITUD_CHOICES)
    datos_solicitud = models.JSONField(default=dict, help_text="Datos extraídos de la conversación")
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    resultado = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(default=timezone.now)
    fecha_procesamiento = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.tipo_solicitud} - {self.estado} - {self.fecha_creacion}"
    
    class Meta:
        verbose_name = "Solicitud Chatbot"
        verbose_name_plural = "Solicitudes Chatbot"
        ordering = ['-fecha_creacion']
