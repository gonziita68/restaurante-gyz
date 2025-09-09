from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from django.core.paginator import Paginator
from decimal import Decimal
import json

from .models import (
    ProductoInventario, MovimientoInventario, OrdenCompra, 
    ItemOrdenCompra, AlertaInventario, Proveedor, CategoriaInventario,
    TipoMovimiento, EstadoOrden, RecetaConsumo
)
from menu.models import PlatoMenu
from pedidos.models import Pedido, ItemPedido

def es_staff(user):
    """Verifica si el usuario es staff"""
    return user.is_staff

@login_required
@user_passes_test(es_staff)
def dashboard_inventario(request):
    """Dashboard principal del inventario"""
    
    # Estadísticas generales
    total_productos = ProductoInventario.objects.filter(activo=True).count()
    productos_stock_bajo = ProductoInventario.objects.filter(
        activo=True,
        stock_actual__lte=F('stock_minimo')
    ).count()
    
    valor_total_inventario = ProductoInventario.objects.filter(
        activo=True
    ).aggregate(
        total=Sum(F('stock_actual') * F('costo_unitario'))
    )['total'] or Decimal('0')
    
    # Alertas activas
    alertas_activas = AlertaInventario.objects.filter(activa=True).count()
    
    # Productos con stock bajo
    productos_criticos = ProductoInventario.objects.filter(
        activo=True,
        stock_actual__lte=F('stock_minimo')
    ).select_related('ingrediente', 'categoria_inventario')[:10]
    
    # Órdenes de compra pendientes
    ordenes_pendientes = OrdenCompra.objects.filter(
        estado__in=[EstadoOrden.ENVIADA, EstadoOrden.CONFIRMADA]
    ).select_related('proveedor').count()
    
    # Movimientos recientes
    movimientos_recientes = MovimientoInventario.objects.select_related(
        'producto__ingrediente', 'usuario'
    ).order_by('-fecha')[:10]
    
    # Productos más rotados (último mes)
    fecha_inicio = timezone.now() - timezone.timedelta(days=30)
    productos_rotacion = ProductoInventario.objects.filter(
        activo=True,
        movimientos__tipo_movimiento=TipoMovimiento.SALIDA,
        movimientos__fecha__gte=fecha_inicio
    ).annotate(
        total_salidas=Sum('movimientos__cantidad')
    ).order_by('-total_salidas')[:10]
    
    context = {
        'total_productos': total_productos,
        'productos_stock_bajo': productos_stock_bajo,
        'valor_total_inventario': valor_total_inventario,
        'alertas_activas': alertas_activas,
        'productos_criticos': productos_criticos,
        'ordenes_pendientes': ordenes_pendientes,
        'movimientos_recientes': movimientos_recientes,
        'productos_rotacion': productos_rotacion,
    }
    
    return render(request, 'inventario/dashboard.html', context)

@login_required
@user_passes_test(es_staff)
def lista_productos(request):
    """Lista de productos en inventario"""
    
    productos = ProductoInventario.objects.filter(activo=True).select_related(
        'ingrediente', 'categoria_inventario', 'proveedor_principal'
    )
    
    # Filtros
    categoria = request.GET.get('categoria')
    nivel_stock = request.GET.get('nivel_stock')
    buscar = request.GET.get('buscar')
    
    if categoria:
        productos = productos.filter(categoria_inventario_id=categoria)
    
    if nivel_stock:
        if nivel_stock == 'bajo':
            productos = productos.filter(stock_actual__lte=F('stock_minimo'))
        elif nivel_stock == 'alto':
            productos = productos.filter(stock_actual__gte=F('stock_maximo'))
    
    if buscar:
        productos = productos.filter(
            Q(ingrediente__nombre__icontains=buscar) |
            Q(codigo_producto__icontains=buscar)
        )
    
    # Paginación
    paginator = Paginator(productos, 20)
    page = request.GET.get('page')
    productos = paginator.get_page(page)
    
    # Categorías para filtro
    categorias = CategoriaInventario.objects.filter(activo=True)
    
    context = {
        'productos': productos,
        'categorias': categorias,
        'categoria_actual': categoria,
        'nivel_stock_actual': nivel_stock,
        'buscar_actual': buscar,
    }
    
    return render(request, 'inventario/lista_productos.html', context)

@login_required
@user_passes_test(es_staff)
def detalle_producto(request, producto_id):
    """Detalle de un producto en inventario"""
    
    producto = get_object_or_404(
        ProductoInventario.objects.select_related(
            'ingrediente', 'categoria_inventario', 'proveedor_principal'
        ),
        id=producto_id,
        activo=True
    )
    
    # Movimientos recientes
    movimientos = producto.movimientos.select_related('usuario').order_by('-fecha')[:20]
    
    # Alertas activas
    alertas = producto.alertas.filter(activa=True).order_by('-fecha_creacion')
    
    # Estadísticas del último mes
    fecha_inicio = timezone.now() - timezone.timedelta(days=30)
    
    stats_mes = producto.movimientos.filter(fecha__gte=fecha_inicio).aggregate(
        entradas=Sum('cantidad', filter=Q(tipo_movimiento=TipoMovimiento.ENTRADA)),
        salidas=Sum('cantidad', filter=Q(tipo_movimiento=TipoMovimiento.SALIDA)),
        total_movimientos=Count('id')
    )
    
    # Recetas que usan este producto
    recetas = RecetaConsumo.objects.filter(
        producto=producto
    ).select_related('plato')
    
    context = {
        'producto': producto,
        'movimientos': movimientos,
        'alertas': alertas,
        'stats_mes': stats_mes,
        'recetas': recetas,
    }
    
    return render(request, 'inventario/detalle_producto.html', context)

@login_required
@user_passes_test(es_staff)
@require_POST
def registrar_movimiento(request):
    """Registra un movimiento de inventario"""
    
    try:
        data = json.loads(request.body)
        
        producto_id = data.get('producto_id')
        tipo_movimiento = data.get('tipo_movimiento')
        cantidad = Decimal(data.get('cantidad', '0'))
        costo_unitario = Decimal(data.get('costo_unitario', '0'))
        motivo = data.get('motivo', '')
        
        producto = get_object_or_404(ProductoInventario, id=producto_id, activo=True)
        
        # Validar cantidad
        if cantidad <= 0:
            return JsonResponse({'error': 'La cantidad debe ser mayor a 0'}, status=400)
        
        # Validar stock suficiente para salidas
        if tipo_movimiento == TipoMovimiento.SALIDA and producto.stock_actual < cantidad:
            return JsonResponse({
                'error': f'Stock insuficiente. Disponible: {producto.stock_actual}'
            }, status=400)
        
        # Calcular nuevo stock
        stock_anterior = producto.stock_actual
        
        if tipo_movimiento == TipoMovimiento.ENTRADA:
            stock_nuevo = stock_anterior + cantidad
        elif tipo_movimiento == TipoMovimiento.SALIDA:
            stock_nuevo = stock_anterior - cantidad
        else:  # AJUSTE
            stock_nuevo = cantidad
            cantidad = stock_nuevo - stock_anterior
        
        # Crear movimiento
        movimiento = MovimientoInventario.objects.create(
            producto=producto,
            tipo_movimiento=tipo_movimiento,
            cantidad=abs(cantidad),
            costo_unitario=costo_unitario,
            stock_anterior=stock_anterior,
            stock_nuevo=stock_nuevo,
            motivo=motivo,
            usuario=request.user
        )
        
        # Actualizar stock del producto
        producto.stock_actual = stock_nuevo
        producto.save()
        
        # Verificar alertas
        verificar_alertas_producto(producto)
        
        return JsonResponse({
            'success': True,
            'movimiento_id': movimiento.id,
            'stock_nuevo': stock_nuevo
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@user_passes_test(es_staff)
def lista_ordenes_compra(request):
    """Lista de órdenes de compra"""
    
    ordenes = OrdenCompra.objects.select_related('proveedor', 'creado_por').order_by('-fecha_creacion')
    
    # Filtros
    estado = request.GET.get('estado')
    proveedor = request.GET.get('proveedor')
    
    if estado:
        ordenes = ordenes.filter(estado=estado)
    
    if proveedor:
        ordenes = ordenes.filter(proveedor_id=proveedor)
    
    # Paginación
    paginator = Paginator(ordenes, 20)
    page = request.GET.get('page')
    ordenes = paginator.get_page(page)
    
    # Proveedores para filtro
    proveedores = Proveedor.objects.filter(activo=True)
    
    context = {
        'ordenes': ordenes,
        'estados': EstadoOrden.choices,
        'proveedores': proveedores,
        'estado_actual': estado,
        'proveedor_actual': proveedor,
    }
    
    return render(request, 'inventario/lista_ordenes.html', context)

@login_required
@user_passes_test(es_staff)
def detalle_orden_compra(request, orden_id):
    """Detalle de una orden de compra"""
    
    orden = get_object_or_404(
        OrdenCompra.objects.select_related('proveedor', 'creado_por'),
        id=orden_id
    )
    
    items = orden.items.select_related('producto__ingrediente').all()
    
    context = {
        'orden': orden,
        'items': items,
    }
    
    return render(request, 'inventario/detalle_orden.html', context)

@login_required
@user_passes_test(es_staff)
def alertas_inventario(request):
    """Lista de alertas de inventario"""
    
    alertas = AlertaInventario.objects.filter(
        activa=True
    ).select_related(
        'producto__ingrediente', 'resuelto_por'
    ).order_by('-fecha_creacion')
    
    # Filtros
    tipo_alerta = request.GET.get('tipo')
    
    if tipo_alerta:
        alertas = alertas.filter(tipo_alerta=tipo_alerta)
    
    context = {
        'alertas': alertas,
        'tipos_alerta': AlertaInventario.TIPOS_ALERTA,
        'tipo_actual': tipo_alerta,
    }
    
    return render(request, 'inventario/alertas.html', context)

@login_required
@user_passes_test(es_staff)
@require_POST
def resolver_alerta(request, alerta_id):
    """Resuelve una alerta de inventario"""
    
    alerta = get_object_or_404(AlertaInventario, id=alerta_id, activa=True)
    alerta.resolver(request.user)
    
    messages.success(request, 'Alerta resuelta correctamente.')
    return redirect('inventario:alertas')

def verificar_alertas_producto(producto):
    """Verifica y genera alertas para un producto"""
    
    # Alerta de stock bajo
    if producto.stock_actual <= producto.stock_minimo:
        AlertaInventario.objects.get_or_create(
            producto=producto,
            tipo_alerta='stock_bajo',
            activa=True,
            defaults={
                'mensaje': f'El stock de {producto.ingrediente.nombre} está por debajo del mínimo ({producto.stock_minimo})'
            }
        )
    
    # Alerta de stock agotado
    if producto.stock_actual <= 0:
        AlertaInventario.objects.get_or_create(
            producto=producto,
            tipo_alerta='stock_agotado',
            activa=True,
            defaults={
                'mensaje': f'El stock de {producto.ingrediente.nombre} está agotado'
            }
        )

@login_required
@user_passes_test(es_staff)
def reporte_inventario(request):
    """Reporte general de inventario"""
    
    # Estadísticas por categoría
    stats_categorias = CategoriaInventario.objects.filter(
        activo=True
    ).annotate(
        total_productos=Count('productos', filter=Q(productos__activo=True)),
        valor_total=Sum(
            F('productos__stock_actual') * F('productos__costo_unitario'),
            filter=Q(productos__activo=True)
        ),
        productos_bajo_stock=Count(
            'productos',
            filter=Q(
                productos__activo=True,
                productos__stock_actual__lte=F('productos__stock_minimo')
            )
        )
    )
    
    # Productos con mayor rotación (último mes)
    fecha_inicio = timezone.now() - timezone.timedelta(days=30)
    productos_rotacion = ProductoInventario.objects.filter(
        activo=True,
        movimientos__tipo_movimiento=TipoMovimiento.SALIDA,
        movimientos__fecha__gte=fecha_inicio
    ).annotate(
        total_salidas=Sum('movimientos__cantidad')
    ).select_related('ingrediente').order_by('-total_salidas')[:15]
    
    # Movimientos del último mes por tipo
    movimientos_mes = MovimientoInventario.objects.filter(
        fecha__gte=fecha_inicio
    ).values('tipo_movimiento').annotate(
        cantidad_total=Sum('cantidad'),
        valor_total=Sum(F('cantidad') * F('costo_unitario')),
        total_movimientos=Count('id')
    )
    
    context = {
        'stats_categorias': stats_categorias,
        'productos_rotacion': productos_rotacion,
        'movimientos_mes': movimientos_mes,
        'fecha_inicio': fecha_inicio,
    }
    
    return render(request, 'inventario/reporte.html', context)

@login_required
@user_passes_test(es_staff)
def consumo_por_pedidos(request):
    """Procesa el consumo de ingredientes por pedidos completados"""
    
    # Obtener pedidos completados del día que no han sido procesados
    hoy = timezone.now().date()
    pedidos_completados = Pedido.objects.filter(
        estado='entregado',
        fecha_entrega__date=hoy,
        procesado_inventario=False  # Campo que agregarías al modelo Pedido
    ).prefetch_related('items__plato')
    
    consumos_procesados = 0
    
    for pedido in pedidos_completados:
        for item in pedido.items.all():
            # Buscar recetas de consumo para este plato
            recetas = RecetaConsumo.objects.filter(plato=item.plato)
            
            for receta in recetas:
                cantidad_consumida = receta.cantidad_necesaria * item.cantidad
                
                # Registrar movimiento de salida
                if receta.producto.stock_actual >= cantidad_consumida:
                    MovimientoInventario.objects.create(
                        producto=receta.producto,
                        tipo_movimiento=TipoMovimiento.SALIDA,
                        cantidad=cantidad_consumida,
                        costo_unitario=receta.producto.costo_unitario,
                        stock_anterior=receta.producto.stock_actual,
                        stock_nuevo=receta.producto.stock_actual - cantidad_consumida,
                        motivo=f'Consumo por pedido {str(pedido.numero_pedido)[:8]}',
                        referencia=str(pedido.numero_pedido),
                        usuario=request.user
                    )
                    
                    # Actualizar stock
                    receta.producto.stock_actual -= cantidad_consumida
                    receta.producto.save()
                    
                    # Verificar alertas
                    verificar_alertas_producto(receta.producto)
                    
                    consumos_procesados += 1
        
        # Marcar pedido como procesado (necesitarías agregar este campo)
        # pedido.procesado_inventario = True
        # pedido.save()
    
    messages.success(request, f'{consumos_procesados} consumos de inventario procesados.')
    return redirect('inventario:dashboard')

def api_productos_disponibles(request):
    """API para obtener productos disponibles"""
    buscar = request.GET.get('q', '')
    
    productos = ProductoInventario.objects.filter(
        activo=True,
        stock_actual__gt=0
    )
    
    if buscar:
        productos = productos.filter(
            ingrediente__nombre__icontains=buscar
        )
    
    productos = productos.select_related('ingrediente')[:10]
    
    data = [{
        'id': p.id,
        'nombre': p.ingrediente.nombre,
        'stock': float(p.stock_actual),
        'unidad': p.get_unidad_medida_display(),
        'costo': float(p.costo_unitario)
    } for p in productos]
    
    return JsonResponse({'productos': data})
