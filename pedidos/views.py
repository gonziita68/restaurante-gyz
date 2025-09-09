from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.utils import timezone
from django.core.paginator import Paginator
from menu.models import PlatoMenu, OpcionPersonalizacion
from .models import (
    CarritoCompras, ItemCarrito, Pedido, ItemPedido, 
    SeguimientoPedido, EstadoPedido, TipoEntrega
)
import json

def obtener_carrito(request):
    """Obtiene o crea el carrito del usuario"""
    if request.user.is_authenticated:
        carrito, created = CarritoCompras.objects.get_or_create(
            usuario=request.user,
            activo=True,
            defaults={'session_key': request.session.session_key}
        )
    else:
        # Para usuarios no autenticados, usar session_key
        if not request.session.session_key:
            request.session.create()
        
        carrito, created = CarritoCompras.objects.get_or_create(
            session_key=request.session.session_key,
            usuario=None,
            activo=True
        )
    
    return carrito

@require_POST
def agregar_al_carrito(request):
    """Agrega un plato al carrito"""
    try:
        data = json.loads(request.body)
        plato_id = data.get('plato_id')
        cantidad = int(data.get('cantidad', 1))
        opciones_ids = data.get('opciones', [])
        instrucciones = data.get('instrucciones', '').strip()
        
        # Validaciones
        if cantidad < 1 or cantidad > 10:
            return JsonResponse({'error': 'Cantidad debe estar entre 1 y 10'}, status=400)
        
        plato = get_object_or_404(PlatoMenu, id=plato_id, disponible=True)
        carrito = obtener_carrito(request)
        
        # Verificar si el plato ya está en el carrito
        item_existente = ItemCarrito.objects.filter(carrito=carrito, plato=plato).first()
        
        with transaction.atomic():
            if item_existente:
                # Actualizar cantidad
                item_existente.cantidad = min(item_existente.cantidad + cantidad, 10)
                item_existente.save()
                item = item_existente
            else:
                # Crear nuevo item
                item = ItemCarrito.objects.create(
                    carrito=carrito,
                    plato=plato,
                    cantidad=cantidad,
                    precio_unitario=plato.precio_actual,
                    instrucciones_especiales=instrucciones
                )
            
            # Agregar opciones de personalización
            if opciones_ids:
                opciones = OpcionPersonalizacion.objects.filter(
                    id__in=opciones_ids,
                    plato=plato,
                    disponible=True
                )
                item.opciones_personalizacion.set(opciones)
        
        return JsonResponse({
            'success': True,
            'message': f'{plato.nombre} agregado al carrito',
            'carrito_items': carrito.total_items,
            'carrito_total': str(carrito.total_final)
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def ver_carrito(request):
    """Vista para ver el contenido del carrito"""
    carrito = obtener_carrito(request)
    items = carrito.items.select_related('plato').prefetch_related('opciones_personalizacion')
    
    context = {
        'carrito': carrito,
        'items': items,
    }
    
    return render(request, 'pedidos/carrito.html', context)

@require_POST
def actualizar_item_carrito(request, item_id):
    """Actualiza la cantidad de un item en el carrito"""
    try:
        data = json.loads(request.body)
        nueva_cantidad = int(data.get('cantidad', 1))
        
        if nueva_cantidad < 1 or nueva_cantidad > 10:
            return JsonResponse({'error': 'Cantidad debe estar entre 1 y 10'}, status=400)
        
        carrito = obtener_carrito(request)
        item = get_object_or_404(ItemCarrito, id=item_id, carrito=carrito)
        
        item.cantidad = nueva_cantidad
        item.save()
        
        return JsonResponse({
            'success': True,
            'item_total': str(item.total),
            'carrito_subtotal': str(carrito.subtotal),
            'carrito_total': str(carrito.total_final)
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_POST
def eliminar_item_carrito(request, item_id):
    """Elimina un item del carrito"""
    try:
        carrito = obtener_carrito(request)
        item = get_object_or_404(ItemCarrito, id=item_id, carrito=carrito)
        
        item.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Item eliminado del carrito',
            'carrito_items': carrito.total_items,
            'carrito_subtotal': str(carrito.subtotal),
            'carrito_total': str(carrito.total_final)
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def checkout(request):
    """Proceso de checkout"""
    carrito = obtener_carrito(request)
    
    if not carrito.items.exists():
        messages.error(request, 'Tu carrito está vacío.')
        return redirect('pedidos:ver_carrito')
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Crear el pedido
                pedido = Pedido.objects.create(
                    usuario=request.user,
                    tipo_entrega=request.POST.get('tipo_entrega', TipoEntrega.DELIVERY),
                    direccion_entrega=request.POST.get('direccion_entrega', ''),
                    telefono_contacto=request.POST.get('telefono_contacto', ''),
                    notas_entrega=request.POST.get('notas_entrega', ''),
                    numero_mesa=request.POST.get('numero_mesa') or None,
                    subtotal=carrito.subtotal,
                    impuestos=carrito.total_impuestos,
                    costo_delivery=carrito.costo_delivery,
                    total=carrito.total_final,
                    metodo_pago=request.POST.get('metodo_pago', 'efectivo'),
                    tiempo_estimado_preparacion=sum(
                        item.plato.tiempo_preparacion * item.cantidad 
                        for item in carrito.items.all()
                    ) // carrito.total_items  # Promedio ponderado
                )
                
                # Crear items del pedido
                for item_carrito in carrito.items.all():
                    ItemPedido.objects.create(
                        pedido=pedido,
                        plato=item_carrito.plato,
                        cantidad=item_carrito.cantidad,
                        precio_unitario=item_carrito.precio_unitario,
                        precio_opciones=item_carrito.precio_opciones,
                        opciones_seleccionadas=[
                            {
                                'nombre': opcion.nombre,
                                'precio': str(opcion.precio_adicional)
                            }
                            for opcion in item_carrito.opciones_personalizacion.all()
                        ],
                        instrucciones_especiales=item_carrito.instrucciones_especiales
                    )
                
                # Limpiar carrito
                carrito.limpiar_carrito()
                
                # Crear seguimiento inicial
                SeguimientoPedido.objects.create(
                    pedido=pedido,
                    estado_anterior='',
                    estado_nuevo=EstadoPedido.PENDIENTE,
                    usuario_responsable=request.user,
                    comentario='Pedido realizado'
                )
                
                messages.success(request, f'¡Pedido realizado exitosamente! Número de pedido: #{str(pedido.numero_pedido)[:8]}')
                return redirect('pedidos:detalle_pedido', pedido_id=pedido.id)
                
        except Exception as e:
            messages.error(request, f'Error al procesar el pedido: {str(e)}')
    
    context = {
        'carrito': carrito,
        'items': carrito.items.select_related('plato').prefetch_related('opciones_personalizacion'),
        'tipos_entrega': TipoEntrega.choices,
    }
    
    return render(request, 'pedidos/checkout.html', context)

@login_required
def mis_pedidos(request):
    """Lista de pedidos del usuario"""
    pedidos_list = Pedido.objects.filter(usuario=request.user).order_by('-fecha_pedido')
    
    # Paginación
    paginator = Paginator(pedidos_list, 10)
    page_number = request.GET.get('page')
    pedidos = paginator.get_page(page_number)
    
    context = {
        'pedidos': pedidos,
    }
    
    return render(request, 'pedidos/mis_pedidos.html', context)

@login_required
def detalle_pedido(request, pedido_id):
    """Detalle de un pedido específico"""
    pedido = get_object_or_404(
        Pedido.objects.prefetch_related('items__plato', 'seguimiento'),
        id=pedido_id,
        usuario=request.user
    )
    
    context = {
        'pedido': pedido,
        'puede_cancelar': pedido.puede_cancelar,
    }
    
    return render(request, 'pedidos/detalle_pedido.html', context)

@login_required
@require_POST
def cancelar_pedido(request, pedido_id):
    """Cancela un pedido"""
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
    
    if pedido.cancelar_pedido():
        # Crear seguimiento
        SeguimientoPedido.objects.create(
            pedido=pedido,
            estado_anterior=pedido.estado,
            estado_nuevo=EstadoPedido.CANCELADO,
            usuario_responsable=request.user,
            comentario='Cancelado por el cliente'
        )
        
        messages.success(request, 'Pedido cancelado exitosamente.')
    else:
        messages.error(request, 'No se puede cancelar este pedido.')
    
    return redirect('pedidos:detalle_pedido', pedido_id=pedido.id)

def seguimiento_pedido(request, numero_pedido):
    """Seguimiento público de pedido (sin autenticación)"""
    try:
        pedido = get_object_or_404(
            Pedido.objects.prefetch_related('seguimiento'),
            numero_pedido=numero_pedido
        )
        
        context = {
            'pedido': pedido,
            'seguimiento': pedido.seguimiento.order_by('fecha_cambio'),
        }
        
        return render(request, 'pedidos/seguimiento_publico.html', context)
        
    except Exception as e:
        messages.error(request, 'Número de pedido no encontrado.')
        return redirect('usuarios:index')

def obtener_info_carrito(request):
    """API para obtener información del carrito"""
    try:
        carrito = obtener_carrito(request)
        
        return JsonResponse({
            'items_count': carrito.total_items,
            'subtotal': str(carrito.subtotal),
            'total': str(carrito.total_final),
            'delivery_cost': str(carrito.costo_delivery),
            'taxes': str(carrito.total_impuestos)
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_POST
def limpiar_carrito(request):
    """Limpia todo el carrito"""
    try:
        carrito = obtener_carrito(request)
        carrito.limpiar_carrito()
        
        return JsonResponse({
            'success': True,
            'message': 'Carrito limpiado exitosamente'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
