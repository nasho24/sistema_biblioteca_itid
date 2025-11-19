from django.db import models
from django.utils import timezone
from datetime import timedelta

class Sala(models.Model):
    ESTADOS = [
        ('disponible', 'Disponible'),
        ('mantenimiento', 'En Mantenimiento'),
    ]
    
    nombre = models.CharField(max_length=100, unique=True)
    capacidad_maxima = models.IntegerField()
    estado = models.CharField(max_length=20, choices=ESTADOS, default='disponible')
    habilitada = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'salas'  # Nombre específico para Oracle
    
    def __str__(self):
        return f"{self.nombre} (Capacidad: {self.capacidad_maxima})"
    
    @property
    def disponible_para_reserva(self):
        if not self.habilitada or self.estado != 'disponible':
            return False
        
        ahora = timezone.now()
        reserva_activa = self.reserva_set.filter(
            fecha_hora_inicio__lte=ahora,
            fecha_hora_termino__gte=ahora
        ).exists()
        
        return not reserva_activa

class Reserva(models.Model):
    rut_reservante = models.CharField(max_length=12)
    sala = models.ForeignKey(Sala, on_delete=models.CASCADE)
    fecha_hora_inicio = models.DateTimeField(default=timezone.now)
    fecha_hora_termino = models.DateTimeField()
    
    class Meta:
        db_table = 'reservas'  # Nombre específico para Oracle
    
    def save(self, *args, **kwargs):
        if not self.fecha_hora_termino:
            self.fecha_hora_termino = self.fecha_hora_inicio + timedelta(hours=2)
        
        # Validar que no exceda 2 horas
        diferencia = self.fecha_hora_termino - self.fecha_hora_inicio
        if diferencia.total_seconds() > 7200:  # 2 horas en segundos
            raise ValueError("La reserva no puede exceder las 2 horas")
            
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Reserva {self.sala.nombre} - {self.rut_reservante}"
    
    @property
    def tiempo_restante(self):
        from django.utils import timezone
        ahora = timezone.now()
        if self.fecha_hora_termino > ahora:
            diferencia = self.fecha_hora_termino - ahora
            horas = int(diferencia.total_seconds() // 3600)
            minutos = int((diferencia.total_seconds() % 3600) // 60)
            return {'horas': horas, 'minutos': minutos}
        return {'horas': 0, 'minutos': 0}
