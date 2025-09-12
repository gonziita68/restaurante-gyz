from django.core.exceptions import ValidationError
import os
from PIL import Image

# Configuraciones para archivos multimedia
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
MAX_AVATAR_SIZE = 2 * 1024 * 1024  # 2MB
ALLOWED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
IMAGE_QUALITY = 85
THUMBNAIL_SIZE = (300, 300)
AVATAR_SIZE = (150, 150)

def validate_image_size(image, max_size=MAX_IMAGE_SIZE):
    """
    Valida el tamaño de una imagen
    """
    if image.size > max_size:
        raise ValidationError(
            f'El archivo es demasiado grande. Tamaño máximo permitido: {max_size // (1024*1024)}MB'
        )

def validate_image_extension(image):
    """
    Valida la extensión de una imagen
    """
    ext = os.path.splitext(image.name)[1].lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValidationError(
            f'Formato de archivo no permitido. Formatos permitidos: {", ".join(ALLOWED_IMAGE_EXTENSIONS)}'
        )

def validate_image_dimensions(image, min_width=100, min_height=100, max_width=4000, max_height=4000):
    """
    Valida las dimensiones de una imagen
    """
    try:
        img = Image.open(image)
        width, height = img.size
        
        if width < min_width or height < min_height:
            raise ValidationError(
                f'La imagen es demasiado pequeña. Dimensiones mínimas: {min_width}x{min_height}px'
            )
        
        if width > max_width or height > max_height:
            raise ValidationError(
                f'La imagen es demasiado grande. Dimensiones máximas: {max_width}x{max_height}px'
            )
    except Exception as e:
        raise ValidationError('No se pudo procesar la imagen. Asegúrate de que sea un archivo de imagen válido.')

def validate_plato_image(image):
    """
    Validador específico para imágenes de platos
    """
    validate_image_extension(image)
    validate_image_size(image, MAX_IMAGE_SIZE)
    validate_image_dimensions(image, min_width=200, min_height=200)

def validate_avatar_image(image):
    """
    Validador específico para avatares
    """
    validate_image_extension(image)
    validate_image_size(image, MAX_AVATAR_SIZE)
    validate_image_dimensions(image, min_width=50, min_height=50, max_width=1000, max_height=1000)

def validate_evento_image(image):
    """
    Validador específico para imágenes de eventos
    """
    validate_image_extension(image)
    validate_image_size(image, MAX_IMAGE_SIZE)
    validate_image_dimensions(image, min_width=300, min_height=200)

# Funciones de utilidad para procesamiento de imágenes
def resize_image(image_path, size, quality=IMAGE_QUALITY):
    """
    Redimensiona una imagen manteniendo la proporción
    """
    try:
        with Image.open(image_path) as img:
            # Convertir a RGB si es necesario
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Redimensionar manteniendo proporción
            img.thumbnail(size, Image.Resampling.LANCZOS)
            
            # Guardar con calidad especificada
            img.save(image_path, 'JPEG', quality=quality, optimize=True)
    except Exception as e:
        print(f"Error al redimensionar imagen {image_path}: {e}")

def create_thumbnail(original_path, thumbnail_path, size=THUMBNAIL_SIZE):
    """
    Crea un thumbnail de una imagen
    """
    try:
        with Image.open(original_path) as img:
            # Convertir a RGB si es necesario
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Crear thumbnail
            img.thumbnail(size, Image.Resampling.LANCZOS)
            
            # Crear directorio si no existe
            os.makedirs(os.path.dirname(thumbnail_path), exist_ok=True)
            
            # Guardar thumbnail
            img.save(thumbnail_path, 'JPEG', quality=IMAGE_QUALITY, optimize=True)
            
        return True
    except Exception as e:
        print(f"Error al crear thumbnail: {e}")
        return False

# Configuración de paths para diferentes tipos de archivos
MEDIA_PATHS = {
    'platos': 'platos/',
    'platos_thumbnails': 'platos/thumbnails/',
    'avatars': 'avatars/',
    'eventos_tipos': 'eventos/tipos/',
    'eventos_menus': 'eventos/menus/',
    'usuarios': 'usuarios/',
}

# Configuración de validadores por tipo
VALIDATORS = {
    'plato': [validate_plato_image],
    'avatar': [validate_avatar_image],
    'evento': [validate_evento_image],
}