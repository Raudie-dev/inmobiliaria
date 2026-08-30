from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_publico, name='index'),
    path('propiedades/', views.lista_propiedades_publica, name='propiedades_publica'),
    path('propiedades/<int:pk>/', views.detalle_propiedad_publica, name='detalle_propiedad_publica'),
]