from django.contrib import admin
from django.utils.html import format_html
from .models import (
    CategoriaMenu, Ingrediente, PlatoMenu, OpcionPersonalizacion,
    MenuDelDia, PlatoMenuDelDia, Resena
)
from django.utils import timezone

@admin.register(CategoriaMenu)
class CategoriaMenuAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'orden', 'activa', 'cantidad_platos']
    list_editable = ['orden', 'activa']
    list_filter = ['activa']
    search_fields = ['nombre', 'descripcion']
    ordering = ['orden', 'nombre']
    
    def cantidad_platos(self, obj):
        return obj.platos.count()
    cantidad_platos.short_description = 'Platos'

@admin.register(Ingrediente)
class IngredienteAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'es_alergeno', 'tipo_alergeno']
    list_filter = ['es_alergeno', 'tipo_alergeno']
    search_fields = ['nombre']
    ordering = ['nombre']

class OpcionPersonalizacionInline(admin.TabularInline):
    model = OpcionPersonalizacion
    extra = 0
    fields = ['nombre', 'descripcion', 'precio_adicional', 'disponible']

@admin.register(PlatoMenu)
class PlatoMenuAdmin(admin.ModelAdmin):
    list_display = [
        'nombre', 'categoria', 'precio_display', 'disponible', 
        'es_vegetariano', 'destacado', 'imagen_preview'
    ]
    list_filter = [
        'categoria', 'disponible', 'es_vegetariano', 'es_vegano', 
        'sin_gluten', 'destacado', 'nuevo'
    ]
    search_fields = ['nombre', 'descripcion']
    list_editable = ['disponible', 'destacado']
    ordering = ['categoria__orden', 'orden', 'nombre']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'descripcion', 'categoria', 'orden')
        }),
        ('Precios', {
            'fields': ('precio', 'precio_oferta')
        }),
        ('Imágenes', {
            'fields': ('imagen', 'imagen_thumbnail')
        }),
        ('Ingredientes y Características', {
            'fields': (
                'ingredientes', 'tiempo_preparacion', 'calorias',
                'es_vegetariano', 'es_vegano', 'sin_gluten',
                'es_picante', 'nivel_picante'
            )
        }),
        ('Disponibilidad', {
            'fields': (
                'disponible', 'disponible_almuerzo', 'disponible_cena',
                'disponible_desde', 'disponible_hasta'
            )
        }),
        ('Opciones Especiales', {
            'fields': ('destacado', 'nuevo')
        })
    )
    
    filter_horizontal = ['ingredientes']
    inlines = [OpcionPersonalizacionInline]
    readonly_fields = ['imagen_thumbnail']
    
    def precio_display(self, obj):
        if obj.tiene_oferta:
            return format_html(
                '<span style="text-decoration: line-through;">${}</span> '
                '<span style="color: red; font-weight: bold;">${}</span>',
                obj.precio, obj.precio_oferta
            )
        return f"${obj.precio}"
    precio_display.short_description = 'Precio'
    
    def imagen_preview(self, obj):
        if obj.imagen:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover;">',
                obj.imagen.url
            )
        return "Sin imagen"
    imagen_preview.short_description = 'Imagen'

class PlatoMenuDelDiaInline(admin.TabularInline):
    model = PlatoMenuDelDia
    extra = 0
    fields = ['plato', 'precio_especial', 'orden']
    ordering = ['orden']

@admin.register(MenuDelDia)
class MenuDelDiaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'fecha', 'precio_completo', 'activo', 'cantidad_platos']
    list_filter = ['activo', 'fecha']
    search_fields = ['nombre', 'descripcion']
    date_hierarchy = 'fecha'
    ordering = ['-fecha']
    
    inlines = [PlatoMenuDelDiaInline]
    
    def cantidad_platos(self, obj):
        return obj.platos.count()
    cantidad_platos.short_description = 'Platos'

@admin.register(OpcionPersonalizacion)
class OpcionPersonalizacionAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'plato', 'precio_adicional', 'disponible']
    list_filter = ['disponible', 'plato__categoria']
    search_fields = ['nombre', 'plato__nombre']
    ordering = ['plato__nombre', 'nombre']

@admin.register(Resena)
class ResenaAdmin(admin.ModelAdmin):
    list_display = ['plato', 'cliente', 'calificacion', 'fecha_creacion', 'activa', 'tiene_respuesta']
    list_filter = ['calificacion', 'activa', 'fecha_creacion', 'plato__categoria']
    search_fields = ['plato__nombre', 'cliente__nombre', 'comentario']
    readonly_fields = ['fecha_creacion', 'fecha_modificacion']
    list_editable = ['activa']
    
    fieldsets = (
        ('Información de la Reseña', {
            'fields': ('plato', 'cliente', 'calificacion', 'comentario', 'activa')
        }),
        ('Respuesta del Restaurante', {
            'fields': ('respuesta_restaurante', 'fecha_respuesta'),
            'classes': ('collapse',)
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_modificacion'),
            'classes': ('collapse',)
        }),
    )
    
    def tiene_respuesta(self, obj):
        return bool(obj.respuesta_restaurante)
    tiene_respuesta.boolean = True
    tiene_respuesta.short_description = 'Tiene respuesta'
    
    def save_model(self, request, obj, form, change):
        if 'respuesta_restaurante' in form.changed_data and obj.respuesta_restaurante:
            obj.fecha_respuesta = timezone.now()
        super().save_model(request, obj, form, change)
