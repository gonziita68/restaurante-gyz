from django.urls import path
from . import views

app_name = 'inventario'

urlpatterns = [
    # Dashboard principal
    path('', views.dashboard_inventario, name='dashboard'),
    
    # Gestión de productos
    path('productos/', views.lista_productos, name='lista_productos'),
    path('productos/<int:producto_id>/', views.detalle_producto, name='detalle_producto'),
    path('productos/movimiento/', views.registrar_movimiento, name='registrar_movimiento'),
    
    # Órdenes de compra
    path('ordenes/', views.lista_ordenes_compra, name='lista_ordenes'),
    path('ordenes/<int:orden_id>/', views.detalle_orden_compra, name='detalle_orden'),
    
    # Alertas
    path('alertas/', views.alertas_inventario, name='alertas'),
    path('alertas/<int:alerta_id>/resolver/', views.resolver_alerta, name='resolver_alerta'),
    
    # Reportes
    path('reporte/', views.reporte_inventario, name='reporte'),
    
    # Procesos automáticos
    path('procesar-consumos/', views.consumo_por_pedidos, name='procesar_consumos'),
    
    # APIs
    path('api/productos/', views.api_productos_disponibles, name='api_productos'),
]
