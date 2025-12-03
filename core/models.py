from django.db import models
from django.contrib.auth.models import User

# Estados posibles de una cita médica
ESTADOS_CITA = [
    ('DISPONIBLE', 'Disponible'),   # Bloque libre creado por la recepcionista/vet
    ('RESERVADA', 'Reservada'),     # Cliente ya tomó la hora
    ('CANCELADA', 'Cancelada'),     # Veterinario canceló (dispara alerta HU005)
    ('REALIZADA', 'Realizada'),     # Cita terminada
]

class Mascota(models.Model):
    # Opciones de animales
    ESPECIES = [
        ('Perro', 'Perro'),
        ('Gato', 'Gato'),
        ('Ave', 'Ave'),
        ('Hamster', 'Hamster'),
        ('Otro', 'Otro'),
    ]

    dueno = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mascotas')
    nombre = models.CharField(max_length=100)
    
    # --- NUEVO CAMPO ---
    especie = models.CharField(max_length=20, choices=ESPECIES, default='Perro')
    # -------------------
    
    raza = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField()

    def __str__(self):
        return f"{self.nombre} ({self.especie} - {self.raza})"

class Cita(models.Model):
    # HU002: Identificar veterinario por bloque
    veterinario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='agenda_veterinario')
    
    # Datos del Cliente (puede estar vacío si el bloque está "DISPONIBLE")
    cliente = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='citas_cliente')
    mascota = models.ForeignKey(Mascota, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Fecha y Hora del bloque de atención
    fecha = models.DateField()
    hora = models.TimeField()
    
    motivo = models.TextField(blank=True, null=True) # Con qué motivo llega
    estado = models.CharField(max_length=20, choices=ESTADOS_CITA, default='DISPONIBLE')
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Ordenar por fecha y hora (lo más próximo primero)
        ordering = ['fecha', 'hora']

    def __str__(self):
        return f"{self.fecha} {self.hora} - Dr. {self.veterinario.first_name} ({self.estado})"

# HU005: Notificaciones (Cuando se cancela una cita)
class Notificacion(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE) # A quién le avisamos
    mensaje = models.TextField()
    leido = models.BooleanField(default=False) # Para saber si ya vio la alerta
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Alerta para {self.usuario.username}"
    
