from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('control/', views.control, name='control'),
    
    # Dashboard CRM
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    
    # Propiedades
    path('propiedades/', views.PropiedadListView.as_view(), name='propiedad_list'),
    path('propiedades/<int:pk>/', views.PropiedadDetailView.as_view(), name='propiedad_detail'),
    path('propiedades/nueva/', views.PropiedadCreateView.as_view(), name='propiedad_create'),
    path('propiedades/<int:pk>/editar/', views.PropiedadUpdateView.as_view(), name='propiedad_update'),
    path('propiedades/<int:pk>/eliminar/', views.PropiedadDeleteView.as_view(), name='propiedad_delete'),

    # Clientes
    path('clientes/', views.ClienteListView.as_view(), name='cliente_list'),
    path('clientes/<int:pk>/', views.ClienteDetailView.as_view(), name='cliente_detail'),
    path('clientes/nuevo/', views.ClienteCreateView.as_view(), name='cliente_create'),
    path('clientes/<int:pk>/editar/', views.ClienteUpdateView.as_view(), name='cliente_update'),
    path('clientes/<int:pk>/eliminar/', views.ClienteDeleteView.as_view(), name='cliente_delete'),
    
    path('configuracion-correo/', views.ConfiguracionCorreoUpdateView.as_view(), name='configuracion_correo'),
    
    # Proxies WhatsApp
    path('api/whatsapp/qr/', views.whatsapp_proxy_qr, name='whatsapp_proxy_qr'),
    path('api/whatsapp/generate/', views.whatsapp_proxy_generate, name='whatsapp_proxy_generate'),
    path('api/whatsapp/unlink/', views.whatsapp_proxy_unlink, name='whatsapp_proxy_unlink'),

    # AJAX endpoints
    path('api/cliente/crear/', views.ajax_cliente_form, name='ajax_cliente_create'),
    path('api/cliente/<int:pk>/editar/', views.ajax_cliente_form, name='ajax_cliente_update'),
    path('api/propiedad/crear/', views.ajax_propiedad_form, name='ajax_propiedad_create'),
    path('api/propiedad/<int:pk>/editar/', views.ajax_propiedad_form, name='ajax_propiedad_update'),
    path('api/imagen/<int:pk>/eliminar/', views.ajax_delete_imagen, name='ajax_delete_imagen'),
]