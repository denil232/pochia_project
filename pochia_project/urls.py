from django.contrib import admin
from django.urls import path, include
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    # Rutas de autenticación (login, logout) que vienen con Django
    path('accounts/', include('django.contrib.auth.urls')),
    # Nuestra ruta de registro personalizada
    path('registro/', views.registro, name='registro'),
    # Página de inicio
    path('', views.home, name='home'),

    # NUEVAS RUTAS
    path('agenda/', views.lista_citas, name='lista_citas'),
    path('crear-horario/', views.crear_horario, name='crear_horario'),
    # NUEVA RUTA: Recibe el ID de la cita (ej: /reservar/1/)
    path('reservar/<int:cita_id>/', views.reservar_cita, name='reservar_cita'),
    path('cancelar/<int:cita_id>/', views.cancelar_cita, name='cancelar_cita'),
    path('notificaciones/', views.mis_notificaciones, name='mis_notificaciones'),
]