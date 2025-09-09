from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.db.models import Q, Prefetch, Avg, Count
from django.utils import timezone
from .models import CategoriaMenu, PlatoMenu, MenuDelDia, Resena
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

def menu_completo(request):
    """Vista para mostrar el menú completo"""
    # Obtener categorías activas con sus platos disponibles
    categorias = CategoriaMenu.objects.filter(activa=True).prefetch_related(
        Prefetch(
            'platos',
            queryset=PlatoMenu.objects.filter(disponible=True).order_by('orden', 'nombre')
        )
    ).order_by('orden', 'nombre')
    
    # Menú del día si existe
    menu_hoy = MenuDelDia.objects.filter(
        fecha=timezone.now().date(),
        activo=True
    ).prefetch_related('platos').first()
    
    # Platos destacados
    platos_destacados = PlatoMenu.objects.filter(
        disponible=True,
        destacado=True
    ).select_related('categoria')[:6]
    
    # Platos nuevos
    platos_nuevos = PlatoMenu.objects.filter(
        disponible=True,
        nuevo=True
    ).select_related('categoria')[:4]
    
    context = {
        'categorias': categorias,
        'menu_hoy': menu_hoy,
        'platos_destacados': platos_destacados,
        'platos_nuevos': platos_nuevos,
    }
    
    return render(request, 'menu/menu_completo.html', context)

def categoria_detalle(request, categoria_id):
    """Vista para mostrar platos de una categoría específica"""
    categoria = get_object_or_404(CategoriaMenu, id=categoria_id, activa=True)
    
    platos = PlatoMenu.objects.filter(
        categoria=categoria,
        disponible=True
    ).prefetch_related('ingredientes', 'opciones_personalizacion').order_by('orden', 'nombre')
    
    # Filtros
    filtro_vegetariano = request.GET.get('vegetariano')
    filtro_sin_gluten = request.GET.get('sin_gluten')
    filtro_precio_max = request.GET.get('precio_max')
    
    if filtro_vegetariano:
        platos = platos.filter(es_vegetariano=True)
    
    if filtro_sin_gluten:
        platos = platos.filter(sin_gluten=True)
    
    if filtro_precio_max:
        try:
            precio_max = float(filtro_precio_max)
            platos = platos.filter(precio__lte=precio_max)
        except ValueError:
            pass
    
    context = {
        'categoria': categoria,
        'platos': platos,
        'filtros': {
            'vegetariano': filtro_vegetariano,
            'sin_gluten': filtro_sin_gluten,
            'precio_max': filtro_precio_max,
        }
    }
    
    return render(request, 'menu/categoria_detalle.html', context)

def plato_detalle(request, plato_id):
    """Vista para mostrar detalles de un plato específico"""
    plato = get_object_or_404(
        PlatoMenu.objects.select_related('categoria').prefetch_related(
            'ingredientes',
            'opciones_personalizacion'
        ),
        id=plato_id,
        disponible=True
    )
    
    # Platos relacionados (misma categoría)
    platos_relacionados = PlatoMenu.objects.filter(
        categoria=plato.categoria,
        disponible=True
    ).exclude(id=plato.id)[:4]
    
    context = {
        'plato': plato,
        'platos_relacionados': platos_relacionados,
    }
    
    return render(request, 'menu/plato_detalle.html', context)

def buscar_platos(request):
    """Vista para buscar platos"""
    query = request.GET.get('q', '').strip()
    
    if not query:
        return JsonResponse({'platos': []})
    
    platos = PlatoMenu.objects.filter(
        Q(nombre__icontains=query) | Q(descripcion__icontains=query),
        disponible=True
    ).select_related('categoria')[:10]
    
    resultados = []
    for plato in platos:
        resultados.append({
            'id': plato.id,
            'nombre': plato.nombre,
            'descripcion': plato.descripcion[:100] + '...' if len(plato.descripcion) > 100 else plato.descripcion,
            'precio': str(plato.precio_actual),
            'categoria': plato.categoria.nombre,
            'imagen': plato.imagen.url if plato.imagen else None,
            'url': f'/menu/plato/{plato.id}/'
        })
    
    return JsonResponse({'platos': resultados})

def menu_api(request):
    """API para obtener el menú completo en formato JSON"""
    categorias_data = []
    
    categorias = CategoriaMenu.objects.filter(activa=True).prefetch_related(
        'platos__ingredientes'
    ).order_by('orden', 'nombre')
    
    for categoria in categorias:
        platos_data = []
        platos = categoria.platos.filter(disponible=True).order_by('orden', 'nombre')
        
        for plato in platos:
            platos_data.append({
                'id': plato.id,
                'nombre': plato.nombre,
                'descripcion': plato.descripcion,
                'precio': str(plato.precio),
                'precio_oferta': str(plato.precio_oferta) if plato.precio_oferta else None,
                'imagen': plato.imagen.url if plato.imagen else None,
                'tiempo_preparacion': plato.tiempo_preparacion,
                'es_vegetariano': plato.es_vegetariano,
                'es_vegano': plato.es_vegano,
                'sin_gluten': plato.sin_gluten,
                'es_picante': plato.es_picante,
                'nivel_picante': plato.nivel_picante,
                'destacado': plato.destacado,
                'nuevo': plato.nuevo,
                'alergenos': [ing.nombre for ing in plato.alergenos],
            })
        
        categorias_data.append({
            'id': categoria.id,
            'nombre': categoria.nombre,
            'descripcion': categoria.descripcion,
            'platos': platos_data
        })
    
    return JsonResponse({
        'categorias': categorias_data,
        'timestamp': timezone.now().isoformat()
    })

def verificar_disponibilidad(request, plato_id):
    """API para verificar si un plato está disponible"""
    try:
        plato = PlatoMenu.objects.get(id=plato_id)
        disponible = plato.esta_disponible_ahora()
        
        return JsonResponse({
            'disponible': disponible,
            'nombre': plato.nombre,
            'tiempo_preparacion': plato.tiempo_preparacion if disponible else None
        })
    except PlatoMenu.DoesNotExist:
        return JsonResponse({'error': 'Plato no encontrado'}, status=404)

@login_required
@require_http_methods(["POST"])
def crear_resena(request, plato_id):
    """Vista para crear una nueva reseña"""
    try:
        plato = PlatoMenu.objects.get(id=plato_id)
        calificacion = int(request.POST.get('calificacion', 0))
        comentario = request.POST.get('comentario', '').strip()
        
        if not (1 <= calificacion <= 5):
            return JsonResponse({
                'success': False,
                'error': 'Calificación inválida'
            })
        
        if not comentario:
            return JsonResponse({
                'success': False,
                'error': 'El comentario es obligatorio'
            })
        
        # Verificar si ya existe una reseña del usuario para este plato
        resena_existente = Resena.objects.filter(plato=plato, cliente=request.user).first()
        
        if resena_existente:
            # Actualizar reseña existente
            resena_existente.calificacion = calificacion
            resena_existente.comentario = comentario
            resena_existente.fecha_modificacion = timezone.now()
            resena_existente.save()
            mensaje = 'Reseña actualizada exitosamente'
        else:
            # Crear nueva reseña
            Resena.objects.create(
                plato=plato,
                cliente=request.user,
                calificacion=calificacion,
                comentario=comentario
            )
            mensaje = 'Reseña creada exitosamente'
        
        return JsonResponse({
            'success': True,
            'message': mensaje,
            'calificacion_promedio': plato.calcular_promedio_calificaciones()
        })
        
    except PlatoMenu.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Plato no encontrado'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': 'Error interno del servidor'
        })

@login_required
@require_http_methods(["POST"])
def responder_resena(request, resena_id):
    """Vista para que el restaurante responda a una reseña"""
    if not request.user.is_staff:
        return JsonResponse({
            'success': False,
            'error': 'No tienes permisos para responder reseñas'
        })
    
    try:
        resena = Resena.objects.get(id=resena_id)
        respuesta = request.POST.get('respuesta', '').strip()
        
        if not respuesta:
            return JsonResponse({
                'success': False,
                'error': 'La respuesta es obligatoria'
            })
        
        resena.respuesta_restaurante = respuesta
        resena.fecha_respuesta = timezone.now()
        resena.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Respuesta enviada exitosamente',
            'fecha_respuesta': resena.fecha_respuesta.strftime('%d/%m/%Y %H:%M')
        })
        
    except Resena.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Reseña no encontrada'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': 'Error interno del servidor'
        })

@login_required
@require_http_methods(["DELETE"])
def eliminar_resena(request, resena_id):
    """Vista para eliminar una reseña (solo el autor o staff)"""
    try:
        resena = Resena.objects.get(id=resena_id)
        
        if not (request.user == resena.cliente or request.user.is_staff):
            return JsonResponse({
                'success': False,
                'error': 'No tienes permisos para eliminar esta reseña'
            })
        
        resena.activa = False
        resena.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Reseña eliminada exitosamente',
            'calificacion_promedio': resena.plato.calcular_promedio_calificaciones()
        })
        
    except Resena.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Reseña no encontrada'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': 'Error interno del servidor'
        })

def obtener_resenas_plato(request, plato_id):
    """Vista para obtener las reseñas de un plato específico"""
    try:
        plato = PlatoMenu.objects.get(id=plato_id)
        resenas = Resena.objects.filter(plato=plato, activa=True).select_related('cliente')
        
        resenas_data = []
        for resena in resenas:
            resena_data = {
                'id': resena.id,
                'cliente_nombre': resena.cliente.nombre,
                'calificacion': resena.calificacion,
                'estrellas': resena.estrellas_display,
                'comentario': resena.comentario,
                'fecha': resena.fecha_creacion.strftime('%d/%m/%Y'),
                'puede_editar': resena.puede_editar(request.user) if request.user.is_authenticated else False,
                'puede_responder': resena.puede_responder(request.user) if request.user.is_authenticated else False,
                'respuesta_restaurante': resena.respuesta_restaurante,
                'fecha_respuesta': resena.fecha_respuesta.strftime('%d/%m/%Y %H:%M') if resena.fecha_respuesta else None
            }
            resenas_data.append(resena_data)
        
        return JsonResponse({
            'success': True,
            'resenas': resenas_data,
            'total_resenas': len(resenas_data)
        })
        
    except PlatoMenu.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Plato no encontrado'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': 'Error interno del servidor'
        })

@login_required
def dashboard_resenas(request):
    """Vista para el dashboard de reseñas del staff"""
    if not request.user.is_staff:
        return redirect('usuarios:login')
    
    # Obtener estadísticas generales
    total_resenas = Resena.objects.filter(activa=True).count()
    resenas_respondidas = Resena.objects.filter(activa=True, respuesta_restaurante__isnull=False).count()
    resenas_pendientes = total_resenas - resenas_respondidas
    
    # Calcular promedio general
    promedio_general = Resena.objects.filter(activa=True).aggregate(
        promedio=Avg('calificacion')
    )['promedio'] or 0
    
    context = {
        'total_resenas': total_resenas,
        'resenas_respondidas': resenas_respondidas,
        'resenas_pendientes': resenas_pendientes,
        'promedio_general': promedio_general,
    }
    
    return render(request, 'menu/dashboard_resenas.html', context)

def obtener_todas_resenas(request):
    """Vista para obtener todas las reseñas para el dashboard"""
    if not request.user.is_authenticated or not request.user.is_staff:
        return JsonResponse({
            'success': False,
            'error': 'No tienes permisos para acceder a esta información'
        })
    
    try:
        resenas = Resena.objects.filter(activa=True).select_related('cliente', 'plato').order_by('-fecha_creacion')
        
        resenas_data = []
        for resena in resenas:
            resena_data = {
                'id': resena.id,
                'cliente_nombre': resena.cliente.nombre,
                'plato_id': resena.plato.id,
                'plato_nombre': resena.plato.nombre,
                'calificacion': resena.calificacion,
                'estrellas': resena.estrellas_display,
                'comentario': resena.comentario,
                'fecha': resena.fecha_creacion.strftime('%d/%m/%Y'),
                'respuesta_restaurante': resena.respuesta_restaurante,
                'fecha_respuesta': resena.fecha_respuesta.strftime('%d/%m/%Y %H:%M') if resena.fecha_respuesta else None
            }
            resenas_data.append(resena_data)
        
        return JsonResponse({
            'success': True,
            'resenas': resenas_data,
            'total_resenas': len(resenas_data)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': 'Error interno del servidor'
        })
