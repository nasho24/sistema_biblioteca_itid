from django import forms
from .models import Reserva

class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['rut_reservante']
        widgets = {
            'rut_reservante': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '12.345.678-9',
                'pattern': '[0-9]{1,2}\.[0-9]{3}\.[0-9]{3}-[0-9kK]{1}',
                'title': 'Formato: 12.345.678-9'
            }),
        }
        labels = {
            'rut_reservante': 'RUT del reservante',
        }
    
    def clean_rut_reservante(self):
        rut = self.cleaned_data.get('rut_reservante')
        # Validación básica de RUT (puedes mejorarla)
        if not rut:
            raise forms.ValidationError('El RUT es obligatorio')
        
        # Limpiar y formatear RUT
        rut = rut.upper().replace('.', '').replace('-', '')
        if len(rut) < 8:
            raise forms.ValidationError('El RUT debe tener al menos 8 dígitos')
        
        return rut