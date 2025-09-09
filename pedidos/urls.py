from django.urls import path
from . import views

app_name = 'pedidos'

urlpatterns = [
    # Carrito de compras
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('carrito/agregar/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/actualizar/<int:item_id>/', views.actualizar_item_carrito, name='actualizar_item_carrito'),
    path('carrito/eliminar/<int:item_id>/', views.eliminar_item_carrito, name='eliminar_item_carrito'),
    path('carrito/limpiar/', views.limpiar_carrito, name='limpiar_carrito'),
    path('carrito/info/', views.obtener_info_carrito, name='obtener_info_carrito'),
    
    # Proceso de pedido
    path('checkout/', views.checkout, name='checkout'),
    
    # Gestión de pedidos
    path('mis-pedidos/', views.mis_pedidos, name='mis_pedidos'),
    path('pedido/<int:pedido_id>/', views.detalle_pedido, name='detalle_pedido'),
    path('pedido/<int:pedido_id>/cancelar/', views.cancelar_pedido, name='cancelar_pedido'),
    
    # Seguimiento público
    path('seguimiento/<uuid:numero_pedido>/', views.seguimiento_pedido, name='seguimiento_pedido'),
]
