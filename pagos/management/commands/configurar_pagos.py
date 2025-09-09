from django.core.management.base import BaseCommand
from pagos.models import ConfiguracionPagos
from decimal import Decimal

class Command(BaseCommand):
    help = 'Configura el sistema de pagos con valores por defecto'

    def handle(self, *args, **options):
        self.stdout.write('Configurando sistema de pagos...')
        
        # Crear configuración de pagos
        config, created = ConfiguracionPagos.objects.get_or_create(
            defaults={
                # Stripe (usar claves de test)
                'stripe_public_key': 'pk_test_51...', # Aquí pondrías tu clave pública de test
                'stripe_secret_key': 'sk_test_51...', # Aquí pondrías tu clave secreta de test  
                'stripe_webhook_secret': 'whsec_...', # Aquí pondrías tu webhook secret
                'stripe_activo': False,  # Desactivado por defecto hasta configurar claves reales
                
                # PayPal (usar sandbox)
                'paypal_client_id': 'AYour_PayPal_Client_ID_Here',
                'paypal_client_secret': 'EYour_PayPal_Client_Secret_Here',
                'paypal_sandbox': True,
                'paypal_activo': False,  # Desactivado por defecto
                
                # MercadoPago (sandbox)
                'mercadopago_access_token': 'TEST-1234567890-123456-abcdefghijklmnop-123456789',
                'mercadopago_public_key': 'TEST-1234567890-123456-abcdefghijklmnop',
                'mercadopago_sandbox': True,
                'mercadopago_activo': False,  # Desactivado por defecto
                
                # Comisiones
                'comision_tarjeta': Decimal('3.50'),
                'comision_paypal': Decimal('3.49'),
                
                # Límites
                'pago_minimo': Decimal('5.00'),
                'pago_maximo_efectivo': Decimal('1000.00'),
                
                # Datos de facturación
                'razon_social': 'Restaurante GYZ S.A.',
                'rfc_cuit': 'GYZ123456789',
                'direccion_fiscal': 'Av. Principal #123, Ciudad, País',
                'telefono_facturacion': '(123) 456-7890',
                'email_facturacion': 'facturacion@restaurantegyz.com',
                
                # Facturación automática
                'facturacion_automatica': True,
                'incluir_iva': True,
                'porcentaje_iva': Decimal('16.00'),
            }
        )
        
        if created:
            self.stdout.write('  ✓ Configuración de pagos creada')
        else:
            self.stdout.write('  ✓ Configuración de pagos ya existe')
        
        self.stdout.write(
            self.style.SUCCESS('✅ Sistema de pagos configurado!')
        )
        
        self.stdout.write(
            self.style.WARNING('⚠️  IMPORTANTE:')
        )
        self.stdout.write('Para usar pagos con tarjeta, configura las claves reales de:')
        self.stdout.write('1. Stripe: https://dashboard.stripe.com/apikeys')
        self.stdout.write('2. PayPal: https://developer.paypal.com/')
        self.stdout.write('3. MercadoPago: https://www.mercadopago.com/developers/')
        self.stdout.write('')
        self.stdout.write('Por ahora solo funcionará el pago en EFECTIVO.')
        self.stdout.write('')
        self.stdout.write('📊 Configuración actual:')
        self.stdout.write(f'   - Stripe: {"✅ Activo" if config.stripe_activo else "❌ Inactivo"}')
        self.stdout.write(f'   - PayPal: {"✅ Activo" if config.paypal_activo else "❌ Inactivo"}')
        self.stdout.write(f'   - MercadoPago: {"✅ Activo" if config.mercadopago_activo else "❌ Inactivo"}')
        self.stdout.write(f'   - Efectivo: ✅ Activo (hasta ${config.pago_maximo_efectivo})')
        self.stdout.write('')
        self.stdout.write(
            self.style.SUCCESS('🌐 Panel de configuración: http://127.0.0.1:8000/admin/pagos/configuracionpagos/')
        )
