from django.urls import path
from . import views

app_name = 'reservas'

urlpatterns = [
    # URLs principales para estudiantes
    path('', views.index, name='index'),
    path('sala/<int:sala_id>/', views.detalle_sala, name='detalle_sala'),
    path('reservar/<int:sala_id>/', views.reservar_sala, name='reservar_sala'),
    
    # URLs del admin
    path('administracion/panel/', views.admin_panel, name='admin_panel'),
    path('administracion/login/', views.admin_login, name='admin_login'),
    path('administracion/logout/', views.admin_logout, name='admin_logout'),
    
    # URLs de gestiónn
    path('administracion/salas/', views.gestion_salas, name='gestion_salas'),
    path('administracion/salas/crear/', views.crear_sala, name='crear_sala'),
    path('administracion/salas/editar/<int:sala_id>/', views.editar_sala, name='editar_sala'),
    path('administracion/salas/eliminar/<int:sala_id>/', views.eliminar_sala, name='eliminar_sala'),
    
    path('administracion/reservas/', views.gestion_reservas, name='gestion_reservas'),
    path('administracion/reservas/crear/', views.crear_reserva_manual, name='crear_reserva_manual'),
    path('administracion/reservas/eliminar/<int:reserva_id>/', views.eliminar_reserva, name='eliminar_reserva'),
    path('administracion/reservas/reducir/<int:reserva_id>/<int:minutos>/', views.reducir_tiempo_reserva, name='reducir_tiempo_reserva'),
    path('administracion/reservas/finalizar/<int:reserva_id>/', views.finalizar_reserva_ahora, name='finalizar_reserva_ahora'),
]