from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from .models import Cita, Mascota, Notificacion
# AQUI AGREGAMOS EL NUEVO FORMULARIO: CancelarMasivoForm
from .forms import RegistroClienteForm, CitaForm, ReservaForm, CancelarMasivoForm

# Vista de la página principal (Home)
def home(request):
    return render(request, 'core/home.html')

# Vista de registro de clientes
def registro(request):
    if request.method == 'POST':
        form = RegistroClienteForm(request.POST)
        if form.is_valid():
            user = form.save()
            try:
                grupo_cliente = Group.objects.get(name='Cliente')
                user.groups.add(grupo_cliente)
            except Group.DoesNotExist:
                pass
            
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
            cita.estado = 'DISPONIBLE'
            cita.save()
            return redirect('lista_citas')
    else:
        form = CitaForm()
    
    return render(request, 'core/crear_horario.html', {'form': form})

# Vista para ver la Agenda (HU002) - CON FILTRO DE FECHA
def lista_citas(request):
    hoy = timezone.now().date()
    # Filtramos: Citas futuras o de hoy
    citas = Cita.objects.filter(fecha__gte=hoy).order_by('fecha', 'hora')
    return render(request, 'core/lista_citas.html', {'citas': citas})

# --- FUNCIÓN: RESERVAR CITA (CLIENTE) ---
@login_required
def reservar_cita(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id)

    if cita.estado != 'DISPONIBLE':
        return redirect('lista_citas')

    if request.method == 'POST':
        form = ReservaForm(request.POST)
        if form.is_valid():
            nueva_mascota = Mascota.objects.create(
                dueno=request.user,
                nombre=form.cleaned_data['nombre_mascota'],
                especie=form.cleaned_data['especie'],
                raza=form.cleaned_data['raza'],
                fecha_nacimiento=form.cleaned_data['fecha_nacimiento']
            )

            cita.cliente = request.user
            cita.mascota = nueva_mascota
            cita.motivo = form.cleaned_data['motivo']
            cita.estado = 'RESERVADA'
            cita.save()

            return redirect('lista_citas')
    else:
        form = ReservaForm()

    return render(request, 'core/reservar_cita.html', {'cita': cita, 'form': form})

# --- FUNCIÓN: CANCELAR CITA INDIVIDUAL (HU005) ---
@staff_member_required
def cancelar_cita(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id)

    if request.method == 'POST':
        cita.estado = 'CANCELADA'
        cita.save()

        if cita.cliente:
            mensaje_alerta = f"Estimado/a {cita.cliente.first_name}, su cita para {cita.mascota.nombre} el día {cita.fecha} ha sido cancelada por la veterinaria."
            Notificacion.objects.create(
                usuario=cita.cliente,
                mensaje=mensaje_alerta
            )
        return redirect('lista_citas')

    return render(request, 'core/cancelar_cita.html', {'cita': cita})

# --- FUNCIÓN: VER NOTIFICACIONES (CLIENTE) ---
@login_required
def mis_notificaciones(request):
    notificaciones = Notificacion.objects.filter(usuario=request.user).order_by('-fecha')
    return render(request, 'core/notificaciones.html', {'notificaciones': notificaciones})

# --- NUEVA FUNCIÓN: CANCELACIÓN MASIVA (HU006 - Gestión de Ausencias) ---
@staff_member_required
def cancelar_masivo(request):
    if request.method == 'POST':
        form = CancelarMasivoForm(request.POST)
        if form.is_valid():
            vet = form.cleaned_data['veterinario']
            inicio = form.cleaned_data['fecha_inicio']
            fin = form.cleaned_data['fecha_fin']

            # 1. Buscar todas las citas (Disponibles o Reservadas) en ese rango
            citas_afectadas = Cita.objects.filter(
                veterinario=vet,
                fecha__range=[inicio, fin],
                estado__in=['DISPONIBLE', 'RESERVADA']
            )

            # 2. Recorrerlas para cancelar y notificar
            for cita in citas_afectadas:
                # Si hay cliente, crear alerta
                if cita.cliente:
                    mensaje = f"URGENTE: Su cita con Dr/a. {vet.last_name} para el {cita.fecha} ha sido cancelada por ausencia médica. Por favor reagende."
                    Notificacion.objects.create(usuario=cita.cliente, mensaje=mensaje)
                
                # Cancelar la cita
                cita.estado = 'CANCELADA'
                cita.save()

            return redirect('lista_citas')
    else:
        form = CancelarMasivoForm()

    return render(request, 'core/cancelar_masivo.html', {'form': form})

# --- NUEVA FUNCIÓN: ELIMINAR NOTIFICACIÓN ---
@login_required
def eliminar_notificacion(request, notificacion_id):
    # Buscamos la notificación
    notificacion = get_object_or_404(Notificacion, id=notificacion_id)
    
    # Seguridad: Solo el dueño de la notificación puede borrarla
    if notificacion.usuario == request.user:
        notificacion.delete()
        
    return redirect('mis_notificaciones')

# --- REAGENDAMIENTO (HU006) ---

@staff_member_required
def reagendar_cita(request, cita_id):
    # 1. Buscamos la cita antigua (la cancelada)
    cita_antigua = get_object_or_404(Cita, id=cita_id)
    
    # 2. Buscamos todos los bloques DISPONIBLES futuros para ofrecer
    hoy = timezone.now().date()
    bloques_disponibles = Cita.objects.filter(
        estado='DISPONIBLE', 
        fecha__gte=hoy
    ).order_by('fecha', 'hora')

    return render(request, 'core/reagendar_seleccionar.html', {
        'cita_antigua': cita_antigua,
        'bloques_disponibles': bloques_disponibles
    })

@staff_member_required
def confirmar_reagendamiento(request, nueva_cita_id, antigua_cita_id):
    # Obtenemos ambas citas
    nueva_cita = get_object_or_404(Cita, id=nueva_cita_id)
    cita_antigua = get_object_or_404(Cita, id=antigua_cita_id)

    # Validamos que el destino esté libre
    if nueva_cita.estado != 'DISPONIBLE':
        return redirect('lista_citas')

    # COPIAMOS LOS DATOS
    nueva_cita.cliente = cita_antigua.cliente
    nueva_cita.mascota = cita_antigua.mascota
    nueva_cita.motivo = cita_antigua.motivo + " (Reagendada)"
    nueva_cita.estado = 'RESERVADA'
    nueva_cita.save()

    # Opcional: Crear notificación de éxito para el cliente
    if nueva_cita.cliente:
        Notificacion.objects.create(
            usuario=nueva_cita.cliente,
            mensaje=f"Su cita ha sido reagendada exitosamente para el {nueva_cita.fecha} a las {nueva_cita.hora} con Dr/a. {nueva_cita.veterinario.last_name}."
        )

    return redirect('lista_citas')