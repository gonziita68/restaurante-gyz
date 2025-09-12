#!/usr/bin/env python
"""
Script para poblar el chatbot con respuestas automáticas predefinidas
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from chatbot.models import RespuestaAutomatica

def crear_respuestas_automaticas():
    """Crear respuestas automáticas predefinidas para el chatbot"""
    
    respuestas = [
        {
            'palabras_clave': 'wifi, internet, contraseña, password, clave',
            'respuesta': '📶 **WiFi Gratuito**\n\nNombre de red: RestauranteGYZ_WiFi\nContraseña: GYZ2024\n\n¡Disfruta de internet gratuito mientras comes!',
            'prioridad': 5
        },
        {
            'palabras_clave': 'delivery, domicilio, entrega, llevar',
            'respuesta': '🚚 **Servicio de Delivery**\n\nOfrecemos servicio a domicilio en un radio de 5km.\n\n⏰ Tiempo de entrega: 30-45 minutos\n💰 Costo de envío: $3,000\n📞 Para pedidos: +57 300 123 4567\n\n¿Te gustaría hacer un pedido?',
            'prioridad': 8
        },
        {
            'palabras_clave': 'cumpleaños, celebración, evento, fiesta',
            'respuesta': '🎉 **Celebraciones Especiales**\n\n¡Hacemos tu celebración inolvidable!\n\n🎂 Tortas personalizadas\n🎈 Decoración especial\n🎵 Música ambiente\n👥 Reservas para grupos\n\n¿Cuántas personas serían y para qué fecha?',
            'prioridad': 6
        },
        {
            'palabras_clave': 'vegetariano, vegano, sin gluten, celíaco, alérgico',
            'respuesta': '🥗 **Opciones Especiales**\n\nTenemos opciones para todos:\n\n🌱 Platos vegetarianos y veganos\n🚫 Opciones sin gluten\n⚠️ Manejo cuidadoso de alérgenos\n\nInforma a tu mesero sobre cualquier alergia o restricción alimentaria.',
            'prioridad': 7
        },
        {
            'palabras_clave': 'estacionamiento, parqueo, carro, vehículo',
            'respuesta': '🚗 **Estacionamiento**\n\nContamos con:\n\n✅ Estacionamiento gratuito\n✅ Espacios cubiertos\n✅ Vigilancia 24/7\n✅ Fácil acceso\n\n¡No te preocupes por tu vehículo!',
            'prioridad': 4
        },
        {
            'palabras_clave': 'niños, infantil, menú niños, kids',
            'respuesta': '👶 **Menú Infantil**\n\nPerfecto para los más pequeños:\n\n🍗 Nuggets de pollo\n🍝 Pasta con mantequilla\n🍕 Mini pizza\n🥤 Jugos naturales\n🍦 Helados\n\n¡También tenemos sillas altas disponibles!',
            'prioridad': 5
        },
        {
            'palabras_clave': 'música, ambiente, terraza, aire libre',
            'respuesta': '🎵 **Ambiente y Música**\n\nDisfruta de:\n\n🎶 Música en vivo los fines de semana\n🌿 Terraza al aire libre\n🕯️ Ambiente romántico\n❄️ Aire acondicionado\n\n¡El lugar perfecto para cualquier ocasión!',
            'prioridad': 3
        },
        {
            'palabras_clave': 'tarjeta, efectivo, pago, visa, mastercard',
            'respuesta': '💳 **Métodos de Pago**\n\nAceptamos:\n\n💵 Efectivo\n💳 Tarjetas de crédito y débito\n📱 Pagos móviles\n🏦 Transferencias bancarias\n\n¡Paga como prefieras!',
            'prioridad': 6
        }
    ]
    
    print("Creando respuestas automáticas para el chatbot...")
    
    for respuesta_data in respuestas:
        respuesta, created = RespuestaAutomatica.objects.get_or_create(
            palabras_clave=respuesta_data['palabras_clave'],
            defaults={
                'respuesta': respuesta_data['respuesta'],
                'prioridad': respuesta_data['prioridad'],
                'activa': True
            }
        )
        
        if created:
            print(f"✅ Creada: {respuesta_data['palabras_clave'][:30]}...")
        else:
            print(f"⚠️ Ya existe: {respuesta_data['palabras_clave'][:30]}...")
    
    print(f"\n🎉 ¡Proceso completado! Se han configurado {len(respuestas)} respuestas automáticas.")
    print("\n📝 Puedes agregar más respuestas desde el panel de administración de Django.")

if __name__ == '__main__':
    crear_respuestas_automaticas()