from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class Usuario(AbstractUser):
    """Modelo de usuario personalizado"""
    
    # Campos adicionales
    telefono = models.CharField(max_length=15, blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    es_activo = models.BooleanField(default=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    ultimo_acceso = models.DateTimeField(blank=True, null=True)
    
    # Resolver conflictos de related_name
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='usuario_set',
        related_query_name='usuario',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='usuario_set',
        related_query_name='usuario',
    )
    
    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
    
    def __str__(self):
        return self.username
    
    def actualizar_ultimo_acceso(self):
        """Actualiza la fecha del último acceso"""
        self.ultimo_acceso = timezone.now()
        self.save(update_fields=['ultimo_acceso'])

class PerfilUsuario(models.Model):
    """Perfil extendido del usuario"""
    
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='perfil')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    biografia = models.TextField(blank=True, max_length=500)
    sitio_web = models.URLField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuario"
    
    def __str__(self):
        return f"Perfil de {self.usuario.username}"

class EmailLog(models.Model):
    PURPOSE_CHOICES = [
        ('verification', 'Verification'),
        ('welcome', 'Welcome'),
        ('password_reset', 'Password Reset'),
        ('password_changed', 'Password Changed'),
        ('other', 'Other'),
    ]
    STATUS_CHOICES = [
        ('queued', 'Queued'),
        ('sent', 'Sent'),
        ('error', 'Error'),
    ]
    user = models.ForeignKey(Usuario, null=True, blank=True, on_delete=models.SET_NULL, related_name='email_logs')
    to_email = models.EmailField()
    subject = models.CharField(max_length=255)
    template = models.CharField(max_length=255, blank=True)
    purpose = models.CharField(max_length=32, choices=PURPOSE_CHOICES, default='other')
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='queued')
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Registro de Email'
        verbose_name_plural = 'Registros de Email'

    def __str__(self) -> str:
        return f"{self.get_purpose_display()} → {self.to_email} [{self.status}]"