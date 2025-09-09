#!/usr/bin/env python
import os
import django
from decimal import Decimal

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from eventos.models import TipoEvento, ServicioAdicional, MenuEvento

def poblar_tipos_evento():
    """Crear tipos de eventos de ejemplo"""
    tipos = [
        {
            'nombre': 'Cumpleaños',
            'descripcion': 'Celebración de cumpleaños con decoración temática y pastel especial',
            'precio_base': Decimal('150.00'),
            'capacidad_minima': 10,
            'capacidad_maxima': 50,
            'duracion_estimada': 4
        },
        {
            'nombre': 'Boda',
            'descripcion': 'Celebración de boda con servicio completo de catering y decoración elegante',
            'precio_base': Decimal('500.00'),
            'capacidad_minima': 20,
            'capacidad_maxima': 200,
            'duracion_estimada': 8
        },
        {
            'nombre': 'Evento Corporativo',
            'descripcion': 'Eventos empresariales, conferencias y reuniones de trabajo',
            'precio_base': Decimal('300.00'),
            'capacidad_minima': 15,
            'capacidad_maxima': 100,
            'duracion_estimada': 6
        },
        {
            'nombre': 'Aniversario',
            'descripcion': 'Celebración de aniversarios con ambiente romántico y especial',
            'precio_base': Decimal('200.00'),
            'capacidad_minima': 8,
            'capacidad_maxima': 40,
            'duracion_estimada': 5
        },
        {
            'nombre': 'Graduación',
            'descripcion': 'Celebración de graduaciones con ambiente festivo y juvenil',
            'precio_base': Decimal('180.00'),
            'capacidad_minima': 12,
            'capacidad_maxima': 60,
            'duracion_estimada': 4
        }
    ]
    
    for tipo_data in tipos:
        tipo, created = TipoEvento.objects.get_or_create(
            nombre=tipo_data['nombre'],
            defaults=tipo_data
        )
        if created:
            print(f"✅ Tipo de evento creado: {tipo.nombre}")
        else:
            print(f"ℹ️ Tipo de evento ya existe: {tipo.nombre}")

def poblar_servicios_adicionales():
    """Crear servicios adicionales de ejemplo"""
    servicios = [
        {
            'nombre': 'Decoración Temática',
            'descripcion': 'Decoración personalizada según el tema del evento',
            'precio': Decimal('80.00'),
            'precio_por_persona': False
        },
        {
            'nombre': 'Música en Vivo',
            'descripcion': 'Servicio de música en vivo con DJ o banda',
            'precio': Decimal('150.00'),
            'precio_por_persona': False
        },
        {
            'nombre': 'Fotógrafo Profesional',
            'descripcion': 'Servicio de fotografía profesional con álbum digital',
            'precio': Decimal('200.00'),
            'precio_por_persona': False
        },
        {
            'nombre': 'Bebidas Premium',
            'descripcion': 'Selección de bebidas premium y cócteles especiales',
            'precio': Decimal('25.00'),
            'precio_por_persona': True
        },
        {
            'nombre': 'Servicio de Mesa',
            'descripcion': 'Personal de servicio para atender a los invitados',
            'precio': Decimal('15.00'),
            'precio_por_persona': True
        },
        {
            'nombre': 'Centro de Mesa',
            'descripcion': 'Centros de mesa decorativos para cada mesa',
            'precio': Decimal('10.00'),
            'precio_por_persona': True
        },
        {
            'nombre': 'Iluminación Especial',
            'descripcion': 'Iluminación ambiental y efectos especiales',
            'precio': Decimal('100.00'),
            'precio_por_persona': False
        },
        {
            'nombre': 'Torta Personalizada',
            'descripcion': 'Torta personalizada según el tema del evento',
            'precio': Decimal('120.00'),
            'precio_por_persona': False
        }
    ]
    
    for servicio_data in servicios:
        servicio, created = ServicioAdicional.objects.get_or_create(
            nombre=servicio_data['nombre'],
            defaults=servicio_data
        )
        if created:
            print(f"✅ Servicio adicional creado: {servicio.nombre}")
        else:
            print(f"ℹ️ Servicio adicional ya existe: {servicio.nombre}")

def poblar_menus_evento():
    """Crear menús de eventos de ejemplo"""
    menus = [
        {
            'nombre': 'Menú Ejecutivo',
            'descripcion': 'Menú ideal para eventos corporativos y reuniones de trabajo',
            'precio_por_persona': Decimal('35.00'),
            'platos': 'Entrada: Ensalada César\nPlato Principal: Pechuga a la plancha con vegetales\nPostre: Tiramisú\nBebida: Agua, café o té',
            'bebidas_incluidas': True,
            'postre_incluido': True
        },
        {
            'nombre': 'Menú Festivo',
            'descripcion': 'Menú perfecto para celebraciones y eventos sociales',
            'precio_por_persona': Decimal('45.00'),
            'platos': 'Entrada: Bruschettas variadas\nPlato Principal: Pasta al pesto o Pollo al horno\nPostre: Cheesecake de frutos rojos\nBebida: Vino tinto o blanco, refrescos',
            'bebidas_incluidas': True,
            'postre_incluido': True
        },
        {
            'nombre': 'Menú Premium',
            'descripcion': 'Menú de alta calidad para eventos especiales',
            'precio_por_persona': Decimal('65.00'),
            'platos': 'Entrada: Carpaccio de res\nPlato Principal: Salmón a la parrilla o Filete mignon\nPostre: Crème brûlée\nBebida: Champagne, vinos premium, cócteles',
            'bebidas_incluidas': True,
            'postre_incluido': True
        },
        {
            'nombre': 'Menú Infantil',
            'descripcion': 'Menú especial para eventos de niños y cumpleaños infantiles',
            'precio_por_persona': Decimal('25.00'),
            'platos': 'Entrada: Nuggets de pollo\nPlato Principal: Hamburguesa con papas fritas\nPostre: Helado con toppings\nBebida: Jugos naturales, refrescos',
            'bebidas_incluidas': True,
            'postre_incluido': True
        },
        {
            'nombre': 'Menú Vegetariano',
            'descripcion': 'Menú completo para vegetarianos y veganos',
            'precio_por_persona': Decimal('40.00'),
            'platos': 'Entrada: Ensalada de quinoa\nPlato Principal: Risotto de hongos o Curry de vegetales\nPostre: Mousse de chocolate vegano\nBebida: Agua, jugos naturales, té',
            'bebidas_incluidas': True,
            'postre_incluido': True
        }
    ]
    
    for menu_data in menus:
        menu, created = MenuEvento.objects.get_or_create(
            nombre=menu_data['nombre'],
            defaults=menu_data
        )
        if created:
            print(f"✅ Menú de evento creado: {menu.nombre}")
        else:
            print(f"ℹ️ Menú de evento ya existe: {menu.nombre}")

def main():
    print("🚀 POBLANDO SISTEMA DE EVENTOS Y CATERING")
    print("="*50)
    
    print("\n📋 Creando tipos de eventos...")
    poblar_tipos_evento()
    
    print("\n🎨 Creando servicios adicionales...")
    poblar_servicios_adicionales()
    
    print("\n🍽️ Creando menús de eventos...")
    poblar_menus_evento()
    
    print("\n" + "="*50)
    print("✅ SISTEMA DE EVENTOS POBLADO EXITOSAMENTE")
    print("="*50)
    print("Ahora puedes:")
    print("1. Ir a http://localhost:8000/admin/")
    print("2. Verificar que los datos se crearon correctamente")
    print("3. Ir a http://localhost:8000/eventos/solicitar/")
    print("4. Probar el sistema de eventos y catering")
    print("="*50)

if __name__ == '__main__':
    main()
