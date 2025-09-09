from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from inventario.models import (
    Proveedor, CategoriaInventario, ProductoInventario, 
    MovimientoInventario, OrdenCompra, ItemOrdenCompra,
    AlertaInventario, RecetaConsumo, TipoMovimiento, EstadoOrden
)
from menu.models import Ingrediente, PlatoMenu
from decimal import Decimal
from django.utils import timezone
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Pobla la base de datos con datos de ejemplo para el sistema de inventario'

    def handle(self, *args, **options):
        self.stdout.write('Poblando sistema de inventario...')
        
        # Crear usuario administrador si no existe
        admin_user, created = User.objects.get_or_create(
            username='admin_inventario',
            defaults={
                'email': 'admin@restaurantegyz.com',
                'first_name': 'Admin',
                'last_name': 'Inventario',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write('  ✓ Usuario administrador creado')
        
        # Crear proveedores
        proveedores_data = [
            {
                'nombre': 'Juan Pérez',
                'empresa': 'Distribuidora La Fresca',
                'email': 'ventas@lafresca.com',
                'telefono': '555-0101',
                'direccion': 'Av. Mercado Central #123',
                'ciudad': 'Ciudad Principal',
                'rfc_cuit': 'PERJ850101ABC',
                'dias_entrega': 2,
                'monto_minimo_pedido': Decimal('500.00'),
                'descuento_volumen': Decimal('5.00'),
            },
            {
                'nombre': 'María González',
                'empresa': 'Carnes Premium S.A.',
                'email': 'pedidos@carnespremium.com',
                'telefono': '555-0102',
                'direccion': 'Zona Industrial #456',
                'ciudad': 'Ciudad Principal',
                'rfc_cuit': 'GONM750615XYZ',
                'dias_entrega': 1,
                'monto_minimo_pedido': Decimal('300.00'),
                'descuento_volumen': Decimal('3.00'),
            },
            {
                'nombre': 'Carlos Rodríguez',
                'empresa': 'Abarrotes El Buen Precio',
                'email': 'carlos@buenprecio.com',
                'telefono': '555-0103',
                'direccion': 'Centro Comercial #789',
                'ciudad': 'Ciudad Secundaria',
                'rfc_cuit': 'RODC820920DEF',
                'dias_entrega': 3,
                'monto_minimo_pedido': Decimal('200.00'),
                'descuento_volumen': Decimal('2.50'),
            },
        ]
        
        proveedores = []
        for proveedor_data in proveedores_data:
            proveedor, created = Proveedor.objects.get_or_create(
                nombre=proveedor_data['nombre'],
                defaults=proveedor_data
            )
            proveedores.append(proveedor)
            if created:
                self.stdout.write(f'  ✓ Proveedor {proveedor.nombre} creado')
        
        # Crear categorías de inventario
        categorias_data = [
            {'nombre': 'Carnes y Aves', 'descripcion': 'Productos cárnicos frescos', 'color': '#dc3545'},
            {'nombre': 'Vegetales', 'descripcion': 'Verduras y hortalizas frescas', 'color': '#28a745'},
            {'nombre': 'Lácteos', 'descripcion': 'Productos lácteos y derivados', 'color': '#fff3cd'},
            {'nombre': 'Granos y Cereales', 'descripcion': 'Arroz, pasta, harinas', 'color': '#ffc107'},
            {'nombre': 'Condimentos', 'descripcion': 'Especias, salsas y condimentos', 'color': '#6f42c1'},
            {'nombre': 'Bebidas', 'descripcion': 'Refrescos, jugos y bebidas', 'color': '#17a2b8'},
            {'nombre': 'Panadería', 'descripcion': 'Panes, tortillas y productos de panadería', 'color': '#fd7e14'},
        ]
        
        categorias = {}
        for cat_data in categorias_data:
            categoria, created = CategoriaInventario.objects.get_or_create(
                nombre=cat_data['nombre'],
                defaults=cat_data
            )
            categorias[cat_data['nombre']] = categoria
            if created:
                self.stdout.write(f'  ✓ Categoría {categoria.nombre} creada')
        
        # Obtener ingredientes existentes
        ingredientes = list(Ingrediente.objects.all())
        
        if not ingredientes:
            self.stdout.write('  ⚠️  No hay ingredientes en el sistema. Ejecuta: python manage.py poblar_menu')
            return
        
        # Crear productos de inventario para cada ingrediente
        productos_config = {
            'Pollo': {
                'categoria': 'Carnes y Aves',
                'unidad_medida': 'kg',
                'stock_actual': Decimal('25.0'),
                'stock_minimo': Decimal('5.0'),
                'stock_maximo': Decimal('50.0'),
                'costo_unitario': Decimal('85.00'),
                'dias_vencimiento': 3,
                'proveedor': 1,
            },
            'Carne de Res': {
                'categoria': 'Carnes y Aves',
                'unidad_medida': 'kg',
                'stock_actual': Decimal('15.0'),
                'stock_minimo': Decimal('3.0'),
                'stock_maximo': Decimal('30.0'),
                'costo_unitario': Decimal('180.00'),
                'dias_vencimiento': 2,
                'proveedor': 1,
            },
            'Tomate': {
                'categoria': 'Vegetales',
                'unidad_medida': 'kg',
                'stock_actual': Decimal('8.0'),
                'stock_minimo': Decimal('10.0'),  # Stock bajo intencionalmente
                'stock_maximo': Decimal('25.0'),
                'costo_unitario': Decimal('25.00'),
                'dias_vencimiento': 5,
                'proveedor': 0,
            },
            'Lechuga': {
                'categoria': 'Vegetales',
                'unidad_medida': 'kg',
                'stock_actual': Decimal('12.0'),
                'stock_minimo': Decimal('5.0'),
                'stock_maximo': Decimal('20.0'),
                'costo_unitario': Decimal('20.00'),
                'dias_vencimiento': 4,
                'proveedor': 0,
            },
            'Cebolla': {
                'categoria': 'Vegetales',
                'unidad_medida': 'kg',
                'stock_actual': Decimal('18.0'),
                'stock_minimo': Decimal('8.0'),
                'stock_maximo': Decimal('30.0'),
                'costo_unitario': Decimal('15.00'),
                'dias_vencimiento': 15,
                'proveedor': 0,
            },
            'Queso': {
                'categoria': 'Lácteos',
                'unidad_medida': 'kg',
                'stock_actual': Decimal('3.0'),
                'stock_minimo': Decimal('2.0'),
                'stock_maximo': Decimal('10.0'),
                'costo_unitario': Decimal('120.00'),
                'dias_vencimiento': 10,
                'proveedor': 2,
            },
            'Arroz': {
                'categoria': 'Granos y Cereales',
                'unidad_medida': 'kg',
                'stock_actual': Decimal('40.0'),
                'stock_minimo': Decimal('15.0'),
                'stock_maximo': Decimal('80.0'),
                'costo_unitario': Decimal('22.00'),
                'dias_vencimiento': 365,
                'proveedor': 2,
            },
            'Aceite': {
                'categoria': 'Condimentos',
                'unidad_medida': 'l',
                'stock_actual': Decimal('6.0'),
                'stock_minimo': Decimal('3.0'),
                'stock_maximo': Decimal('15.0'),
                'costo_unitario': Decimal('45.00'),
                'dias_vencimiento': 180,
                'proveedor': 2,
            },
        }
        
        productos_creados = []
        for ingrediente in ingredientes:
            if ingrediente.nombre in productos_config:
                config = productos_config[ingrediente.nombre]
                
                producto, created = ProductoInventario.objects.get_or_create(
                    ingrediente=ingrediente,
                    defaults={
                        'categoria_inventario': categorias[config['categoria']],
                        'unidad_medida': config['unidad_medida'],
                        'stock_actual': config['stock_actual'],
                        'stock_minimo': config['stock_minimo'],
                        'stock_maximo': config['stock_maximo'],
                        'costo_unitario': config['costo_unitario'],
                        'precio_promedio': config['costo_unitario'],
                        'dias_vencimiento': config['dias_vencimiento'],
                        'proveedor_principal': proveedores[config['proveedor']],
                    }
                )
                productos_creados.append(producto)
                
                if created:
                    self.stdout.write(f'  ✓ Producto {producto.ingrediente.nombre} creado')
                    
                    # Crear movimiento inicial de entrada
                    MovimientoInventario.objects.create(
                        producto=producto,
                        tipo_movimiento=TipoMovimiento.ENTRADA,
                        cantidad=config['stock_actual'],
                        costo_unitario=config['costo_unitario'],
                        stock_anterior=Decimal('0'),
                        stock_nuevo=config['stock_actual'],
                        motivo='Stock inicial del sistema',
                        usuario=admin_user,
                    )
        
        # Crear algunas alertas de ejemplo
        for producto in productos_creados:
            if producto.necesita_reposicion:
                AlertaInventario.objects.get_or_create(
                    producto=producto,
                    tipo_alerta='stock_bajo',
                    activa=True,
                    defaults={
                        'mensaje': f'El stock de {producto.ingrediente.nombre} está por debajo del mínimo ({producto.stock_minimo})'
                    }
                )
        
        # Crear algunas órdenes de compra de ejemplo
        for i, proveedor in enumerate(proveedores[:2]):
            orden = OrdenCompra.objects.create(
                proveedor=proveedor,
                estado=EstadoOrden.BORRADOR if i == 0 else EstadoOrden.ENVIADA,
                creado_por=admin_user,
                notas=f'Orden de ejemplo #{i+1}',
            )
            
            # Agregar algunos items
            productos_proveedor = [p for p in productos_creados if p.proveedor_principal == proveedor]
            for producto in productos_proveedor[:3]:
                ItemOrdenCompra.objects.create(
                    orden=orden,
                    producto=producto,
                    cantidad=Decimal(str(random.randint(5, 20))),
                    precio_unitario=producto.costo_unitario * Decimal('0.95'),  # 5% descuento
                    descripcion=f'{producto.ingrediente.nombre} - Calidad premium',
                )
            
            orden.calcular_totales()
            self.stdout.write(f'  ✓ Orden de compra #{str(orden.numero_orden)[:8]} creada')
        
        # Crear recetas de consumo (relación platos-ingredientes)
        platos = PlatoMenu.objects.all()
        
        # Configuración de consumo por plato (ejemplo)
        consumos_config = {
            'Hamburguesa Clásica': [
                ('Carne de Res', Decimal('0.15')),  # 150g por hamburguesa
                ('Tomate', Decimal('0.05')),       # 50g
                ('Lechuga', Decimal('0.03')),      # 30g
                ('Cebolla', Decimal('0.02')),      # 20g
                ('Queso', Decimal('0.03')),        # 30g
            ],
            'Pollo a la Parrilla': [
                ('Pollo', Decimal('0.20')),        # 200g por porción
                ('Aceite', Decimal('0.01')),       # 10ml
            ],
            'Ensalada César': [
                ('Lechuga', Decimal('0.15')),      # 150g
                ('Queso', Decimal('0.05')),        # 50g
                ('Aceite', Decimal('0.02')),       # 20ml
            ],
            'Arroz con Pollo': [
                ('Pollo', Decimal('0.15')),        # 150g
                ('Arroz', Decimal('0.08')),        # 80g
                ('Aceite', Decimal('0.01')),       # 10ml
                ('Cebolla', Decimal('0.03')),      # 30g
            ],
        }
        
        for plato in platos:
            if plato.nombre in consumos_config:
                for ingrediente_nombre, cantidad in consumos_config[plato.nombre]:
                    try:
                        ingrediente = Ingrediente.objects.get(nombre=ingrediente_nombre)
                        producto = ProductoInventario.objects.get(ingrediente=ingrediente)
                        
                        RecetaConsumo.objects.get_or_create(
                            plato=plato,
                            producto=producto,
                            defaults={'cantidad_necesaria': cantidad}
                        )
                    except (Ingrediente.DoesNotExist, ProductoInventario.DoesNotExist):
                        continue
        
        self.stdout.write('  ✓ Recetas de consumo configuradas')
        
        # Crear algunos movimientos adicionales para simular actividad
        for producto in productos_creados[:4]:
            # Simular algunas salidas
            for _ in range(random.randint(1, 3)):
                cantidad_salida = Decimal(str(random.uniform(0.5, 3.0)))
                if producto.stock_actual >= cantidad_salida:
                    MovimientoInventario.objects.create(
                        producto=producto,
                        tipo_movimiento=TipoMovimiento.SALIDA,
                        cantidad=cantidad_salida,
                        costo_unitario=producto.costo_unitario,
                        stock_anterior=producto.stock_actual,
                        stock_nuevo=producto.stock_actual - cantidad_salida,
                        motivo='Consumo simulado por pedido',
                        usuario=admin_user,
                        fecha=timezone.now() - timezone.timedelta(days=random.randint(1, 7))
                    )
                    producto.stock_actual -= cantidad_salida
                    producto.save()
        
        # Estadísticas finales
        total_productos = ProductoInventario.objects.filter(activo=True).count()
        total_proveedores = Proveedor.objects.filter(activo=True).count()
        total_alertas = AlertaInventario.objects.filter(activa=True).count()
        total_ordenes = OrdenCompra.objects.count()
        
        self.stdout.write(
            self.style.SUCCESS('✅ Sistema de inventario poblado exitosamente!')
        )
        self.stdout.write('')
        self.stdout.write('📊 Resumen:')
        self.stdout.write(f'   - Productos: {total_productos}')
        self.stdout.write(f'   - Proveedores: {total_proveedores}')
        self.stdout.write(f'   - Alertas activas: {total_alertas}')
        self.stdout.write(f'   - Órdenes de compra: {total_ordenes}')
        self.stdout.write(f'   - Categorías: {CategoriaInventario.objects.count()}')
        self.stdout.write('')
        self.stdout.write('🌐 Acceso al sistema:')
        self.stdout.write('   - Dashboard: http://127.0.0.1:8000/inventario/')
        self.stdout.write('   - Admin: http://127.0.0.1:8000/admin/inventario/')
        self.stdout.write(f'   - Usuario: admin_inventario / Contraseña: admin123')
        self.stdout.write('')
        self.stdout.write(
            self.style.WARNING('⚠️  Algunas alertas de stock bajo han sido creadas intencionalmente para demostración.')
        )
