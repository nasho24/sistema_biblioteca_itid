from django.contrib import admin
from .models import Sala, Reserva

@admin.register(Sala)
class SalaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'capacidad_maxima', 'estado', 'habilitada', 'disponible_para_reserva']
    list_filter = ['estado', 'habilitada']
    list_editable = ['estado', 'habilitada']
    search_fields = ['nombre']
    list_per_page = 20
    
    actions = ['habilitar_salas', 'deshabilitar_salas']

    def habilitar_salas(self, request, queryset):
        updated = queryset.update(habilitada=True)
        self.message_user(request, f'{updated} salas habilitadas correctamente.')
    habilitar_salas.short_description = "Habilitar salas seleccionadas"

    def deshabilitar_salas(self, request, queryset):
        updated = queryset.update(habilitada=False)
        self.message_user(request, f'{updated} salas deshabilitadas correctamente.')
    deshabilitar_salas.short_description = "Deshabilitar salas seleccionadas"

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ['sala', 'rut_reservante', 'fecha_hora_inicio', 'fecha_hora_termino', 'duracion_horas']
    list_editable = ['fecha_hora_inicio', 'fecha_hora_termino'] 
    list_filter = ['sala', 'fecha_hora_inicio']
    search_fields = ['rut_reservante', 'sala__nombre']
    readonly_fields = ['fecha_hora_inicio']
    date_hierarchy = 'fecha_hora_inicio'
    list_per_page = 20

    def duracion_horas(self, obj):
        diferencia = obj.fecha_hora_termino - obj.fecha_hora_inicio
        horas = diferencia.total_seconds() / 3600
        return f"{horas:.1f} horas"
    duracion_horas.short_description = 'Duración'