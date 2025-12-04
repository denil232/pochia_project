from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils import timezone
import datetime
from .models import Cita

# --- GENERADOR DE HORARIOS (De 08:00 a 20:00 cada 30 min) ---
HORARIOS_CHOICES = []
for h in range(8, 21): # Desde las 8 hasta las 20 horas
    for m in (0, 30):
        # Formato visual: "08:00", "08:30", etc.
        hora_str = f"{h:02d}:{m:02d}"
        HORARIOS_CHOICES.append((hora_str, hora_str))

# --- FORMULARIO 1: REGISTRO DE CLIENTES ---
class RegistroClienteForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, label="Nombre")
    last_name = forms.CharField(max_length=30, required=True, label="Apellido")
    email = forms.EmailField(max_length=254, required=True, label="Email")

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')


# --- FORMULARIO 2: CREAR HORARIOS (RECEPCIONISTA) ---
class CitaForm(forms.ModelForm):
    # CAMBIO IMPORTANTE: Usamos ChoiceField (Lista) en vez de TimeInput (Reloj)
    hora = forms.ChoiceField(
        choices=HORARIOS_CHOICES,
        label="Hora de Atención",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Cita
        fields = ['veterinario', 'fecha', 'hora']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'veterinario': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['veterinario'].queryset = User.objects.filter(groups__name='Veterinario')
        self.fields['veterinario'].label = "Médico Veterinario"
        self.fields['fecha'].widget.attrs['min'] = timezone.now().date()

    # --- VALIDACIÓN: EVITAR DUPLICADOS ---
    def clean(self):
        cleaned_data = super().clean()
        veterinario = cleaned_data.get('veterinario')
        fecha = cleaned_data.get('fecha')
        hora = cleaned_data.get('hora')

        if veterinario and fecha and hora:
            # Buscamos si existe choque de horario
            existe = Cita.objects.filter(
                veterinario=veterinario,
                fecha=fecha,
                hora=hora
            ).exists()

            if existe:
                # Marcamos el error en el campo 'hora' para que salga rojo
                self.add_error('hora', f"El Dr/a. {veterinario.last_name} ya tiene agenda a las {hora}.")
        
        return cleaned_data


# --- FORMULARIO 3: REALIZAR RESERVA (CLIENTE) ---
class ReservaForm(forms.Form):
    nombre_mascota = forms.CharField(max_length=100, label="Nombre de la Mascota")
    
    especie = forms.ChoiceField(
        choices=[('Perro', 'Perro'), ('Gato', 'Gato'), ('Ave', 'Ave'), ('Hamster', 'Hamster'), ('Otro', 'Otro')],
        label="Tipo de Animal",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    raza = forms.CharField(max_length=100, label="Raza")
    
    fecha_nacimiento = forms.DateField(
        label="Fecha de Nacimiento de la Mascota",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    
    motivo = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        label="Motivo de la consulta"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fecha_nacimiento'].widget.attrs['max'] = timezone.now().date()

    def clean_fecha_nacimiento(self):
        fecha = self.cleaned_data.get('fecha_nacimiento')
        if fecha and fecha > timezone.now().date():
            raise forms.ValidationError("La mascota no puede haber nacido en el futuro.")
        return fecha