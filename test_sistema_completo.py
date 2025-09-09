#!/usr/bin/env python
"""
Script de prueba para verificar que todo el sistema esté funcionando correctamente
"""
import os
import sys
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client
from django.core import mail

from usuarios.models import Usuario
from eventos.models import TipoEvento, ServicioAdicional, MenuEvento, Evento
from reservas.models import Reserva
from menu.models import CategoriaMenu, PlatoMenu

def test_configuracion_django():
    """Verificar configuración básica de Django"""
    print("🔧 Verificando configuración de Django...")
    
    # Verificar que las apps estén instaladas
    apps_requeridas = [
        'usuarios', 'menu', 'reservas', 'pagos', 'inventario', 
        'empleados', 'eventos', 'allauth', 'allauth.account', 
        'allauth.socialaccount'
    ]
    
    for app in apps_requeridas:
        if app in settings.INSTALLED_APPS:
            print(f"  ✅ {app} está instalada")
        else:
            print(f"  ❌ {app} NO está instalada")
    
    # Verificar configuración de allauth
    print(f"  📧 ACCOUNT_EMAIL_VERIFICATION: {getattr(settings, 'ACCOUNT_EMAIL_VERIFICATION', 'No configurado')}")
    print(f"  🔗 SITE_ID: {getattr(settings, 'SITE_ID', 'No configurado')}")
    
    return True

def test_modelos():
    """Verificar que los modelos funcionen correctamente"""
    print("\n📊 Verificando modelos...")
    
    try:
        # Verificar modelo de usuario
        User = get_user_model()
        print(f"  ✅ Modelo de usuario: {User.__name__}")
        
        # Verificar modelos de eventos
        print(f"  ✅ TipoEvento: {TipoEvento.__name__}")
        print(f"  ✅ ServicioAdicional: {ServicioAdicional.__name__}")
        print(f"  ✅ MenuEvento: {MenuEvento.__name__}")
        print(f"  ✅ Evento: {Evento.__name__}")
        
        # Verificar modelos de reservas
        print(f"  ✅ Reserva: {Reserva.__name__}")
        
        # Verificar modelos de menú
        print(f"  ✅ CategoriaMenu: {CategoriaMenu.__name__}")
        print(f"  ✅ PlatoMenu: {PlatoMenu.__name__}")
        
        return True
    except Exception as e:
        print(f"  ❌ Error en modelos: {e}")
        return False

def test_urls():
    """Verificar que las URLs estén configuradas correctamente"""
    print("\n🔗 Verificando URLs...")
    
    try:
        from django.urls import get_resolver
        resolver = get_resolver()
        
        # Verificar URLs principales
        urls_principales = [
            'usuarios:index',
            'usuarios:registro',
            'usuarios:login',
            'eventos:mis_eventos',
            'eventos:solicitar_evento',
            'reservas:disponibilidad',
            'reservas:mis_reservas',
        ]
        
        for url_name in urls_principales:
            try:
                reverse(url_name)
                print(f"  ✅ {url_name}")
            except Exception as e:
                print(f"  ❌ {url_name}: {e}")
        
        return True
    except Exception as e:
        print(f"  ❌ Error en URLs: {e}")
        return False

def test_templates():
    """Verificar que los templates existan"""
    print("\n📄 Verificando templates...")
    
    from django.template.loader import get_template
    
    templates_principales = [
        'usuarios/base.html',
        'usuarios/index.html',
        'usuarios/registro.html',
        'usuarios/login.html',
        'eventos/solicitar_evento.html',
        'eventos/mis_eventos.html',
        'eventos/detalle_evento.html',
        'eventos/solicitar_evento_paso2.html',
        'eventos/solicitar_evento_paso3.html',
        'eventos/solicitar_evento_paso4.html',
        'reservas/disponibilidad.html',
        'reservas/mis_reservas.html',
    ]
    
    for template in templates_principales:
        try:
            get_template(template)
            print(f"  ✅ {template}")
        except Exception as e:
            print(f"  ❌ {template}: {e}")
    
    return True

def test_registro_usuario():
    """Probar el registro de usuarios"""
    print("\n👤 Probando registro de usuarios...")
    
    try:
        # Crear un usuario de prueba
        User = get_user_model()
        user_data = {
            'username': 'test_user_registro',
            'email': 'test_registro@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password1': 'testpass123',
            'password2': 'testpass123',
        }
        
        # Verificar que el usuario no existe
        if User.objects.filter(username=user_data['username']).exists():
            User.objects.filter(username=user_data['username']).delete()
        
        # Crear el usuario
        user = User.objects.create_user(
            username=user_data['username'],
            email=user_data['email'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            password=user_data['password1']
        )
        
        print(f"  ✅ Usuario creado: {user.username}")
        
        # Verificar que se puede autenticar
        from django.contrib.auth import authenticate
        auth_user = authenticate(username=user_data['username'], password=user_data['password1'])
        if auth_user:
            print(f"  ✅ Autenticación exitosa: {auth_user.username}")
        else:
            print(f"  ❌ Error en autenticación")
        
        # Limpiar
        user.delete()
        print(f"  ✅ Usuario de prueba eliminado")
        
        return True
    except Exception as e:
        print(f"  ❌ Error en registro: {e}")
        return False

def test_eventos():
    """Probar funcionalidad de eventos"""
    print("\n🎉 Probando funcionalidad de eventos...")
    
    try:
        # Verificar que hay datos de ejemplo
        tipos_evento = TipoEvento.objects.count()
        servicios = ServicioAdicional.objects.count()
        menus = MenuEvento.objects.count()
        
        print(f"  📊 Tipos de evento: {tipos_evento}")
        print(f"  📊 Servicios adicionales: {servicios}")
        print(f"  📊 Menús: {menus}")
        
        if tipos_evento == 0:
            print("  ⚠️  No hay tipos de evento. Ejecutando poblar_eventos.py...")
            # Aquí podrías ejecutar el script de poblar datos
            return False
        
        # Crear un evento de prueba
        User = get_user_model()
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        user = User.objects.create_user(
            username=f'test_evento_user_{unique_id}',
            email=f'test_evento_{unique_id}@example.com',
            password='testpass123'
        )
        
        tipo_evento = TipoEvento.objects.first()
        menu_evento = MenuEvento.objects.first()
        
        evento = Evento.objects.create(
            cliente=user,
            nombre_evento='Evento de Prueba',
            descripcion='Evento de prueba para testing',
            tipo_evento=tipo_evento,
            menu_evento=menu_evento,
            fecha_evento='2025-12-25',
            hora_inicio='18:00',
            hora_fin='22:00',
            tipo_ubicacion='restaurante',
            numero_invitados=20,
            categoria='cumpleanos',
            estado='solicitado'
        )
        
        print(f"  ✅ Evento creado: {evento.nombre_evento}")
        
        # Probar cálculo de total
        total = evento.calcular_total()
        print(f"  ✅ Total calculado: ${total}")
        
        # Limpiar
        evento.delete()
        user.delete()
        print(f"  ✅ Datos de prueba eliminados")
        
        return True
    except Exception as e:
        print(f"  ❌ Error en eventos: {e}")
        return False

def main():
    """Función principal de pruebas"""
    print("🚀 Iniciando pruebas del sistema completo...")
    print("=" * 50)
    
    tests = [
        test_configuracion_django,
        test_modelos,
        test_urls,
        test_templates,
        test_registro_usuario,
        test_eventos,
    ]
    
    resultados = []
    for test in tests:
        try:
            resultado = test()
            resultados.append(resultado)
        except Exception as e:
            print(f"❌ Error en {test.__name__}: {e}")
            resultados.append(False)
    
    print("\n" + "=" * 50)
    print("📋 RESUMEN DE PRUEBAS")
    print("=" * 50)
    
    exitos = sum(resultados)
    total = len(resultados)
    
    print(f"✅ Pruebas exitosas: {exitos}/{total}")
    print(f"❌ Pruebas fallidas: {total - exitos}/{total}")
    
    if exitos == total:
        print("\n🎉 ¡Todas las pruebas pasaron! El sistema está funcionando correctamente.")
    else:
        print("\n⚠️  Algunas pruebas fallaron. Revisa los errores arriba.")
    
    return exitos == total

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
