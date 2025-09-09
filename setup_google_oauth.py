#!/usr/bin/env python
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp

# Actualizar el sitio
site = Site.objects.get(id=1)
site.domain = 'localhost:8000'
site.name = 'Restaurante GYZ'
site.save()

# Crear aplicación social de Google (con credenciales de prueba)
try:
    google_app = SocialApp.objects.get(provider='google')
    print(f"Aplicación social existente: {google_app.name}")
except SocialApp.DoesNotExist:
    google_app = SocialApp.objects.create(
        provider='google',
        name='Google OAuth',
        client_id='123456789-test.apps.googleusercontent.com',  # Credencial de prueba
        secret='GOCSPX-test-secret-key'  # Secreto de prueba
    )
    google_app.sites.add(site)
    print(f"Aplicación social creada: {google_app.name}")

print("\n" + "="*60)
print("CONFIGURACIÓN DE GOOGLE OAUTH COMPLETADA")
print("="*60)
print("✅ Sitio configurado:")
print(f"   Domain: {site.domain}")
print(f"   Name: {site.name}")
print("\n✅ Aplicación social creada:")
print(f"   Provider: {google_app.provider}")
print(f"   Name: {google_app.name}")
print(f"   Client ID: {google_app.client_id}")
print("\n⚠️  IMPORTANTE:")
print("   Las credenciales actuales son de PRUEBA")
print("   Para usar en producción, necesitas:")
print("   1. Ir a https://console.cloud.google.com/")
print("   2. Crear un proyecto")
print("   3. Habilitar Google+ API")
print("   4. Crear credenciales OAuth 2.0")
print("   5. Actualizar Client ID y Secret en Django Admin")
print("\n🔗 URLs para probar:")
print(f"   Admin: http://localhost:8000/admin/")
print(f"   Login: http://localhost:8000/usuarios/login/")
print(f"   Registro: http://localhost:8000/usuarios/registro/")
print("="*60)
