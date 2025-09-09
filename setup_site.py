#!/usr/bin/env python
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.sites.models import Site

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
