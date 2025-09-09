from django.core.management.base import BaseCommand
from reservas.models import ConfiguracionRestaurante, TipoMesa, Mesa
from decimal import Decimal

class Command(BaseCommand):
    help = 'Configura el sistema de reservas con datos iniciales'

    def handle(self, *args, **options):
        self.stdout.write('Configurando sistema de reservas...')
        
        # Crear configuración del restaurante
        config, created = ConfiguracionRestaurante.objects.get_or_create(
            nombre="Restaurante GYZ",
            defaults={
                'hora_apertura': '12:00',
                'hora_cierre': '22:00',
                'duracion_turno_minutos': 120,
                'tiempo_minimo_reserva_horas': 2,
                'tiempo_maximo_reserva_dias': 30,
                'dias_cerrado': '',
                'telefono_contacto': '(123) 456-7890',
                'email_contacto': 'reservas@restaurantegyz.com',
                'permite_cancelacion_horas': 4,
            }
        )
        
        if created:
            self.stdout.write('  ✓ Configuración del restaurante creada')
        else:
            self.stdout.write('  ✓ Configuración del restaurante ya existe')
        
        # Crear tipos de mesa
        tipos_mesa_data = [
            ('Mesa para 2', 2, 2, 'Mesa íntima para parejas', Decimal('0.00')),
            ('Mesa para 4', 3, 4, 'Mesa familiar estándar', Decimal('0.00')),
            ('Mesa para 6', 5, 6, 'Mesa para grupos medianos', Decimal('10.00')),
            ('Mesa para 8', 7, 8, 'Mesa para grupos grandes', Decimal('20.00')),
            ('Mesa VIP', 2, 4, 'Mesa VIP con vista especial', Decimal('50.00')),
            ('Mesa de Barra', 1, 2, 'Asientos en la barra', Decimal('0.00')),
        ]
        
        for nombre, cap_min, cap_max, descripcion, precio in tipos_mesa_data:
            tipo, created = TipoMesa.objects.get_or_create(
                nombre=nombre,
                defaults={
                    'capacidad_minima': cap_min,
                    'capacidad_maxima': cap_max,
                    'descripcion': descripcion,
                    'precio_base': precio,
                    'activo': True
                }
            )
            if created:
                self.stdout.write(f'  ✓ Tipo de mesa creado: {nombre}')
        
        # Crear mesas físicas
        mesas_data = [
            # Mesas para 2 - Interior
            ('1', 'Mesa para 2', 'interior'),
            ('2', 'Mesa para 2', 'interior'),
            ('3', 'Mesa para 2', 'ventana'),
            ('4', 'Mesa para 2', 'ventana'),
            
            # Mesas para 4 - Interior
            ('5', 'Mesa para 4', 'interior'),
            ('6', 'Mesa para 4', 'interior'),
            ('7', 'Mesa para 4', 'interior'),
            ('8', 'Mesa para 4', 'ventana'),
            ('9', 'Mesa para 4', 'ventana'),
            
            # Mesas para 6 - Interior y Terraza
            ('10', 'Mesa para 6', 'interior'),
            ('11', 'Mesa para 6', 'terraza'),
            ('12', 'Mesa para 6', 'terraza'),
            
            # Mesas para 8 - Terraza y Privado
            ('13', 'Mesa para 8', 'terraza'),
            ('14', 'Mesa para 8', 'privado'),
            
            # Mesas VIP
            ('VIP1', 'Mesa VIP', 'ventana'),
            ('VIP2', 'Mesa VIP', 'privado'),
            
            # Barra
            ('B1', 'Mesa de Barra', 'barra'),
            ('B2', 'Mesa de Barra', 'barra'),
            ('B3', 'Mesa de Barra', 'barra'),
            ('B4', 'Mesa de Barra', 'barra'),
        ]
        
        for numero, tipo_nombre, ubicacion in mesas_data:
            try:
                tipo_mesa = TipoMesa.objects.get(nombre=tipo_nombre)
                mesa, created = Mesa.objects.get_or_create(
                    numero=numero,
                    defaults={
                        'tipo_mesa': tipo_mesa,
                        'ubicacion': ubicacion,
                        'descripcion': f'Mesa {numero} ubicada en {ubicacion}',
                        'activa': True
                    }
                )
                if created:
                    self.stdout.write(f'  ✓ Mesa creada: {numero} ({tipo_nombre})')
            except TipoMesa.DoesNotExist:
                self.stdout.write(f'  ⚠ Tipo de mesa no encontrado: {tipo_nombre}')
        
        # Estadísticas finales
        total_mesas = Mesa.objects.filter(activa=True).count()
        total_tipos = TipoMesa.objects.filter(activo=True).count()
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ Sistema de reservas configurado exitosamente!')
        )
        self.stdout.write(
            self.style.SUCCESS(f'📊 Resumen:')
        )
        self.stdout.write(f'   - {total_tipos} tipos de mesa')
        self.stdout.write(f'   - {total_mesas} mesas disponibles')
        self.stdout.write(f'   - Horario: {config.hora_apertura} - {config.hora_cierre}')
        self.stdout.write(
            self.style.SUCCESS('🌐 Accede a: http://127.0.0.1:8000/reservas/')
        )
