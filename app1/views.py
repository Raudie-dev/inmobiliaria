from django.shortcuts import render, get_object_or_404
from app2.models import Propiedad

def index_publico(request):
    """
    Landing page pública del sistema CRM.
    """
    propiedades = Propiedad.objects.filter(estado='Disponible').order_by('?')[:6]
    return render(request, 'index_publico.html', {'propiedades': propiedades})

def lista_propiedades_publica(request):
    """
    Vista pública para mostrar propiedades disponibles al estilo e-commerce.
    """
    propiedades = Propiedad.objects.filter(estado='Disponible').order_by('-fecha_creacion')
    return render(request, 'propiedades_ecommerce.html', {'propiedades': propiedades})

def detalle_propiedad_publica(request, pk):
    """
    Vista pública para ver el detalle de una propiedad específica y su galería de imágenes.
    """
    propiedad = get_object_or_404(Propiedad, pk=pk, estado='Disponible')
    return render(request, 'propiedad_detalle_publico.html', {'propiedad': propiedad})
