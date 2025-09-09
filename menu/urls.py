from django.urls import path
from . import views

app_name = 'menu'

urlpatterns = [
    path('', views.menu_completo, name='menu_completo'),
    path('categoria/<int:categoria_id>/', views.categoria_detalle, name='categoria_detalle'),
    path('plato/<int:plato_id>/', views.plato_detalle, name='plato_detalle'),
    path('buscar/', views.buscar_platos, name='buscar_platos'),
    path('api/', views.menu_api, name='menu_api'),
    path('api/disponibilidad/<int:plato_id>/', views.verificar_disponibilidad, name='verificar_disponibilidad'),

    # URLs para el sistema de reseñas
    path('plato/<int:plato_id>/resenas/', views.obtener_resenas_plato, name='obtener_resenas_plato'),
    path('plato/<int:plato_id>/resena/', views.crear_resena, name='crear_resena'),
    path('resena/<int:resena_id>/responder/', views.responder_resena, name='responder_resena'),
    path('resena/<int:resena_id>/eliminar/', views.eliminar_resena, name='eliminar_resena'),
    path('dashboard/resenas/', views.dashboard_resenas, name='dashboard_resenas'),
    path('api/resenas/todas/', views.obtener_todas_resenas, name='obtener_todas_resenas'),
]
