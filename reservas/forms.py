from django import forms
from .models import Reserva

class ReservaForm(forms.ModelForm):
    DURACION_OPCIONES = [
        (15, '15 minutos'),
        (30, '30 minutos'), 
        (60, '1 hora'),
        (90, '1 hora 30 minutos'),
        (120, '2 horas (máximo)'),
    ]
    
    duracion_minutos = forms.ChoiceField(
        choices=DURACION_OPCIONES,
        initial=120,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'duracion-select'
        }),
        label='Duración de la reserva'
    )
    
    class Meta:
        model = Reserva
        fields = ['rut_reservante', 'duracion_minutos']
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
        if not rut:
            raise forms.ValidationError('El RUT es obligatorio')
        
        # Limpiar y formatear RUT
        rut = rut.upper().replace('.', '').replace('-', '')
        if len(rut) < 8:
            raise forms.ValidationError('El RUT debe tener al menos 8 dígitos')
        
        return rut
    
    def clean_duracion_minutos(self):
        duracion = self.cleaned_data.get('duracion_minutos')
        try:
            duracion = int(duracion)
            if duracion < 1 or duracion > 120:
                raise forms.ValidationError('La duración debe estar entre 1 minuto y 2 horas')
            return duracion
        except (ValueError, TypeError):
            raise forms.ValidationError('Duración inválida')