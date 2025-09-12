#!/usr/bin/env python
"""
Script para poblar la base de datos del chatbot con respuestas predefinidas
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurante_gyz.settings')
django.setup()

from chatbot.models import RespuestaAutomatica

def crear_respuestas_automaticas():
    """Crea respuestas automáticas predefinidas para el chatbot"""
    
    respuestas = [
        {
            'palabras_clave': 'especialidad, especialidades, plato especial, recomendacion, recomendación',
            'respuesta': '🌟 **Nuestras especialidades de la casa:**\n\n• **Paella Valenciana** - Arroz con mariscos frescos y azafrán\n• **Lomo a la Plancha** - Carne premium con guarnición\n• **Salmón Grillado** - Con vegetales de temporada\n• **Risotto de Hongos** - Cremoso y aromático\n\n¿Te interesa alguna de estas opciones?',
            'tipo_accion': 'informacion',
            'prioridad': 10,
            'activa': True
        },
        {
            'palabras_clave': 'vegetariano, vegano, sin carne, opciones vegetales',
            'respuesta': '🥗 **Opciones vegetarianas y veganas:**\n\n• **Ensalada Mediterránea** - Con queso feta y aceitunas\n• **Pasta Primavera** - Con vegetales frescos\n• **Quinoa Bowl** - Súper nutritivo y delicioso\n• **Hamburguesa Vegana** - Con proteína vegetal\n\n¡Tenemos muchas opciones saludables!',
            'tipo_accion': 'informacion',
            'prioridad': 8,
            'activa': True
        },
        {
            'palabras_clave': 'postre, postres, dulce, dulces, dessert',
            'respuesta': '🍰 **Nuestros postres irresistibles:**\n\n• **Tiramisú Casero** - Receta tradicional italiana\n• **Cheesecake de Frutos Rojos** - Cremoso y fresco\n• **Brownie con Helado** - Caliente con helado de vainilla\n• **Flan de Caramelo** - Clásico y delicioso\n\n¿Con cuál te tentamos hoy?',
            'tipo_accion': 'informacion',
            'prioridad': 7,
            'activa': True
        },
        {
            'palabras_clave': 'bebida, bebidas, vino, cerveza, jugo, refresco',
            'respuesta': '🍷 **Nuestra carta de bebidas:**\n\n• **Vinos** - Selección nacional e internacional\n• **Cervezas** - Artesanales y comerciales\n• **Jugos Naturales** - Frescos y vitamínicos\n• **Cócteles** - Preparados por nuestro bartender\n• **Café Premium** - Diferentes preparaciones\n\n¿Qué te apetece tomar?',
            'tipo_accion': 'informacion',
            'prioridad': 6,
            'activa': True
        },
        {
            'palabras_clave': 'delivery, domicilio, entrega, llevar, para llevar',
            'respuesta': '🚚 **Servicio de delivery:**\n\n• **Zona de cobertura:** Toda la ciudad\n• **Tiempo de entrega:** 30-45 minutos\n• **Costo de envío:** $3,000 (gratis en pedidos >$50,000)\n• **Horarios:** Mismo horario del restaurante\n• **Pago:** Efectivo, tarjeta o transferencia\n\n¿Te gustaría hacer un pedido a domicilio?',
            'tipo_accion': 'pedido',
            'requiere_datos': True,
            'prioridad': 9,
            'activa': True
        },
        {
            'palabras_clave': 'cumpleaños, celebracion, celebración, evento, fiesta',
            'respuesta': '🎉 **Celebraciones especiales:**\n\n• **Reservas para grupos** - Mesas especiales\n• **Menú de celebración** - Opciones personalizadas\n• **Decoración incluida** - Para cumpleaños\n• **Torta de cortesía** - En celebraciones especiales\n• **Música ambiente** - Para crear el ambiente perfecto\n\n¿Te gustaría reservar para una celebración?',
            'tipo_accion': 'reserva',
            'requiere_datos': True,
            'prioridad': 8,
            'activa': True
        },
        {
            'palabras_clave': 'wifi, internet, contraseña, password',
            'respuesta': '📶 **WiFi gratuito:**\n\nRed: RestauranteGYZ_WiFi\nContraseña: GYZ2024\n\n¡Conéctate y comparte tus momentos con nosotros! 📸',
            'tipo_accion': 'informacion',
            'prioridad': 3,
            'activa': True
        },
        {
            'palabras_clave': 'estacionamiento, parqueadero, parking, aparcar',
            'respuesta': '🚗 **Estacionamiento:**\n\n• **Disponibilidad:** Amplio parqueadero propio\n• **Costo:** Gratuito para clientes\n• **Seguridad:** Vigilancia 24/7\n• **Capacidad:** 50 vehículos\n• **Acceso:** Entrada por la calle principal\n\n¡No te preocupes por dónde aparcar!',
            'tipo_accion': 'informacion',
            'prioridad': 4,
            'activa': True
        },
        {
            'palabras_clave': 'niños, niño, infantil, kids, familia',
            'respuesta': '👨‍👩‍👧‍👦 **Restaurante familiar:**\n\n• **Menú infantil** - Platos especiales para niños\n• **Sillas altas** - Disponibles\n• **Área de juegos** - Pequeña zona recreativa\n• **Descuentos** - Niños menores de 8 años 50% off\n• **Ambiente familiar** - Perfecto para toda la familia\n\n¡Los niños son bienvenidos!',
            'tipo_accion': 'informacion',
            'prioridad': 5,
            'activa': True
        },
        {
            'palabras_clave': 'alergia, alergias, celiaco, gluten, sin gluten',
            'respuesta': '⚠️ **Información sobre alergias:**\n\n• **Menú sin gluten** - Opciones disponibles\n• **Alergias alimentarias** - Informamos ingredientes\n• **Preparación especial** - Cocina separada si es necesario\n• **Personal capacitado** - Para atender necesidades especiales\n\nPor favor, informa sobre cualquier alergia al hacer tu pedido.',
            'tipo_accion': 'informacion',
            'prioridad': 9,
            'activa': True
        }
    ]
    
    print("Creando respuestas automáticas...")
    
    for respuesta_data in respuestas:
        respuesta, created = RespuestaAutomatica.objects.get_or_create(
            palabras_clave=respuesta_data['palabras_clave'],
            defaults=respuesta_data
        )
        
        if created:
            print(f"✓ Creada: {respuesta_data['palabras_clave'][:50]}...")
        else:
            print(f"- Ya existe: {respuesta_data['palabras_clave'][:50]}...")
    
    print(f"\n¡Proceso completado! Total de respuestas: {RespuestaAutomatica.objects.count()}")

if __name__ == '__main__':
    crear_respuestas_automaticas()