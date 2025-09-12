def carrito_context(request):
    """
    Context processor para hacer disponible la cantidad del carrito en todas las plantillas
    """
    carrito_cantidad = 0
    
    # Obtener cantidad de productos en el carrito desde la sesión
    carrito = request.session.get('carrito', {})
    if carrito:
        carrito_cantidad = sum(item['cantidad'] for item in carrito.values())
    
    return {
        'carrito_cantidad': carrito_cantidad
    }