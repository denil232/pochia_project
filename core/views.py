from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from .models import Cita, Mascota
from .forms import RegistroClienteForm, CitaForm, ReservaForm

# Vista de la página principal (Home)
def home(request):
    return render(request, 'core/home.html')

# Vista de registro de clientes
def registro(request):
    if request.method == 'POST':
        form = RegistroClienteForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Asignar grupo 'Cliente' automáticamente
            try:
                grupo_cliente = Group.objects.get(name='Cliente')
                user.groups.add(grupo_cliente)
            except Group.DoesNotExist:
                pass # Si el grupo no existe, no falla, pero idealmente debería existir
            
            # Loguear al usuario inmediatamente y enviarlo al inicio
            login(request, user)
            return redirect('home')
    else:
        form = RegistroClienteForm()
    
    return render(request, 'registration/registro.html', {'form': form})

# Vista para que la Recepcionista cree bloques vacíos
@staff_member_required
def crear_horario(request):
    if request.method == 'POST':
        form = CitaForm(request.POST)
        if form.is_valid():
            cita = form.save(commit=False)
            cita.estado = 'DISPONIBLE' # Se crea libre por defecto
            cita.save()
            return redirect('lista_citas')
    else:
        form = CitaForm()
    
    return render(request, 'core/crear_horario.html', {'form': form})

# Vista para ver la Agenda (HU002)
def lista_citas(request):
    # Traemos todas las citas ordenadas por fecha y hora
    citas = Cita.objects.all().order_by('fecha', 'hora')
    return render(request, 'core/lista_citas.html', {'citas': citas})

# --- NUEVA FUNCIÓN: RESERVAR CITA (CLIENTE) ---
@login_required
def reservar_cita(request, cita_id):
    # Buscamos la cita por su ID. Si no existe, da error 404.
    cita = get_object_or_404(Cita, id=cita_id)

    # Validación de seguridad: Si ya está ocupada, no dejar reservar
    if cita.estado != 'DISPONIBLE':
        return redirect('lista_citas')

    if request.method == 'POST':
        form = ReservaForm(request.POST)
        if form.is_valid():
            # 1. Crear la Mascota y asignarla al dueño actual
            nueva_mascota = Mascota.objects.create(
                dueno=request.user,
                nombre=form.cleaned_data['nombre_mascota'],
                especie=form.cleaned_data['especie'],  # <--- AQUÍ AGREGUÉ EL NUEVO CAMPO
                raza=form.cleaned_data['raza'],
                fecha_nacimiento=form.cleaned_data['fecha_nacimiento']
            )

            # 2. Actualizar la Cita con los datos del cliente y la mascota
            cita.cliente = request.user
            cita.mascota = nueva_mascota
            cita.motivo = form.cleaned_data['motivo']
            cita.estado = 'RESERVADA'
            cita.save()

            return redirect('lista_citas')
    else:
        form = ReservaForm()

    return render(request, 'core/reservar_cita.html', {'cita': cita, 'form': form})