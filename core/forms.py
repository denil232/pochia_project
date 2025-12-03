from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Cita

# --- FORMULARIO 1: REGISTRO DE CLIENTES ---
class RegistroClienteForm(UserCreationForm):
    # Hacemos obligatorios el nombre, apellido y email
    first_name = forms.CharField(max_length=30, required=True, label="Nombre")
    last_name = forms.CharField(max_length=30, required=True, label="Apellido")
    email = forms.EmailField(max_length=254, required=True, label="Email")

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')


# --- FORMULARIO 2: CREAR HORARIOS (RECEPCIONISTA) ---
class CitaForm(forms.ModelForm):
    class Meta:
        model = Cita
        fields = ['veterinario', 'fecha', 'hora']
        
        # Aquí configuramos que se vean como calendarios y relojes
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'hora': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'veterinario': forms.Select(attrs={'class': 'form-control'}),
        }

    # Este bloque sirve para que en la lista SOLO salgan los Veterinarios
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtramos usuarios que pertenezcan al grupo 'Veterinario'
        self.fields['veterinario'].queryset = User.objects.filter(groups__name='Veterinario')
        self.fields['veterinario'].label = "Médico Veterinario"

# --- FORMULARIO 3: REALIZAR RESERVA (CLIENTE) ---
class ReservaForm(forms.Form):
    # Datos de la Mascota
    nombre_mascota = forms.CharField(max_length=100, label="Nombre de la Mascota")
    
    # --- NUEVO CAMPO ---
    especie = forms.ChoiceField(
        choices=[('Perro', 'Perro'), ('Gato', 'Gato'), ('Ave', 'Ave'), ('Hamster', 'Hamster'), ('Otro', 'Otro')],
        label="Tipo de Animal",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    # -------------------

    raza = forms.CharField(max_length=100, label="Raza")
    
    fecha_nacimiento = forms.DateField(
        label="Fecha de Nacimiento de la Mascota",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    motivo = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        label="Motivo de la consulta"
    )
    # Datos de la Cita
    motivo = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        label="Motivo de la consulta"
    )