from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('usuarios.urls')),  # URLs principales del sitio
    path('menu/', include('menu.urls')),  # URLs del sistema de menú
    path('pedidos/', include('pedidos.urls')),  # URLs del sistema de pedidos
    path('reservas/', include('reservas.urls')),  # URLs del sistema de reservas
    path('pagos/', include('pagos.urls')),  # URLs del sistema de pagos
    path('inventario/', include('inventario.urls')),  # URLs del sistema de inventario
    path('empleados/', include('empleados.urls')),  # URLs del sistema de empleados
    path('eventos/', include('eventos.urls')),  # URLs del sistema de eventos y catering
    
    # URLs de django-allauth
    path('accounts/', include('allauth.urls')),
]

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)