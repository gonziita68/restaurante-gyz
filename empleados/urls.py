from django.urls import path
from . import views

app_name = 'empleados'

urlpatterns = [
    # Dashboard principal
    path('', views.dashboard_empleados, name='dashboard'),
    
    # Gestión de empleados
    path('lista/', views.lista_empleados, name='lista_empleados'),
    path('empleado/<int:empleado_id>/', views.detalle_empleado, name='detalle_empleado'),
    
    # Asistencia
    path('asistencia/', views.asistencia_diaria, name='asistencia_diaria'),
    path('asistencia/marcar/', views.marcar_asistencia, name='marcar_asistencia'),
    
    # Evaluaciones
    path('evaluaciones-pendientes/', views.evaluaciones_pendientes, name='evaluaciones_pendientes'),
    
    # Capacitaciones
    path('capacitaciones/', views.capacitaciones, name='capacitaciones'),
    
    # Nómina
    path('nomina/', views.reporte_nomina, name='reporte_nomina'),
    
    # Perfil del empleado
    path('mi-perfil/', views.mi_perfil_empleado, name='mi_perfil'),
    
    # APIs
    path('api/buscar/', views.api_empleados_buscar, name='api_buscar'),
]
