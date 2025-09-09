#!/usr/bin/env python
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp

print("🔍 DIAGNÓSTICO DE GOOGLE OAUTH")
print("="*50)

# Verificar sitio
try:
    site = Site.objects.get(id=1)
    print(f"✅ Sitio configurado:")
    print(f"   Domain: {site.domain}")
    print(f"   Name: {site.name}")
    
    if site.domain != 'localhost:8000':
        print("⚠️  ADVERTENCIA: El dominio del sitio no es 'localhost:8000'")
        print("   Esto puede causar problemas con Google OAuth")
except Site.DoesNotExist:
    print("❌ ERROR: No se encontró el sitio")
    print("   Ejecuta: python setup_admin.py")

# Verificar aplicación social
try:
    google_app = SocialApp.objects.get(provider='google')
    print(f"\n✅ Aplicación social encontrada:")
    print(f"   Provider: {google_app.provider}")
    print(f"   Name: {google_app.name}")
    print(f"   Client ID: {google_app.client_id}")
    
    # Verificar si las credenciales son reales o de prueba
    if 'test' in google_app.client_id or '123456789' in google_app.client_id:
        print("⚠️  ADVERTENCIA: Usando credenciales de prueba")
        print("   Para que funcione completamente, necesitas credenciales reales de Google")
    else:
        print("✅ Usando credenciales reales de Google")
    
    # Verificar sitios asociados
    sites = google_app.sites.all()
    if sites:
        print(f"   Sitios asociados: {[s.domain for s in sites]}")
    else:
        print("❌ ERROR: No hay sitios asociados a la aplicación")
        
except SocialApp.DoesNotExist:
    print("\n❌ ERROR: No se encontró aplicación social de Google")
    print("   Necesitas crear una en Django Admin")

print("\n" + "="*50)
print("📋 PASOS PARA SOLUCIONAR:")
print("="*50)

if not Site.objects.filter(domain='localhost:8000').exists():
    print("1. Configura el sitio en Django Admin:")
    print("   - Ve a Sites")
    print("   - Cambia Domain name a: localhost:8000")
    print("   - Cambia Display name a: Restaurante GYZ")

if not SocialApp.objects.filter(provider='google').exists():
    print("2. Crea aplicación social en Django Admin:")
    print("   - Ve a Social Applications")
    print("   - Add Social Application")
    print("   - Provider: Google")
    print("   - Usa credenciales reales de Google Cloud Console")

print("3. Verifica credenciales en Google Cloud Console:")
print("   - URI de origen: http://localhost:8000")
print("   - URI de redirección: http://localhost:8000/accounts/google/login/callback/")

print("\n🔗 URLs para probar:")
print("   Admin: http://localhost:8000/admin/")
print("   Registro: http://localhost:8000/usuarios/registro/")
print("   Login: http://localhost:8000/usuarios/login/")
