from django.urls import path
from . import views

app_name = 'pagos'

urlpatterns = [
    # Procesamiento de pagos
    path('pedido/<int:pedido_id>/', views.procesar_pago, name='procesar_pago_pedido'),
    path('reserva/<int:reserva_id>/', views.procesar_pago, name='procesar_pago_reserva'),
    path('crear/', views.crear_pago, name='crear_pago'),
    
    # Pago con tarjeta
    path('tarjeta/', views.pago_tarjeta, name='pago_tarjeta'),
    path('confirmacion/<str:transaccion_id>/', views.confirmacion_pago, name='confirmacion_pago'),
    path('api/procesar/', views.procesar_pago_ajax, name='procesar_pago_ajax'),
    
    # Confirmación de pagos
    path('confirmar-efectivo/<int:pago_id>/', views.confirmar_pago_efectivo, name='confirmar_pago_efectivo'),
    
    # Webhooks
    path('webhook/stripe/', views.webhook_stripe, name='webhook_stripe'),
    
    # Consultas
    path('historial/', views.historial_pagos, name='historial_pagos'),
    path('estado/<uuid:numero_pago>/', views.estado_pago, name='estado_pago'),
]
