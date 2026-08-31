from django.shortcuts import render, get_object_or_404
from app2.models import Propiedad

def index_publico(request):
    """
    Landing page pública del sistema CRM.
    """
    propiedades = Propiedad.objects.filter(estado='Disponible').order_by('?')[:6]
    return render(request, 'index.html', {'propiedades': propiedades})

from django.db.models import Q

def lista_propiedades_publica(request):
    """
    Vista pública para mostrar propiedades disponibles al estilo e-commerce.
    """
    propiedades = Propiedad.objects.filter(estado='Disponible').order_by('-fecha_creacion')
    
    ubicacion = request.GET.get('ubicacion', '').strip()
    tipo = request.GET.get('tipo', '')
    precio = request.GET.get('precio', '')
    
    if ubicacion:
        propiedades = propiedades.filter(
            Q(zona__icontains=ubicacion) | Q(direccion__icontains=ubicacion) | Q(titulo__icontains=ubicacion)
        )
        
    if tipo and tipo not in ['Cualquier Tipo', 'Todos']:
        propiedades = propiedades.filter(tipo_inmueble=tipo)
        
    if precio and precio != 'Cualquier Precio':
        if '-' in precio:
            parts = precio.split('-')
            min_p = parts[0]
            max_p = parts[1] if len(parts) > 1 else ''
            
            if min_p.isdigit():
                propiedades = propiedades.filter(precio__gte=int(min_p))
            if max_p.isdigit():
                propiedades = propiedades.filter(precio__lte=int(max_p))
                
    context = {
        'propiedades': propiedades,
        'ubicacion_q': ubicacion,
        'tipo_q': tipo,
        'precio_q': precio
    }
    return render(request, 'propiedades_ecommerce.html', context)

def detalle_propiedad_publica(request, pk):
    """
    Vista pública para ver el detalle de una propiedad específica y su galería de imágenes.
    """
    propiedad = get_object_or_404(Propiedad, pk=pk, estado='Disponible')
    return render(request, 'propiedad_detalle_publico.html', {'propiedad': propiedad})
