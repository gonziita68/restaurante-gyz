from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
import json
import uuid
import re
from .models import Conversacion, Mensaje, RespuestaAutomatica, SolicitudChatbot
from menu.models import PlatoMenu, CategoriaMenu
from reservas.models import Mesa, Reserva
from pedidos.models import Pedido, ItemPedido
from django.utils import timezone
from datetime import datetime, timedelta
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User

class ChatBotService:
    @staticmethod
    def obtener_respuesta(mensaje, session_id):
        mensaje_lower = mensaje.lower()
        conversacion = Conversacion.objects.get(session_id=session_id)
        
        # Detectar intención y procesar
        intencion = ChatBotService.detectar_intencion(mensaje_lower)
        
        if intencion == 'saludo':
            return "¡Hola! Bienvenido al Restaurante GYZ. ¿En qué puedo ayudarte hoy? Puedo ayudarte con información sobre nuestro menú, reservas, pedidos, horarios y más."
        
        elif intencion == 'menu':
            return ChatBotService.procesar_consulta_menu(mensaje_lower)
        
        elif intencion == 'reserva':
            return ChatBotService.procesar_reserva(mensaje, conversacion)
        
        elif intencion == 'pedido':
            return ChatBotService.procesar_pedido(mensaje, conversacion)
        
        elif intencion == 'horario':
            return "Nuestros horarios son:\n\n🕐 **Lunes a Viernes:** 12:00 PM - 10:00 PM\n🕐 **Sábados y Domingos:** 11:00 AM - 11:00 PM\n\n¡Te esperamos!"
        
        elif intencion == 'ubicacion':
            return "📍 **Nuestra ubicación:**\nEstamos ubicados en el centro de la ciudad.\n\n🚗 Contamos con estacionamiento disponible\n🚌 Fácil acceso en transporte público\n\n¿Necesitas indicaciones específicas?"
        
        elif intencion == 'precios':
            return "Nuestros precios varían según el plato:\n\n💰 **Entradas:** $8,000 - $15,000\n💰 **Platos principales:** $18,000 - $35,000\n💰 **Postres:** $6,000 - $12,000\n💰 **Bebidas:** $3,000 - $8,000\n\n¿Te interesa alguna categoría en particular?"
        
        elif intencion == 'contacto':
            return "📞 **Información de contacto:**\n\nTeléfono: +57 (1) 234-5678\nWhatsApp: +57 300 123 4567\nEmail: info@restaurantegyz.com\n\n¿En qué más puedo ayudarte?"
        
        # Buscar respuestas automáticas personalizadas
        respuestas = RespuestaAutomatica.objects.filter(activa=True).order_by('-prioridad')
        for respuesta in respuestas:
            palabras_clave = [palabra.strip().lower() for palabra in respuesta.palabras_clave.split(',')]
            if any(palabra in mensaje_lower for palabra in palabras_clave):
                return respuesta.respuesta
        
        # Respuesta por defecto
        return "Gracias por tu mensaje. Soy el asistente virtual del Restaurante GYZ. Puedo ayudarte con información sobre:\n\n🍽️ Nuestro menú y platos\n📅 Reservas y disponibilidad\n🕐 Horarios de atención\n📍 Ubicación y contacto\n💰 Precios\n🛒 Realizar pedidos\n\n¿Sobre qué te gustaría saber más?"
    
    @staticmethod
    def detectar_intencion(mensaje):
        """Detecta la intención del usuario basada en palabras clave"""
        if any(palabra in mensaje for palabra in ['hola', 'buenos días', 'buenas tardes', 'buenas noches', 'hi', 'hello']):
            return 'saludo'
        elif any(palabra in mensaje for palabra in ['menú', 'menu', 'platos', 'comida', 'carta']):
            return 'menu'
        elif any(palabra in mensaje for palabra in ['reserva', 'reservar', 'mesa', 'disponibilidad']):
            return 'reserva'
        elif any(palabra in mensaje for palabra in ['pedido', 'pedir', 'ordenar', 'comprar', 'llevar']):
            return 'pedido'
        elif any(palabra in mensaje for palabra in ['horario', 'horarios', 'abierto', 'cerrado', 'hora']):
            return 'horario'
        elif any(palabra in mensaje for palabra in ['ubicación', 'ubicacion', 'dirección', 'direccion', 'donde', 'dónde']):
            return 'ubicacion'
        elif any(palabra in mensaje for palabra in ['precio', 'precios', 'costo', 'cuanto', 'cuánto']):
            return 'precios'
        elif any(palabra in mensaje for palabra in ['contacto', 'teléfono', 'telefono', 'llamar']):
            return 'contacto'
        else:
            return 'general'
    
    @staticmethod
    def procesar_consulta_menu(mensaje):
        """Procesa consultas sobre el menú"""
        platos_destacados = PlatoMenu.objects.filter(destacado=True)[:3]
        if platos_destacados:
            respuesta = "Aquí tienes algunos de nuestros platos destacados:\n\n"
            for plato in platos_destacados:
                respuesta += f"🍽️ **{plato.nombre}** - ${plato.precio}\n{plato.descripcion}\n\n"
            respuesta += "¿Te gustaría hacer un pedido o saber más sobre algún plato?"
            return respuesta
        return "Tenemos una gran variedad de platos deliciosos. ¿Hay algún tipo de comida específica que te interese?"
    
    @staticmethod
    def procesar_reserva(mensaje, conversacion):
        """Procesa solicitudes de reserva"""
        # Extraer información de la reserva
        datos_reserva = ChatBotService.extraer_datos_reserva(mensaje)
        
        if datos_reserva['completo']:
            # Crear solicitud de reserva
            solicitud = SolicitudChatbot.objects.create(
                conversacion=conversacion,
                tipo_solicitud='reserva',
                datos_solicitud=datos_reserva,
                estado='procesando'
            )
            
            # Procesar la reserva
            resultado = ChatBotService.crear_reserva_automatica(datos_reserva, solicitud)
            return resultado
        else:
            # Solicitar datos faltantes
            return ChatBotService.solicitar_datos_reserva(datos_reserva)
    
    @staticmethod
    def procesar_pedido(mensaje, conversacion):
        """Procesa solicitudes de pedido"""
        # Extraer información del pedido
        datos_pedido = ChatBotService.extraer_datos_pedido(mensaje)
        
        if datos_pedido['completo']:
            # Crear solicitud de pedido
            solicitud = SolicitudChatbot.objects.create(
                conversacion=conversacion,
                tipo_solicitud='pedido',
                datos_solicitud=datos_pedido,
                estado='procesando'
            )
            
            # Procesar el pedido
            resultado = ChatBotService.crear_pedido_automatico(datos_pedido, solicitud)
            return resultado
        else:
            # Solicitar datos faltantes
            return ChatBotService.solicitar_datos_pedido(datos_pedido)
    
    @staticmethod
    def extraer_datos_reserva(mensaje):
        """Extrae datos de reserva del mensaje"""
        datos = {
            'personas': None,
            'fecha': None,
            'hora': None,
            'nombre': None,
            'telefono': None,
            'email': None,
            'completo': False
        }
        
        # Extraer número de personas
        numeros = re.findall(r'\b(\d+)\b', mensaje)
        if numeros:
            datos['personas'] = int(numeros[0])
        
        # Extraer fecha (formato básico)
        fechas = re.findall(r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b', mensaje)
        if fechas:
            datos['fecha'] = fechas[0]
        
        # Extraer hora
        horas = re.findall(r'\b(\d{1,2}:\d{2})\b', mensaje)
        if horas:
            datos['hora'] = horas[0]
        
        # Extraer email
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', mensaje)
        if emails:
            datos['email'] = emails[0]
        
        # Extraer teléfono
        telefonos = re.findall(r'\b\d{10,}\b', mensaje)
        if telefonos:
            datos['telefono'] = telefonos[0]
        
        # Verificar si está completo
        datos['completo'] = all([datos['personas'], datos['fecha'], datos['hora'], datos['email']])
        
        return datos
    
    @staticmethod
    def extraer_datos_pedido(mensaje):
        """Extrae datos de pedido del mensaje"""
        datos = {
            'platos': [],
            'nombre': None,
            'telefono': None,
            'email': None,
            'direccion': None,
            'completo': False
        }
        
        # Buscar platos mencionados
        platos = PlatoMenu.objects.all()
        for plato in platos:
            if plato.nombre.lower() in mensaje.lower():
                datos['platos'].append({
                    'id': plato.id,
                    'nombre': plato.nombre,
                    'precio': float(plato.precio)
                })
        
        # Extraer email
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', mensaje)
        if emails:
            datos['email'] = emails[0]
        
        # Extraer teléfono
        telefonos = re.findall(r'\b\d{10,}\b', mensaje)
        if telefonos:
            datos['telefono'] = telefonos[0]
        
        # Verificar si está completo
        datos['completo'] = all([datos['platos'], datos['email']])
        
        return datos
    
    @staticmethod
    def solicitar_datos_reserva(datos):
        """Solicita datos faltantes para la reserva"""
        faltantes = []
        if not datos['personas']:
            faltantes.append('número de personas')
        if not datos['fecha']:
            faltantes.append('fecha (DD/MM/AAAA)')
        if not datos['hora']:
            faltantes.append('hora (HH:MM)')
        if not datos['email']:
            faltantes.append('email de contacto')
        
        return f"Para completar tu reserva, necesito que me proporciones: {', '.join(faltantes)}.\n\nPor favor, envía toda la información en un solo mensaje."
    
    @staticmethod
    def solicitar_datos_pedido(datos):
        """Solicita datos faltantes para el pedido"""
        if not datos['platos']:
            return "¿Qué platos te gustaría pedir? Puedes ver nuestro menú completo o decirme qué tipo de comida prefieres."
        elif not datos['email']:
            return "Para procesar tu pedido, necesito tu email de contacto. Por favor proporciónamelo."
        else:
            return "Para completar tu pedido, necesito tu información de contacto completa (nombre, teléfono, email y dirección de entrega)."
    
    @staticmethod
    def crear_reserva_automatica(datos, solicitud):
        """Crea una reserva automáticamente"""
        try:
            # Crear usuario temporal si no existe
            email = datos['email']
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'username': email,
                    'first_name': datos.get('nombre', 'Cliente Chatbot')
                }
            )
            
            # Parsear fecha y hora
            fecha_str = datos['fecha']
            hora_str = datos['hora']
            
            # Crear la reserva
            reserva = Reserva.objects.create(
                usuario=user,
                fecha=datetime.strptime(fecha_str, '%d/%m/%Y').date(),
                hora=datetime.strptime(hora_str, '%H:%M').time(),
                numero_personas=datos['personas'],
                estado='confirmada',
                observaciones='Reserva creada por chatbot'
            )
            
            # Enviar email de confirmación
            ChatBotService.enviar_email_reserva(reserva)
            
            # Actualizar solicitud
            solicitud.estado = 'completada'
            solicitud.resultado = f'Reserva creada con ID: {reserva.id}'
            solicitud.fecha_procesamiento = timezone.now()
            solicitud.save()
            
            return f"¡Perfecto! Tu reserva ha sido confirmada:\n\n📅 **Fecha:** {fecha_str}\n🕐 **Hora:** {hora_str}\n👥 **Personas:** {datos['personas']}\n📧 **Confirmación enviada a:** {email}\n\n¡Te esperamos en el Restaurante GYZ!"
            
        except Exception as e:
            solicitud.estado = 'error'
            solicitud.resultado = str(e)
            solicitud.save()
            return f"Lo siento, hubo un error al procesar tu reserva. Por favor, intenta nuevamente o contáctanos directamente al teléfono del restaurante."
    
    @staticmethod
    def crear_pedido_automatico(datos, solicitud):
        """Crea un pedido automáticamente"""
        try:
            # Crear usuario temporal si no existe
            email = datos['email']
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'username': email,
                    'first_name': datos.get('nombre', 'Cliente Chatbot')
                }
            )
            
            # Calcular total
            total = sum(plato['precio'] for plato in datos['platos'])
            
            # Crear el pedido
            pedido = Pedido.objects.create(
                usuario=user,
                total=total,
                estado='pendiente',
                tipo_entrega='domicilio',
                direccion_entrega=datos.get('direccion', 'Por confirmar'),
                observaciones='Pedido creado por chatbot'
            )
            
            # Crear detalles del pedido
            for plato_data in datos['platos']:
                plato = PlatoMenu.objects.get(id=plato_data['id'])
                ItemPedido.objects.create(
                    pedido=pedido,
                    plato=plato,
                    cantidad=1,
                    precio_unitario=plato.precio
                )
            
            # Enviar email de confirmación
            ChatBotService.enviar_email_pedido(pedido)
            
            # Actualizar solicitud
            solicitud.estado = 'completada'
            solicitud.resultado = f'Pedido creado con ID: {pedido.id}'
            solicitud.fecha_procesamiento = timezone.now()
            solicitud.save()
            
            platos_texto = '\n'.join([f"• {plato['nombre']} - ${plato['precio']}" for plato in datos['platos']])
            
            return f"¡Excelente! Tu pedido ha sido recibido:\n\n🍽️ **Platos:**\n{platos_texto}\n\n💰 **Total:** ${total}\n📧 **Confirmación enviada a:** {email}\n\nTu pedido será procesado y te contactaremos pronto para confirmar la entrega."
            
        except Exception as e:
            solicitud.estado = 'error'
            solicitud.resultado = str(e)
            solicitud.save()
            return f"Lo siento, hubo un error al procesar tu pedido. Por favor, intenta nuevamente o contáctanos directamente."
    
    @staticmethod
    def enviar_email_reserva(reserva):
        """Envía email de confirmación de reserva"""
        try:
            asunto = f'Confirmación de Reserva - Restaurante GYZ'
            mensaje = f'''
            Estimado/a {reserva.usuario.first_name},
            
            Tu reserva ha sido confirmada con los siguientes detalles:
            
            Fecha: {reserva.fecha}
            Hora: {reserva.hora}
            Número de personas: {reserva.numero_personas}
            
            ¡Te esperamos en el Restaurante GYZ!
            
            Saludos cordiales,
            Equipo Restaurante GYZ
            '''
            
            send_mail(
                asunto,
                mensaje,
                settings.DEFAULT_FROM_EMAIL,
                [reserva.usuario.email],
                fail_silently=False,
            )
        except Exception as e:
            print(f"Error enviando email de reserva: {e}")
    
    @staticmethod
    def enviar_email_pedido(pedido):
        """Envía email de confirmación de pedido"""
        try:
            asunto = f'Confirmación de Pedido - Restaurante GYZ'
            
            detalles = '\n'.join([
                f"- {item.plato.nombre} x{item.cantidad} - ${item.precio_unitario}"
                for item in pedido.items.all()
            ])
            
            mensaje = f'''
            Estimado/a {pedido.usuario.first_name},
            
            Tu pedido ha sido recibido con los siguientes detalles:
            
            {detalles}
            
            Total: ${pedido.total}
            Dirección de entrega: {pedido.direccion_entrega}
            
            Te contactaremos pronto para confirmar la entrega.
            
            Saludos cordiales,
            Equipo Restaurante GYZ
            '''
            
            send_mail(
                asunto,
                mensaje,
                settings.DEFAULT_FROM_EMAIL,
                [pedido.usuario.email],
                fail_silently=False,
            )
        except Exception as e:
            print(f"Error enviando email de pedido: {e}")
        for respuesta in respuestas:
            palabras_clave = [palabra.strip().lower() for palabra in respuesta.palabras_clave.split(',')]
            if any(palabra in mensaje_lower for palabra in palabras_clave):
                return respuesta.respuesta
        
        # Respuesta por defecto
        return "Gracias por tu mensaje. Soy el asistente virtual del Restaurante GYZ. Puedo ayudarte con información sobre:\n\n🍽️ Nuestro menú y platos\n📅 Reservas y disponibilidad\n🕐 Horarios de atención\n📍 Ubicación y contacto\n💰 Precios\n\n¿Sobre qué te gustaría saber más?"

@method_decorator(csrf_exempt, name='dispatch')
class ChatBotView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            mensaje = data.get('mensaje', '').strip()
            session_id = data.get('session_id')
            
            if not mensaje:
                return JsonResponse({'error': 'Mensaje vacío'}, status=400)
            
            if not session_id:
                session_id = str(uuid.uuid4())
            
            # Obtener o crear conversación
            conversacion, created = Conversacion.objects.get_or_create(
                session_id=session_id,
                defaults={'activa': True}
            )
            
            # Guardar mensaje del usuario
            Mensaje.objects.create(
                conversacion=conversacion,
                tipo='usuario',
                contenido=mensaje
            )
            
            # Obtener respuesta del bot
            respuesta = ChatBotService.obtener_respuesta(mensaje, session_id)
            
            # Guardar respuesta del bot
            Mensaje.objects.create(
                conversacion=conversacion,
                tipo='bot',
                contenido=respuesta
            )
            
            return JsonResponse({
                'respuesta': respuesta,
                'session_id': session_id,
                'timestamp': timezone.now().isoformat()
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON inválido'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    def get(self, request):
        return JsonResponse({'message': 'Chatbot API funcionando correctamente'})

def chatbot_widget(request):
    """Vista para mostrar el widget del chatbot"""
    return render(request, 'chatbot/widget.html')
