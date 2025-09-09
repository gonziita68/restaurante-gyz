from django.urls import path
from . import views

app_name = 'eventos'

urlpatterns = [
    # Vistas para clientes
    path('solicitar/', views.solicitar_evento, name='solicitar_evento'),
    path('solicitar/paso2/<int:evento_id>/', views.solicitar_evento_paso2, name='solicitar_evento_paso2'),
    path('solicitar/paso3/<int:evento_id>/', views.solicitar_evento_paso3, name='solicitar_evento_paso3'),
    path('solicitar/paso4/<int:evento_id>/', views.solicitar_evento_paso4, name='solicitar_evento_paso4'),
    path('mis-eventos/', views.mis_eventos, name='mis_eventos'),
    path('detalle/<int:evento_id>/', views.detalle_evento, name='detalle_evento'),
    path('cancelar/<int:evento_id>/', views.cancelar_evento, name='cancelar_evento'),
    
    # Vistas para catering
    path('catering/solicitar/', views.solicitar_catering, name='solicitar_catering'),
    
    # Vistas para el personal del restaurante
    path('dashboard/', views.dashboard_eventos, name='dashboard_eventos'),
    path('gestionar/<int:evento_id>/', views.gestionar_evento, name='gestionar_evento'),
    path('cotizacion/<int:evento_id>/', views.crear_cotizacion, name='crear_cotizacion'),
    path('presupuesto/<int:evento_id>/', views.crear_presupuesto, name='crear_presupuesto'),
    
    # Vistas AJAX
    path('api/calcular-precio/', views.calcular_precio_evento, name='calcular_precio_evento'),
]
