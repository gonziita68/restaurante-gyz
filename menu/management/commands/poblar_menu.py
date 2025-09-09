from django.core.management.base import BaseCommand
from menu.models import CategoriaMenu, Ingrediente, PlatoMenu, OpcionPersonalizacion
from decimal import Decimal

class Command(BaseCommand):
    help = 'Puebla la base de datos con datos de ejemplo para el menú'

    def handle(self, *args, **options):
        self.stdout.write('Creando datos de ejemplo para el menú...')
        
        # Crear ingredientes
        ingredientes_data = [
            ('Tomate', False, ''),
            ('Lechuga', False, ''),
            ('Cebolla', False, ''),
            ('Queso mozzarella', True, 'lacteos'),
            ('Queso parmesano', True, 'lacteos'),
            ('Pollo', False, ''),
            ('Carne de res', False, ''),
            ('Salmón', True, 'pescado'),
            ('Camarones', True, 'mariscos'),
            ('Huevos', True, 'huevos'),
            ('Leche', True, 'lacteos'),
            ('Harina de trigo', True, 'gluten'),
            ('Almendras', True, 'frutos_secos'),
            ('Nueces', True, 'frutos_secos'),
            ('Aceite de soja', True, 'soja'),
            ('Albahaca', False, ''),
            ('Orégano', False, ''),
            ('Ajo', False, ''),
            ('Limón', False, ''),
            ('Aguacate', False, ''),
        ]
        
        for nombre, es_alergeno, tipo_alergeno in ingredientes_data:
            ingrediente, created = Ingrediente.objects.get_or_create(
                nombre=nombre,
                defaults={
                    'es_alergeno': es_alergeno,
                    'tipo_alergeno': tipo_alergeno
                }
            )
            if created:
                self.stdout.write(f'  ✓ Creado ingrediente: {nombre}')

        # Crear categorías
        categorias_data = [
            ('Entradas', 'Deliciosos aperitivos para comenzar', 1, 'fas fa-seedling'),
            ('Ensaladas', 'Frescas y nutritivas ensaladas', 2, 'fas fa-leaf'),
            ('Sopas', 'Sopas calientes y reconfortantes', 3, 'fas fa-soup'),
            ('Platos Principales', 'Nuestros platos más populares', 4, 'fas fa-hamburger'),
            ('Pastas', 'Deliciosas pastas italianas', 5, 'fas fa-pastafarianism'),
            ('Pizzas', 'Pizzas artesanales con ingredientes frescos', 6, 'fas fa-pizza-slice'),
            ('Mariscos', 'Frescos del mar', 7, 'fas fa-fish'),
            ('Postres', 'Dulces tentaciones', 8, 'fas fa-ice-cream'),
            ('Bebidas', 'Refrescantes bebidas', 9, 'fas fa-glass-water'),
            ('Cafés', 'Café de especialidad', 10, 'fas fa-coffee'),
        ]
        
        for nombre, descripcion, orden, icono in categorias_data:
            categoria, created = CategoriaMenu.objects.get_or_create(
                nombre=nombre,
                defaults={
                    'descripcion': descripcion,
                    'orden': orden,
                    'icono': icono
                }
            )
            if created:
                self.stdout.write(f'  ✓ Creada categoría: {nombre}')

        # Crear platos
        platos_data = [
            # Entradas
            ('Bruschetta Clásica', 'Pan tostado con tomate, albahaca y ajo', 'Entradas', 
             Decimal('8.50'), None, ['Tomate', 'Albahaca', 'Ajo', 'Harina de trigo'], 
             10, True, False, False, False, 0, True, False),
            
            ('Nachos Supremos', 'Nachos con queso derretido, guacamole y crema', 'Entradas',
             Decimal('12.00'), None, ['Queso mozzarella', 'Aguacate', 'Leche'],
             15, True, False, False, False, 0, False, True),
            
            # Ensaladas
            ('Ensalada César', 'Lechuga romana, crutones, parmesano y aderezo césar', 'Ensaladas',
             Decimal('11.00'), Decimal('9.50'), ['Lechuga', 'Queso parmesano', 'Huevos', 'Harina de trigo'],
             8, True, False, False, False, 0, True, False),
            
            ('Ensalada de Salmón', 'Mix de verdes con salmón a la parrilla', 'Ensaladas',
             Decimal('16.00'), None, ['Lechuga', 'Salmón', 'Limón'],
             12, False, False, True, False, 0, False, False),
            
            # Platos Principales
            ('Pollo a la Parrilla', 'Pechuga de pollo marinada con hierbas', 'Platos Principales',
             Decimal('18.00'), None, ['Pollo', 'Orégano', 'Ajo'],
             25, False, False, True, False, 0, True, False),
            
            ('Lomo de Res', 'Jugoso lomo con papas y vegetales', 'Platos Principales',
             Decimal('28.00'), None, ['Carne de res'],
             30, False, False, True, False, 0, True, False),
            
            # Pastas
            ('Spaghetti Carbonara', 'Pasta con huevo, queso y panceta', 'Pastas',
             Decimal('15.00'), None, ['Harina de trigo', 'Huevos', 'Queso parmesano'],
             18, True, False, False, False, 0, False, False),
            
            ('Lasagna de la Casa', 'Lasagna con carne, queso y salsa de tomate', 'Pastas',
             Decimal('17.00'), Decimal('15.00'), ['Harina de trigo', 'Carne de res', 'Queso mozzarella', 'Tomate'],
             25, True, False, False, False, 0, True, False),
            
            # Pizzas
            ('Pizza Margherita', 'Salsa de tomate, mozzarella y albahaca', 'Pizzas',
             Decimal('14.00'), None, ['Harina de trigo', 'Tomate', 'Queso mozzarella', 'Albahaca'],
             20, True, False, False, False, 0, False, False),
            
            ('Pizza Pepperoni', 'Pepperoni, queso mozzarella y salsa de tomate', 'Pizzas',
             Decimal('16.00'), None, ['Harina de trigo', 'Tomate', 'Queso mozzarella'],
             20, True, False, False, True, 2, False, True),
            
            # Mariscos
            ('Paella de Mariscos', 'Arroz con mariscos frescos y azafrán', 'Mariscos',
             Decimal('24.00'), None, ['Camarones', 'Salmón'],
             35, False, False, True, False, 0, True, False),
            
            # Postres
            ('Tiramisu', 'Clásico postre italiano con café y mascarpone', 'Postres',
             Decimal('8.00'), None, ['Huevos', 'Queso mozzarella'],
             5, True, False, False, False, 0, False, False),
            
            ('Cheesecake de Frutos Rojos', 'Cremoso cheesecake con salsa de frutos', 'Postres',
             Decimal('9.00'), None, ['Queso mozzarella', 'Huevos', 'Harina de trigo'],
             5, True, False, False, False, 0, True, True),
            
            # Bebidas
            ('Limonada Natural', 'Refrescante limonada con limones frescos', 'Bebidas',
             Decimal('4.00'), None, ['Limón'],
             3, True, True, True, False, 0, False, False),
            
            ('Smoothie Verde', 'Batido de espinaca, manzana y apio', 'Bebidas',
             Decimal('6.00'), None, [],
             5, True, True, True, False, 0, False, True),
            
            # Cafés
            ('Espresso', 'Café espresso tradicional', 'Cafés',
             Decimal('3.00'), None, [],
             2, True, True, True, False, 0, False, False),
            
            ('Cappuccino', 'Espresso con leche vaporizada y espuma', 'Cafés',
             Decimal('4.50'), None, ['Leche'],
             4, True, False, False, False, 0, False, False),
        ]
        
        for (nombre, descripcion, categoria_nombre, precio, precio_oferta, ingredientes_nombres,
             tiempo_prep, vegetariano, vegano, sin_gluten, picante, nivel_picante, destacado, nuevo) in platos_data:
            
            try:
                categoria = CategoriaMenu.objects.get(nombre=categoria_nombre)
                
                plato, created = PlatoMenu.objects.get_or_create(
                    nombre=nombre,
                    categoria=categoria,
                    defaults={
                        'descripcion': descripcion,
                        'precio': precio,
                        'precio_oferta': precio_oferta,
                        'tiempo_preparacion': tiempo_prep,
                        'es_vegetariano': vegetariano,
                        'es_vegano': vegano,
                        'sin_gluten': sin_gluten,
                        'es_picante': picante,
                        'nivel_picante': nivel_picante,
                        'destacado': destacado,
                        'nuevo': nuevo,
                        'disponible': True,
                    }
                )
                
                if created:
                    # Agregar ingredientes
                    for ingrediente_nombre in ingredientes_nombres:
                        try:
                            ingrediente = Ingrediente.objects.get(nombre=ingrediente_nombre)
                            plato.ingredientes.add(ingrediente)
                        except Ingrediente.DoesNotExist:
                            self.stdout.write(f'    ⚠ Ingrediente no encontrado: {ingrediente_nombre}')
                    
                    self.stdout.write(f'  ✓ Creado plato: {nombre}')
                    
            except CategoriaMenu.DoesNotExist:
                self.stdout.write(f'    ⚠ Categoría no encontrada: {categoria_nombre}')

        # Crear opciones de personalización para algunos platos
        opciones_data = [
            ('Pizza Margherita', 'Extra queso', '', Decimal('2.00')),
            ('Pizza Margherita', 'Sin cebolla', 'Preparado sin cebolla', Decimal('0.00')),
            ('Pizza Pepperoni', 'Extra pepperoni', '', Decimal('3.00')),
            ('Pizza Pepperoni', 'Masa delgada', 'Preparado con masa delgada', Decimal('0.00')),
            ('Ensalada César', 'Sin crutones', 'Para personas con intolerancia al gluten', Decimal('0.00')),
            ('Ensalada César', 'Extra pollo', '', Decimal('4.00')),
            ('Spaghetti Carbonara', 'Extra queso', '', Decimal('2.00')),
            ('Pollo a la Parrilla', 'Término medio', 'Cocción término medio', Decimal('0.00')),
            ('Pollo a la Parrilla', 'Término bien cocido', 'Cocción bien cocida', Decimal('0.00')),
        ]
        
        for plato_nombre, opcion_nombre, descripcion, precio_adicional in opciones_data:
            try:
                plato = PlatoMenu.objects.get(nombre=plato_nombre)
                opcion, created = OpcionPersonalizacion.objects.get_or_create(
                    plato=plato,
                    nombre=opcion_nombre,
                    defaults={
                        'descripcion': descripcion,
                        'precio_adicional': precio_adicional,
                        'disponible': True
                    }
                )
                if created:
                    self.stdout.write(f'  ✓ Creada opción: {opcion_nombre} para {plato_nombre}')
            except PlatoMenu.DoesNotExist:
                self.stdout.write(f'    ⚠ Plato no encontrado: {plato_nombre}')

        self.stdout.write(
            self.style.SUCCESS('✅ Datos de ejemplo creados exitosamente!')
        )
        self.stdout.write(
            self.style.SUCCESS('Puedes acceder al admin en: http://127.0.0.1:8000/admin/')
        )
        self.stdout.write(
            self.style.SUCCESS('Y ver el menú en: http://127.0.0.1:8000/menu/')
        )
