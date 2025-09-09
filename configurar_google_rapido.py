#!/usr/bin/env python
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp

print("🚀 CONFIGURANDO GOOGLE OAUTH RÁPIDAMENTE")
print("="*50)

# 1. Configurar el sitio
try:
    site = Site.objects.get(id=1)
    site.domain = 'localhost:8000'
    site.name = 'Restaurante GYZ'
    site.save()
    print("✅ Sitio configurado correctamente")
except Exception as e:
    print(f"❌ Error configurando sitio: {e}")

# 2. Crear aplicación social de Google
try:
    # Eliminar aplicación existente si hay
    SocialApp.objects.filter(provider='google').delete()
    
    # Crear nueva aplicación
    google_app = SocialApp.objects.create(
        provider='google',
        name='Google OAuth',
        client_id='123456789-test.apps.googleusercontent.com',
        secret='GOCSPX-test-secret-key'
    )
    google_app.sites.add(site)
    print("✅ Aplicación social de Google creada")
except Exception as e:
    print(f"❌ Error creando aplicación social: {e}")

print("\n" + "="*50)
print("🎯 CONFIGURACIÓN COMPLETADA")
print("="*50)
print("Ahora puedes:")
print("1. Ir a http://localhost:8000/usuarios/registro/")
print("2. Hacer clic en 'Registrarse con Google'")
print("3. Verás una página de error de Google (normal con credenciales temporales)")
print("\nPara que funcione completamente:")
print("1. Ve a https://console.cloud.google.com/")
print("2. Crea credenciales OAuth 2.0 reales")
print("3. Actualiza las credenciales en Django Admin")
print("="*50)
