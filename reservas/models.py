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
        db_table = 'salas' 
    
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
    duracion_minutos = models.IntegerField(default=120)  # Nueva campo para duración
    
    class Meta:
        db_table = 'reservas'
    
    def save(self, *args, **kwargs):
    # Si se proporciona duración, calcular término
        if not self.fecha_hora_termino and hasattr(self, 'duracion_minutos'):
            self.fecha_hora_termino = self.fecha_hora_inicio + timedelta(minutes=self.duracion_minutos)
    
    # Validar que no exceda las 2 horas (120 minutos)
        if self.fecha_hora_termino:
            diferencia = self.fecha_hora_termino - self.fecha_hora_inicio
            minutos_totales = diferencia.total_seconds() / 60
        
        # Solo validar duración para reservas futuras o normales
        # Permitir finalización inmediata (duración = 0 o negativa)
        if minutos_totales > 120:  # 2 horas en minutos
            raise ValueError("La reserva no puede exceder las 2 horas")
        if minutos_totales < 0:
            # Para finalización inmediata, establecer duración mínima
            self.duracion_minutos = 1
        else:
            self.duracion_minutos = int(minutos_totales)
            
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

def finalizar_ahora(self):
        """
        Finalizar la reserva inmediatamente sin activar validaciones normales
        """
        from django.utils import timezone
        ahora = timezone.now()
        
        # Si ya está finalizada, no hacer nada
        if self.fecha_hora_termino <= ahora:
            return False
            
        # Calcular duración real hasta ahora
        duracion_real = (ahora - self.fecha_hora_inicio).total_seconds() / 60
        
        # Si la duración es muy corta, establecer mínimo 1 minuto
        if duracion_real < 1:
            duracion_real = 1
            
        self.fecha_hora_termino = ahora
        self.duracion_minutos = int(duracion_real)
        
        # Guardar sin validaciones estrictas
        super().save()
        return True

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
    
@property
def esta_activa(self):
    from django.utils import timezone
    ahora = timezone.now()
    return self.fecha_hora_inicio <= ahora <= self.fecha_hora_termino