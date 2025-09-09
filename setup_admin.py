#!/usr/bin/env python
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site

User = get_user_model()

# Crear superusuario si no existe
try:
    admin_user = User.objects.get(username='admin')
    print(f"Superusuario existente: {admin_user.username}")
except User.DoesNotExist:
    admin_user = User.objects.create_superuser(
        username='admin',
        email='admin@restaurante.com',
        password='admin123456'
    )
    print(f"Superusuario creado: {admin_user.username}")

# Crear o actualizar el sitio
site, created = Site.objects.get_or_create(
    id=1,
    defaults={
        'domain': 'localhost:8000',
        'name': 'Restaurante GYZ'
    }
)

if created:
    print(f"Sitio creado: {site.name} - {site.domain}")
else:
    print(f"Sitio existente: {site.name} - {site.domain}")

print("\n" + "="*50)
print("CONFIGURACIÓN COMPLETADA")
print("="*50)
print("Superusuario:")
print(f"  Usuario: admin")
print(f"  Contraseña: admin123456")
print(f"  Email: admin@restaurante.com")
print("\nURLs importantes:")
print(f"  Admin: http://localhost:8000/admin/")
print(f"  Página principal: http://localhost:8000/")
print(f"  Registro: http://localhost:8000/usuarios/registro/")
print(f"  Login: http://localhost:8000/usuarios/login/")
print("="*50)
