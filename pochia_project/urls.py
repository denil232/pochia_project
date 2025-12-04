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
    path('cancelacion-masiva/', views.cancelar_masivo, name='cancelar_masivo'),
    path('notificaciones/borrar/<int:notificacion_id>/', views.eliminar_notificacion, name='eliminar_notificacion'),
    path('reagendar/<int:cita_id>/', views.reagendar_cita, name='reagendar_cita'),
    path('reagendar-confirmar/<int:nueva_cita_id>/<int:antigua_cita_id>/', views.confirmar_reagendamiento, name='confirmar_reagendamiento'),
]