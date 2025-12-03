from django.contrib import admin
from .models import Mascota, Cita, Notificacion

# Esto permite ver las tablas en http://127.0.0.1:8000/admin
admin.site.register(Mascota)
admin.site.register(Cita)
admin.site.register(Notificacion)