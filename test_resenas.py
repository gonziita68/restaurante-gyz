#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from menu.models import PlatoMenu, Resena
from django.utils import timezone

User = get_user_model()

def crear_resenas_prueba():
    """Crear algunas reseñas de prueba para verificar el sistema"""
    
    # Obtener o crear usuarios de prueba
    try:
        usuario1 = User.objects.get(email='test1@example.com')
    except User.DoesNotExist:
        usuario1 = User.objects.create_user(
            username='testuser1',
            email='test1@example.com',
            nombre='María',
            apellido='González',
            password='testpass123'
        )
    
    try:
        usuario2 = User.objects.get(email='test2@example.com')
    except User.DoesNotExist:
        usuario2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            nombre='Carlos',
            apellido='Rodríguez',
            password='testpass123'
        )
    
    try:
        usuario3 = User.objects.get(email='test3@example.com')
    except User.DoesNotExist:
        usuario3 = User.objects.create_user(
            username='testuser3',
            email='test3@example.com',
            nombre='Ana',
            apellido='López',
            password='testpass123'
        )
    
    # Obtener algunos platos
    platos = PlatoMenu.objects.filter(disponible=True)[:3]
    
    if not platos:
        print("No hay platos disponibles. Creando platos de prueba...")
        from menu.models import CategoriaMenu
        
        categoria, created = CategoriaMenu.objects.get_or_create(
            nombre='Principales',
            defaults={'descripcion': 'Platos principales'}
        )
        
        plato1 = PlatoMenu.objects.create(
            nombre='Paella Valenciana',
            descripcion='Deliciosa paella tradicional',
            precio=25.00,
            categoria=categoria,
            disponible=True
        )
        
        plato2 = PlatoMenu.objects.create(
            nombre='Salmón a la Plancha',
            descripcion='Salmón fresco con verduras',
            precio=22.00,
            categoria=categoria,
            disponible=True
        )
        
        plato3 = PlatoMenu.objects.create(
            nombre='Risotto de Hongos',
            descripcion='Cremoso risotto con hongos',
            precio=18.00,
            categoria=categoria,
            disponible=True
        )
        
        platos = [plato1, plato2, plato3]
    
    # Crear reseñas de prueba con diferentes calificaciones
    resenas_data = [
        {
            'plato': platos[0],
            'cliente': usuario1,
            'calificacion': 5,
            'comentario': 'Excelente paella, auténtico sabor valenciano. El arroz estaba perfecto y los mariscos muy frescos.'
        },
        {
            'plato': platos[0],
            'cliente': usuario2,
            'calificacion': 4,
            'comentario': 'Muy buena paella, aunque esperaba un poco más de mariscos. El sabor es muy bueno.'
        },
        {
            'plato': platos[1],
            'cliente': usuario1,
            'calificacion': 5,
            'comentario': 'El salmón estaba perfecto, jugoso y bien condimentado. Las verduras como acompañamiento excelentes.'
        },
        {
            'plato': platos[1],
            'cliente': usuario3,
            'calificacion': 3,
            'comentario': 'El salmón estaba bien, pero las verduras un poco pasadas. Servicio rápido.'
        },
        {
            'plato': platos[2],
            'cliente': usuario2,
            'calificacion': 4,
            'comentario': 'Risotto cremoso y sabroso. Los hongos frescos le dan un toque especial.'
        },
        {
            'plato': platos[2],
            'cliente': usuario3,
            'calificacion': 2,
            'comentario': 'El risotto estaba un poco soso y los hongos no sabían muy frescos.'
        }
    ]
    
    # Crear las reseñas
    for resena_data in resenas_data:
        resena, created = Resena.objects.get_or_create(
            plato=resena_data['plato'],
            cliente=resena_data['cliente'],
            defaults={
                'calificacion': resena_data['calificacion'],
                'comentario': resena_data['comentario']
            }
        )
        
        if created:
            print(f"✓ Reseña creada: {resena.cliente.nombre} - {resena.plato.nombre} ({resena.calificacion} estrellas)")
        else:
            print(f"- Reseña ya existe: {resena.cliente.nombre} - {resena.plato.nombre}")
    
    print(f"\n📊 Resumen:")
    print(f"Total de reseñas activas: {Resena.objects.filter(activa=True).count()}")
    
    # Mostrar distribución de calificaciones
    for i in range(1, 6):
        count = Resena.objects.filter(activa=True, calificacion=i).count()
        stars = '⭐' * i
        print(f"{stars} ({i} estrella{'s' if i > 1 else ''}): {count} reseñas")

if __name__ == '__main__':
    print("🔧 Creando reseñas de prueba...")
    crear_resenas_prueba()
    print("\n✅ ¡Reseñas de prueba creadas exitosamente!")
    print("\n🌐 Visita http://127.0.0.1:8000/ para ver las reseñas en la página principal.")