from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from .models import User_admin
from .crud import crear_prueba, obtener_pruebas, eliminar_prueba


def login(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        password = request.POST.get('password', '')

        try:
            user = User_admin.objects.get(nombre=nombre)
            if user.bloqueado:
                messages.error(request, 'Usuario bloqueado')
            elif user.password == password or check_password(password, user.password):
                request.session['user_admin_id'] = user.id
                return redirect('dashboard')
            else:
                messages.error(request, 'Contraseña incorrecta')
            return render(request, 'login.html')
        except User_admin.DoesNotExist:
            messages.error(request, 'Usuario no encontrado')
            return render(request, 'login.html')

    return render(request, 'login.html')


def control(request):
    user_id = request.session.get('user_admin_id')
    if not user_id:
        messages.error(request, 'Debe iniciar sesión primero')
        return redirect('login')
    try:
        user = User_admin.objects.get(id=user_id)
    except User_admin.DoesNotExist:
        messages.error(request, 'Usuario no encontrado')
        return redirect('login')

    # CRUD Prueba
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        fecha = request.POST.get('fecha')
        socio = request.POST.get('socio') == 'on'
        if nombre and fecha:
            crear_prueba(nombre, fecha, socio)
            messages.success(request, 'Registro creado correctamente')
        else:
            messages.error(request, 'Todos los campos son obligatorios')

    if request.method == 'POST' and 'eliminar_id' in request.POST:
        eliminar_prueba(request.POST.get('eliminar_id'))
        messages.success(request, 'Registro eliminado')

    pruebas = obtener_pruebas()
    return render(request, 'control.html', {'pruebas': pruebas})

# --- Mixin para proteger vistas ---
from django.utils.decorators import method_decorator
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse
from django.template.loader import render_to_string
from .models import Propiedad, Cliente, NotificacionMatch, ConfiguracionCorreo, PropiedadImagen
from .forms import ClienteForm, PropiedadForm

class AdminLoginRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.session.get('user_admin_id'):
            messages.error(request, 'Debe iniciar sesión primero')
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)

from .utils import disparar_notificaciones_asincronas

# --- Funciones Auxiliares ---
def generar_matches_para_propiedad(propiedad, request):
    if propiedad.estado != 'Disponible':
        return
    
    # Filtrar clientes activos que coincidan
    clientes_compatibles = Cliente.objects.filter(
        activo=True,
        tipo_inmueble=propiedad.tipo_inmueble,
        zona_interes__icontains=propiedad.zona,
        presupuesto_min__lte=propiedad.precio,
        presupuesto_max__gte=propiedad.precio
    )
    
    # Crear notificaciones y coleccionarlas
    nuevos_matches = []
    for cliente in clientes_compatibles:
        match, created = NotificacionMatch.objects.get_or_create(
            cliente=cliente,
            propiedad=propiedad,
            defaults={'canal': 'Email', 'estado': 'Pendiente'}
        )
        if created or match.estado == 'Pendiente':
            nuevos_matches.append(match)
            
    if nuevos_matches:
        # Usar el dominio de producción indicado por el usuario
        dominio = "https://demos.raudie.net"
        disparar_notificaciones_asincronas(nuevos_matches, dominio)

# --- Dashboard ---
class DashboardView(AdminLoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_propiedades'] = Propiedad.objects.filter(estado='Disponible').count()
        context['clientes_activos'] = Cliente.objects.filter(activo=True).count()
        context['ultimos_matches'] = NotificacionMatch.objects.select_related('cliente', 'propiedad').order_by('-fecha_envio')[:5]
        return context

# --- Vistas CRUD de Propiedades ---
class PropiedadListView(AdminLoginRequiredMixin, ListView):
    model = Propiedad
    template_name = 'propiedad_list.html'
    context_object_name = 'propiedades'
    ordering = ['-fecha_creacion']

class PropiedadDetailView(AdminLoginRequiredMixin, DetailView):
    model = Propiedad
    template_name = 'propiedad_detail.html'
    context_object_name = 'propiedad'

class PropiedadCreateView(AdminLoginRequiredMixin, CreateView):
    model = Propiedad
    template_name = 'propiedad_form.html'
    fields = '__all__'
    success_url = reverse_lazy('propiedad_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        imagenes = self.request.FILES.getlist('imagenes_galeria')
        for img in imagenes:
            PropiedadImagen.objects.create(propiedad=self.object, imagen=img)
        generar_matches_para_propiedad(self.object, self.request)
        return response

class PropiedadUpdateView(AdminLoginRequiredMixin, UpdateView):
    model = Propiedad
    template_name = 'propiedad_form.html'
    fields = '__all__'
    success_url = reverse_lazy('propiedad_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        imagenes = self.request.FILES.getlist('imagenes_galeria')
        for img in imagenes:
            PropiedadImagen.objects.create(propiedad=self.object, imagen=img)
        generar_matches_para_propiedad(self.object, self.request)
        return response

class PropiedadDeleteView(AdminLoginRequiredMixin, DeleteView):
    model = Propiedad
    template_name = 'propiedad_confirm_delete.html'
    success_url = reverse_lazy('propiedad_list')

# --- Vistas CRUD de Clientes ---
class ClienteListView(AdminLoginRequiredMixin, ListView):
    model = Cliente
    template_name = 'cliente_list.html'
    context_object_name = 'clientes'
    ordering = ['-fecha_registro']

class ClienteDetailView(AdminLoginRequiredMixin, DetailView):
    model = Cliente
    template_name = 'cliente_detail.html'
    context_object_name = 'cliente'

class ClienteCreateView(AdminLoginRequiredMixin, CreateView):
    model = Cliente
    template_name = 'cliente_form.html'
    fields = '__all__'
    success_url = reverse_lazy('cliente_list')

    def form_valid(self, form):
        import re
        telefono = form.cleaned_data.get('telefono', '')
        if telefono:
            form.instance.telefono = re.sub(r'\D', '', telefono)
        return super().form_valid(form)

class ClienteUpdateView(AdminLoginRequiredMixin, UpdateView):
    model = Cliente
    template_name = 'cliente_form.html'
    fields = '__all__'
    success_url = reverse_lazy('cliente_list')

    def form_valid(self, form):
        import re
        telefono = form.cleaned_data.get('telefono', '')
        if telefono:
            form.instance.telefono = re.sub(r'\D', '', telefono)
        return super().form_valid(form)

class ClienteDeleteView(AdminLoginRequiredMixin, DeleteView):
    model = Cliente
    template_name = 'cliente_confirm_delete.html'
    success_url = reverse_lazy('cliente_list')

# --- Configuración de Correo ---
class ConfiguracionCorreoUpdateView(AdminLoginRequiredMixin, UpdateView):
    model = ConfiguracionCorreo
    template_name = 'configuracion_correo.html'
    fields = ['email_host_user', 'email_host_password']
    success_url = reverse_lazy('configuracion_correo')

    def get_object(self, queryset=None):
        return ConfiguracionCorreo.load()

    def form_valid(self, form):
        messages.success(self.request, "Configuración SMTP actualizada con éxito.")
        return super().form_valid(form)

# --- Proxies para WhatsApp Gateway ---
import urllib.request
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

def _check_admin(request):
    return request.session.get('user_admin_id') is not None

def whatsapp_proxy_qr(request):
    if not _check_admin(request): return JsonResponse({'error': 'Unauthorized'}, status=401)
    try:
        req = urllib.request.Request('http://127.0.0.1:3000/qr')
        with urllib.request.urlopen(req) as response:
            return JsonResponse(json.loads(response.read().decode()))
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def whatsapp_proxy_generate(request):
    if not _check_admin(request): return JsonResponse({'error': 'Unauthorized'}, status=401)
    try:
        req = urllib.request.Request('http://127.0.0.1:3000/generate', method='POST')
        with urllib.request.urlopen(req) as response:
            return JsonResponse(json.loads(response.read().decode()))
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def whatsapp_proxy_unlink(request):
    if not _check_admin(request): return JsonResponse({'error': 'Unauthorized'}, status=401)
    try:
        req = urllib.request.Request('http://127.0.0.1:3000/unlink', method='POST')
        with urllib.request.urlopen(req) as response:
            return JsonResponse(json.loads(response.read().decode()))
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
# --- AJAX Views para Modales ---
def ajax_cliente_form(request, pk=None):
    if not request.session.get('user_admin_id'):
        return JsonResponse({'error': 'Unauthorized'}, status=401)
        
    cliente = get_object_or_404(Cliente, pk=pk) if pk else None

    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = ClienteForm(instance=cliente)
    
    html = render_to_string('cliente_form_ajax.html', {'form': form}, request=request)
    return JsonResponse({'html': html})

def ajax_propiedad_form(request, pk=None):
    if not request.session.get('user_admin_id'):
        return JsonResponse({'error': 'Unauthorized'}, status=401)
        
    propiedad = get_object_or_404(Propiedad, pk=pk) if pk else None

    if request.method == 'POST':
        form = PropiedadForm(request.POST, instance=propiedad)
        if form.is_valid():
            prop = form.save()
            
            # Guardar nuevas imágenes si hay
            if 'imagenes_galeria' in request.FILES:
                for f in request.FILES.getlist('imagenes_galeria'):
                    PropiedadImagen.objects.create(propiedad=prop, imagen=f)

            # Actualizar orden y portadas
            import json
            imagenes_data = request.POST.get('imagenes_data', '[]')
            try:
                datos = json.loads(imagenes_data)
                for item in datos:
                    img_id = item.get('id')
                    orden = item.get('orden', 0)
                    es_portada = item.get('es_portada', False)
                    img = PropiedadImagen.objects.filter(id=img_id, propiedad=prop).first()
                    if img:
                        img.orden = orden
                        img.es_portada = es_portada
                        img.save()
            except Exception as e:
                print("Error actualizando imagenes:", e)

            # Generar matches
            generar_matches_para_propiedad(prop, request)
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = PropiedadForm(instance=propiedad)
        # Traer imágenes existentes para la UI
        imagenes = [{'id': img.id, 'url': img.imagen.url, 'es_portada': img.es_portada, 'orden': img.orden} for img in getattr(propiedad, 'imagenes', PropiedadImagen.objects.none()).all()]
        html = render_to_string('propiedad_form_ajax.html', {'form': form, 'imagenes_existentes': imagenes}, request=request)
        return JsonResponse({'html': html, 'imagenes': imagenes})

def ajax_delete_imagen(request, pk):
    if not request.session.get('user_admin_id'):
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    if request.method == 'POST':
        img = get_object_or_404(PropiedadImagen, pk=pk)
        img.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})
