from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from PIL import Image
import os

class CategoriaMenu(models.Model):
    """Categorías del menú (Entrantes, Principales, Postres, Bebidas, etc.)"""
    
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    orden = models.PositiveIntegerField(default=0, help_text="Orden de aparición en el menú")
    activa = models.BooleanField(default=True)
    icono = models.CharField(max_length=50, blank=True, help_text="Clase de icono FontAwesome")
    
    class Meta:
        verbose_name = "Categoría del Menú"
        verbose_name_plural = "Categorías del Menú"
        ordering = ['orden', 'nombre']
    
    def __str__(self):
        return self.nombre

class Ingrediente(models.Model):
    """Ingredientes disponibles"""
    
    nombre = models.CharField(max_length=100, unique=True)
    es_alergeno = models.BooleanField(default=False)
    tipo_alergeno = models.CharField(
        max_length=50, 
        blank=True, 
        choices=[
            ('gluten', 'Gluten'),
            ('lacteos', 'Lácteos'),
            ('huevos', 'Huevos'),
            ('pescado', 'Pescado'),
            ('mariscos', 'Mariscos'),
            ('frutos_secos', 'Frutos Secos'),
            ('soja', 'Soja'),
            ('sesamo', 'Sésamo'),
        ]
    )
    
    class Meta:
        verbose_name = "Ingrediente"
        verbose_name_plural = "Ingredientes"
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.nombre} {'(Alérgeno)' if self.es_alergeno else ''}"

class PlatoMenu(models.Model):
    """Platos del menú"""
    
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    categoria = models.ForeignKey(CategoriaMenu, on_delete=models.CASCADE, related_name='platos')
    precio = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0)])
    precio_oferta = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        blank=True, 
        null=True,
        validators=[MinValueValidator(0)],
        help_text="Precio con descuento (opcional)"
    )
    
    # Imágenes
    imagen = models.ImageField(upload_to='platos/', blank=True, null=True)
    imagen_thumbnail = models.ImageField(upload_to='platos/thumbnails/', blank=True, null=True)
    
    # Características del plato
    ingredientes = models.ManyToManyField(Ingrediente, blank=True, related_name='platos')
    tiempo_preparacion = models.PositiveIntegerField(
        help_text="Tiempo de preparación en minutos",
        default=15
    )
    calorias = models.PositiveIntegerField(blank=True, null=True)
    
    # Opciones especiales
    es_vegetariano = models.BooleanField(default=False)
    es_vegano = models.BooleanField(default=False)
    sin_gluten = models.BooleanField(default=False)
    es_picante = models.BooleanField(default=False)
    nivel_picante = models.PositiveIntegerField(
        default=0,
        choices=[(0, 'No picante'), (1, 'Suave'), (2, 'Medio'), (3, 'Picante'), (4, 'Muy picante')]
    )
    
    # Disponibilidad
    disponible = models.BooleanField(default=True)
    disponible_almuerzo = models.BooleanField(default=True)
    disponible_cena = models.BooleanField(default=True)
    disponible_desde = models.TimeField(blank=True, null=True)
    disponible_hasta = models.TimeField(blank=True, null=True)
    
    # Información adicional
    destacado = models.BooleanField(default=False, help_text="Plato destacado/recomendado")
    nuevo = models.BooleanField(default=False, help_text="Plato nuevo en el menú")
    orden = models.PositiveIntegerField(default=0, help_text="Orden dentro de la categoría")
    
    # Fechas
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Plato del Menú"
        verbose_name_plural = "Platos del Menú"
        ordering = ['categoria__orden', 'orden', 'nombre']
        unique_together = ['nombre', 'categoria']
    
    def __str__(self):
        return f"{self.nombre} - {self.categoria.nombre}"
    
    @property
    def precio_actual(self):
        """Retorna el precio actual (con oferta si la hay)"""
        return self.precio_oferta if self.precio_oferta else self.precio
    
    @property
    def tiene_oferta(self):
        """Verifica si el plato tiene oferta"""
        return self.precio_oferta is not None and self.precio_oferta < self.precio
    
    @property
    def descuento_porcentaje(self):
        """Calcula el porcentaje de descuento"""
        if self.tiene_oferta:
            return round(((self.precio - self.precio_oferta) / self.precio) * 100)
        return 0
    
    @property
    def alergenos(self):
        """Lista de alérgenos del plato"""
        return self.ingredientes.filter(es_alergeno=True)
    
    def esta_disponible_ahora(self):
        """Verifica si el plato está disponible en el horario actual"""
        if not self.disponible:
            return False
        
        now = timezone.now().time()
        
        if self.disponible_desde and self.disponible_hasta:
            return self.disponible_desde <= now <= self.disponible_hasta
        
        return True
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Crear thumbnail automáticamente
        if self.imagen and not self.imagen_thumbnail:
            self.crear_thumbnail()
    
    def crear_thumbnail(self):
        """Crea un thumbnail de la imagen principal"""
        if not self.imagen:
            return
        
        try:
            image = Image.open(self.imagen.path)
            image.thumbnail((300, 300), Image.Resampling.LANCZOS)
            
            # Guardar thumbnail
            thumb_path = self.imagen.path.replace('platos/', 'platos/thumbnails/')
            os.makedirs(os.path.dirname(thumb_path), exist_ok=True)
            image.save(thumb_path, quality=85)
            
            # Actualizar campo thumbnail
            self.imagen_thumbnail = thumb_path.replace(os.path.dirname(self.imagen.path), 'platos/thumbnails')
            super().save(update_fields=['imagen_thumbnail'])
        except Exception as e:
            print(f"Error creando thumbnail: {e}")
    
    def calcular_promedio_calificaciones(self):
        """Calcula el promedio de calificaciones del plato"""
        from django.db.models import Avg
        return self.resenas.filter(activa=True).aggregate(
            promedio=Avg('calificacion')
        )['promedio'] or 0
    
    def obtener_total_resenas(self):
        """Obtiene el total de reseñas activas"""
        return self.resenas.filter(activa=True).count()
    
    def obtener_distribucion_calificaciones(self):
        """Obtiene la distribución de calificaciones (1-5 estrellas)"""
        from django.db.models import Count
        distribucion = self.resenas.filter(activa=True).values('calificacion').annotate(
            total=Count('calificacion')
        ).order_by('calificacion')
        
        # Crear diccionario con todas las calificaciones (1-5)
        resultado = {i: 0 for i in range(1, 6)}
        for item in distribucion:
            resultado[item['calificacion']] = item['total']
        
        return resultado

class OpcionPersonalizacion(models.Model):
    """Opciones de personalización para platos (ej: sin cebolla, extra queso)"""
    
    plato = models.ForeignKey(PlatoMenu, on_delete=models.CASCADE, related_name='opciones_personalizacion')
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=200, blank=True)
    precio_adicional = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0)]
    )
    disponible = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Opción de Personalización"
        verbose_name_plural = "Opciones de Personalización"
        unique_together = ['plato', 'nombre']
    
    def __str__(self):
        precio_text = f" (+${self.precio_adicional})" if self.precio_adicional > 0 else ""
        return f"{self.nombre}{precio_text}"

class MenuDelDia(models.Model):
    """Menú especial del día"""
    
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    fecha = models.DateField()
    platos = models.ManyToManyField(PlatoMenu, through='PlatoMenuDelDia')
    precio_completo = models.DecimalField(
        max_digits=8, 
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Precio por el menú completo (opcional)"
    )
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Menú del Día"
        verbose_name_plural = "Menús del Día"
        ordering = ['-fecha']
        unique_together = ['fecha', 'nombre']
    
    def __str__(self):
        return f"{self.nombre} - {self.fecha}"
    
    @property
    def es_hoy(self):
        return self.fecha == timezone.now().date()

class PlatoMenuDelDia(models.Model):
    """Relación entre platos y menú del día con precios especiales"""
    
    menu_dia = models.ForeignKey(MenuDelDia, on_delete=models.CASCADE)
    plato = models.ForeignKey(PlatoMenu, on_delete=models.CASCADE)
    precio_especial = models.DecimalField(
        max_digits=8, 
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Precio especial para este menú"
    )
    orden = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = "Plato del Menú del Día"
        verbose_name_plural = "Platos del Menú del Día"
        ordering = ['orden']
        unique_together = ['menu_dia', 'plato']
    
    def __str__(self):
        return f"{self.plato.nombre} en {self.menu_dia.nombre}"
    
    @property
    def precio_final(self):
        return self.precio_especial if self.precio_especial else self.plato.precio_actual

class Resena(models.Model):
    ESTRELLAS_CHOICES = [
        (1, '⭐'),
        (2, '⭐⭐'),
        (3, '⭐⭐⭐'),
        (4, '⭐⭐⭐⭐'),
        (5, '⭐⭐⭐⭐⭐'),
    ]
    
    plato = models.ForeignKey(PlatoMenu, on_delete=models.CASCADE, related_name='resenas')
    cliente = models.ForeignKey('usuarios.Usuario', on_delete=models.CASCADE, related_name='resenas')
    calificacion = models.IntegerField(choices=ESTRELLAS_CHOICES, verbose_name='Calificación')
    comentario = models.TextField(max_length=500, verbose_name='Comentario')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    fecha_modificacion = models.DateTimeField(auto_now=True, verbose_name='Fecha de modificación')
    activa = models.BooleanField(default=True, verbose_name='Reseña activa')
    
    # Respuesta del restaurante
    respuesta_restaurante = models.TextField(max_length=500, blank=True, null=True, verbose_name='Respuesta del restaurante')
    fecha_respuesta = models.DateTimeField(blank=True, null=True, verbose_name='Fecha de respuesta')
    
    class Meta:
        verbose_name = 'Reseña'
        verbose_name_plural = 'Reseñas'
        unique_together = ['plato', 'cliente']  # Un cliente solo puede reseñar un plato una vez
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f'{self.cliente.nombre} - {self.plato.nombre} ({self.calificacion} estrellas)'
    
    @property
    def estrellas_display(self):
        """Retorna las estrellas como emojis para mostrar en templates"""
        return '⭐' * self.calificacion
    
    @property
    def calificacion_promedio_plato(self):
        """Calcula el promedio de calificaciones del plato"""
        return self.plato.resenas.filter(activa=True).aggregate(
            promedio=models.Avg('calificacion')
        )['promedio'] or 0
    
    def puede_editar(self, usuario):
        """Verifica si un usuario puede editar esta reseña"""
        return usuario == self.cliente and self.activa
    
    def puede_responder(self, usuario):
        """Verifica si un usuario del restaurante puede responder a esta reseña"""
        return usuario.is_staff and self.activa
