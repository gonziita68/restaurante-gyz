from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, PerfilUsuario, EmailLog

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    """Configuración del admin para el modelo Usuario"""
    
    list_display = ('username', 'email', 'first_name', 'last_name', 'telefono', 
                   'es_activo', 'fecha_registro', 'ultimo_acceso')
    list_filter = ('es_activo', 'fecha_registro', 'groups')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'telefono')
    ordering = ('-fecha_registro',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Información Personal', {
            'fields': ('first_name', 'last_name', 'email', 'telefono', 
                      'fecha_nacimiento', 'direccion')
        }),
        ('Permisos', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Fechas importantes', {
            'fields': ('last_login', 'fecha_registro', 'ultimo_acceso'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'first_name', 
                      'last_name', 'telefono', 'fecha_nacimiento', 'direccion'),
        }),
    )
    
    readonly_fields = ('fecha_registro', 'ultimo_acceso')
    
    def get_queryset(self, request):
        """Personalizar queryset para mostrar solo usuarios personalizados"""
        return super().get_queryset(request)

@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    """Configuración del admin para el modelo PerfilUsuario"""
    
    list_display = ('usuario', 'sitio_web')
    search_fields = ('usuario__username', 'usuario__email', 'biografia')
    
    fieldsets = (
        ('Usuario', {
            'fields': ('usuario',)
        }),
        ('Información del Perfil', {
            'fields': ('avatar', 'biografia', 'sitio_web')
        }),
    )

@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'user', 'to_email', 'purpose', 'status', 'subject')
    list_filter = ('status', 'purpose', 'created_at')
    search_fields = ('to_email', 'subject', 'error_message')