#!/usr/bin/env python
"""
Script de debug para identificar problemas en el registro
"""
import os
import sys
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from usuarios.forms import RegistroUsuarioForm

User = get_user_model()

def debug_registro():
    """Debug del proceso de registro"""
    print("🔍 Debug del registro de usuarios...")
    
    # 1. Verificar formulario
    print("\n1. Probando formulario...")
    datos = {
        'username': 'debug_user',
        'email': 'debug@example.com',
        'first_name': 'Debug',
        'last_name': 'User',
        'password1': 'testpass123',
        'password2': 'testpass123',
    }
    
    form = RegistroUsuarioForm(data=datos)
    if form.is_valid():
        print("  ✅ Formulario válido")
        print(f"  📝 Datos limpios: {form.cleaned_data}")
    else:
        print(f"  ❌ Formulario inválido: {form.errors}")
        return
    
    # 2. Verificar creación de usuario
    print("\n2. Probando creación de usuario...")
    try:
        user = form.save()
        print(f"  ✅ Usuario creado: {user.username}")
        print(f"  📧 Email: {user.email}")
        print(f"  🔐 Contraseña hasheada: {user.password[:20]}...")
        
        # Limpiar
        user.delete()
        print("  ✅ Usuario eliminado")
    except Exception as e:
        print(f"  ❌ Error creando usuario: {e}")
        return
    
    # 3. Probar con cliente HTTP
    print("\n3. Probando con cliente HTTP...")
    client = Client()
    
    # GET
    response = client.get(reverse('usuarios:registro'))
    print(f"  📄 GET /registro/: {response.status_code}")
    
    # POST
    response = client.post(reverse('usuarios:registro'), datos)
    print(f"  📤 POST /registro/: {response.status_code}")
    
    if response.status_code == 302:
        print(f"  🔄 Redirección a: {response.url}")
    elif response.status_code == 200:
        print("  ⚠️  No redirigió (posible error en formulario)")
        # Verificar si hay errores en el contexto
        if hasattr(response, 'context') and response.context:
            form_in_response = response.context.get('form')
            if form_in_response and form_in_response.errors:
                print(f"  ❌ Errores en formulario: {form_in_response.errors}")
    else:
        print(f"  ❌ Error inesperado: {response.status_code}")
    
    # 4. Verificar configuración
    print("\n4. Verificando configuración...")
    print(f"  🔧 AUTHENTICATION_BACKENDS: {settings.AUTHENTICATION_BACKENDS}")
    print(f"  🔧 AUTH_USER_MODEL: {settings.AUTH_USER_MODEL}")
    print(f"  🔧 LOGIN_REDIRECT_URL: {getattr(settings, 'LOGIN_REDIRECT_URL', 'No configurado')}")
    print(f"  🔧 ACCOUNT_LOGIN_REDIRECT_URL: {getattr(settings, 'ACCOUNT_LOGIN_REDIRECT_URL', 'No configurado')}")

if __name__ == '__main__':
    debug_registro()
