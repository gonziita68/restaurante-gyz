from django.contrib import admin
from .models import Conversacion, Mensaje, RespuestaAutomatica

@admin.register(Conversacion)
class ConversacionAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'usuario', 'fecha_inicio', 'activa']
    list_filter = ['activa', 'fecha_inicio']
    search_fields = ['session_id', 'usuario__username']
    readonly_fields = ['fecha_inicio']

@admin.register(Mensaje)
class MensajeAdmin(admin.ModelAdmin):
    list_display = ['conversacion', 'tipo', 'contenido_corto', 'timestamp']
    list_filter = ['tipo', 'timestamp']
    search_fields = ['contenido']
    readonly_fields = ['timestamp']
    
    def contenido_corto(self, obj):
        return obj.contenido[:50] + '...' if len(obj.contenido) > 50 else obj.contenido
    contenido_corto.short_description = 'Contenido'

@admin.register(RespuestaAutomatica)
class RespuestaAutomaticaAdmin(admin.ModelAdmin):
    list_display = ['palabras_clave_cortas', 'respuesta_corta', 'activa', 'prioridad']
    list_filter = ['activa', 'prioridad']
    search_fields = ['palabras_clave', 'respuesta']
    
    def palabras_clave_cortas(self, obj):
        return obj.palabras_clave[:30] + '...' if len(obj.palabras_clave) > 30 else obj.palabras_clave
    palabras_clave_cortas.short_description = 'Palabras Clave'
    
    def respuesta_corta(self, obj):
        return obj.respuesta[:50] + '...' if len(obj.respuesta) > 50 else obj.respuesta
    respuesta_corta.short_description = 'Respuesta'
