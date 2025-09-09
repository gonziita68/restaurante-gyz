from django.urls import path
from . import views

app_name = 'reservas'

urlpatterns = [
    # Vista principal de reservas
    path('', views.disponibilidad_mesas, name='disponibilidad'),
    
    # APIs para disponibilidad
    path('api/buscar-disponibilidad/', views.buscar_disponibilidad, name='buscar_disponibilidad'),
    path('api/horarios-disponibles/', views.horarios_disponibles, name='horarios_disponibles'),
    
    # Gestión de reservas
    path('crear/', views.crear_reserva, name='crear_reserva'),
    path('mis-reservas/', views.mis_reservas, name='mis_reservas'),
    path('reserva/<int:reserva_id>/', views.detalle_reserva, name='detalle_reserva'),
    path('reserva/<int:reserva_id>/cancelar/', views.cancelar_reserva, name='cancelar_reserva'),
    
    # Consulta pública
    path('consultar/', views.consultar_reserva, name='consultar_reserva'),
    
    # Vista de calendario (para staff)
    path('calendario/', views.calendario_reservas, name='calendario'),
]
