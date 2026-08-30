from django import forms
from .models import Cliente, Propiedad, PropiedadImagen
import re

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = '__all__'
    
    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono', '')
        if telefono:
            return re.sub(r'\D', '', telefono)
        return telefono

class PropiedadForm(forms.ModelForm):
    class Meta:
        model = Propiedad
        fields = ['titulo', 'tipo_operacion', 'tipo_inmueble', 'precio', 'superficie', 'habitaciones', 'banos', 'direccion', 'zona', 'estado', 'descripcion']
