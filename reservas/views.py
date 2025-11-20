from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib import messages
from .models import Sala, Reserva
from .forms import ReservaForm
from datetime import timedelta
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test


def es_staff(user):
    return user.is_staff

def index(request):
    """
    Vista principal que muestra todas las salas disponibles
    """
    salas = Sala.objects.filter(habilitada=True).order_by('nombre')
    
    # Verificar disponibilidad de cada sala
    for sala in salas:
        sala.disponible = sala.disponible_para_reserva
    
    context = {
        'salas': salas,
        'ahora': timezone.now()
    }
    return render(request, 'index.html', context)

def detalle_sala(request, sala_id):
    """
    Vista que muestra el detalle de una sala específica
    """
    sala = get_object_or_404(Sala, id=sala_id, habilitada=True)
    
    # Obtener reserva activa si existe
    reserva_activa = None
    ahora = timezone.now()
    
    reservas_activas = Reserva.objects.filter(
        sala=sala,
        fecha_hora_inicio__lte=ahora,
        fecha_hora_termino__gte=ahora
    ).order_by('-fecha_hora_inicio')
    
    if reservas_activas.exists():
        reserva_activa = reservas_activas.first()
    
    # Obtener próximas reservas (próximas 24 horas)
    proximas_reservas = Reserva.objects.filter(
        sala=sala,
        fecha_hora_inicio__gt=ahora,
        fecha_hora_inicio__lt=ahora + timezone.timedelta(hours=24)
    ).order_by('fecha_hora_inicio')
    
    context = {
        'sala': sala,
        'reserva_activa': reserva_activa,
        'proximas_reservas': proximas_reservas,
        'disponible': sala.disponible_para_reserva,
        'ahora': ahora
    }
    return render(request, 'detalle_sala.html', context)

def reservar_sala(request, sala_id):
    """
    Vista para realizar una reserva con duración personalizada
    """
    sala = get_object_or_404(Sala, id=sala_id, habilitada=True)
    
    # Verificar que la sala esté disponible
    if not sala.disponible_para_reserva:
        messages.error(request, 'Esta sala no está disponible para reservar en este momento.')
        return redirect('reservas:detalle_sala', sala_id=sala_id)
    
    if request.method == 'POST':
        form = ReservaForm(request.POST)
        if form.is_valid():
            reserva = form.save(commit=False)
            reserva.sala = sala
            reserva.fecha_hora_inicio = timezone.now()
            
            # Calcular fecha_hora_termino basado en la duración
            duracion_minutos = form.cleaned_data['duracion_minutos']
            reserva.fecha_hora_termino = timezone.now() + timedelta(minutes=duracion_minutos)
            
            try:
                reserva.save()
                
                # Mensaje con la duración seleccionada
                if duracion_minutos == 120:
                    duracion_texto = "2 horas"
                elif duracion_minutos == 60:
                    duracion_texto = "1 hora" 
                elif duracion_minutos == 90:
                    duracion_texto = "1 hora 30 minutos"
                else:
                    duracion_texto = f"{duracion_minutos} minutos"
                
                messages.success(request, f'¡Reserva realizada con éxito para la sala {sala.nombre} por {duracion_texto}!')
                return redirect('reservas:index')
                
            except ValueError as e:
                messages.error(request, str(e))
            except Exception as e:
                messages.error(request, 'Error al crear la reserva. Por favor, intenta nuevamente.')
    else:
        form = ReservaForm()
    
    context = {
        'sala': sala,
        'form': form
    }
    return render(request, 'reservar_sala.html', context)

@login_required
@user_passes_test(es_staff, login_url='/administracion/login/')
def admin_panel(request):
    """
    Panel de administración personalizado para bibliotecarios
    """
    # Estadísticas
    total_salas = Sala.objects.count()
    salas_disponibles = Sala.objects.filter(habilitada=True, estado='disponible').count()
    
    # Calcular salas ocupadas
    ahora = timezone.now()
    reservas_activas = Reserva.objects.filter(
        fecha_hora_inicio__lte=ahora,
        fecha_hora_termino__gte=ahora
    ).select_related('sala')
    
    salas_ocupadas = reservas_activas.count()
    
    # Reservas de hoy
    hoy = timezone.now().date()
    reservas_hoy = Reserva.objects.filter(
        fecha_hora_inicio__date=hoy
    ).count()
    
    context = {
        'total_salas': total_salas,
        'salas_disponibles': salas_disponibles,
        'salas_ocupadas': salas_ocupadas,
        'reservas_hoy': reservas_hoy,
        'reservas_activas': reservas_activas,
    }
    
    return render(request, 'admin_panel.html', context)

def es_staff(user):
    """Verifica si el usuario es staff"""
    return user.is_staff

def admin_login(request):
    """
    Login personalizado para el panel de administración
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.is_staff:
            login(request, user)
            messages.success(request, f'¡Bienvenido/a, {user.username}!')
            return redirect('reservas:admin_panel')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos. Acceso restringido al personal autorizado.')
    
    return render(request, 'admin_login.html')

def admin_logout(request):
    """
    Cerrar sesión del panel de administración
    """
    logout(request)
    messages.success(request, 'Sesión cerrada correctamente.')
    return redirect('reservas:admin_login') 

def admin_panel(request):
    """
    Panel de administración personalizado para bibliotecarios
    """
    # Estadísticas
    total_salas = Sala.objects.count()
    salas_disponibles = Sala.objects.filter(habilitada=True, estado='disponible').count()
    
    # Calcular salas ocupadas
    ahora = timezone.now()
    reservas_activas = Reserva.objects.filter(
        fecha_hora_inicio__lte=ahora,
        fecha_hora_termino__gte=ahora
    ).select_related('sala')
    
    salas_ocupadas = reservas_activas.count()
    
    # Reservas de hoy
    hoy = timezone.now().date()
    reservas_hoy = Reserva.objects.filter(
        fecha_hora_inicio__date=hoy
    ).count()
    
    # Próximas reservas (próximas 2 horas)
    proximas_reservas = Reserva.objects.filter(
        fecha_hora_inicio__gt=ahora,
        fecha_hora_inicio__lte=ahora + timezone.timedelta(hours=2)
    ).select_related('sala').order_by('fecha_hora_inicio')
    
    context = {
        'total_salas': total_salas,
        'salas_disponibles': salas_disponibles,
        'salas_ocupadas': salas_ocupadas,
        'reservas_hoy': reservas_hoy,
        'reservas_activas': reservas_activas,
        'proximas_reservas': proximas_reservas,
        'usuario_actual': request.user,
    }
    
    return render(request, 'admin_panel.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff)
def gestion_salas(request):
    """
    Vista para gestionar salas (reemplaza /admin/reservas/sala/)
    """
    salas = Sala.objects.all().order_by('nombre')
    
    if request.method == 'POST':
        pass
    
    context = {
        'salas': salas,
        'usuario_actual': request.user,
    }
    return render(request, 'gestion_salas.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff)
def crear_sala(request):
    """
    Vista para crear nueva sala
    """
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        capacidad = request.POST.get('capacidad_maxima')
        estado = request.POST.get('estado')
        habilitada = request.POST.get('habilitada') == 'on'
        
        try:
            Sala.objects.create(
                nombre=nombre,
                capacidad_maxima=capacidad,
                estado=estado,
                habilitada=habilitada
            )
            messages.success(request, f'Sala "{nombre}" creada exitosamente!')
            return redirect('reservas:gestion_salas')
        except Exception as e:
            messages.error(request, f'Error al crear sala: {str(e)}')
    
    context = {
        'usuario_actual': request.user,
    }
    return render(request, 'crear_sala.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff)
def editar_sala(request, sala_id):
    """
    Vista para editar una sala existente
    """
    sala = get_object_or_404(Sala, id=sala_id)
    
    if request.method == 'POST':
        sala.nombre = request.POST.get('nombre')
        sala.capacidad_maxima = request.POST.get('capacidad_maxima')
        sala.estado = request.POST.get('estado')
        sala.habilitada = request.POST.get('habilitada') == 'on'
        sala.save()
        
        messages.success(request, f'Sala "{sala.nombre}" actualizada exitosamente!')
        return redirect('reservas:gestion_salas')
    
    context = {
        'sala': sala,
        'usuario_actual': request.user,
    }
    return render(request, 'editar_sala.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff)
def eliminar_sala(request, sala_id):
    """
    Vista para eliminar una sala
    """
    sala = get_object_or_404(Sala, id=sala_id)
    nombre_sala = sala.nombre
    
    # Verificar que no tenga reservas activas
    reservas_activas = Reserva.objects.filter(sala=sala).exists()
    if reservas_activas:
        messages.error(request, f'No se puede eliminar la sala "{nombre_sala}" porque tiene reservas asociadas.')
    else:
        sala.delete()
        messages.success(request, f'Sala "{nombre_sala}" eliminada exitosamente!')
    
    return redirect('reservas:gestion_salas')

@login_required
@user_passes_test(es_staff, login_url='/administracion/login/')
def gestion_reservas(request):
    """
    Vista para gestionar reservas (reemplaza /admin/reservas/reserva/)
    """
    # Filtros
    filtro_estado = request.GET.get('estado', 'todas')
    hoy = timezone.now().date()
    
    reservas = Reserva.objects.all().select_related('sala').order_by('-fecha_hora_inicio')
    
    # Aplicar filtros
    if filtro_estado == 'activas':
        reservas = reservas.filter(fecha_hora_termino__gt=timezone.now())
    elif filtro_estado == 'completadas':
        reservas = reservas.filter(fecha_hora_termino__lte=timezone.now())
    elif filtro_estado == 'hoy':
        reservas = reservas.filter(fecha_hora_inicio__date=hoy)
    
    context = {
        'reservas': reservas,
        'filtro_actual': filtro_estado,
        'usuario_actual': request.user,
        'now': timezone.now(),
    }
    return render(request, 'gestion_reservas.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff)
def crear_reserva_manual(request):
    """
    Vista para crear reserva manualmente
    """
    salas = Sala.objects.filter(habilitada=True, estado='disponible')
    
    if request.method == 'POST':
        rut = request.POST.get('rut_reservante')
        sala_id = request.POST.get('sala')
        fecha_inicio = request.POST.get('fecha_hora_inicio')
        fecha_termino = request.POST.get('fecha_hora_termino')
        
        try:
            sala = Sala.objects.get(id=sala_id)
            
            # Convertir strings a datetime
            from datetime import datetime
            fecha_inicio_dt = datetime.fromisoformat(fecha_inicio.replace('Z', '+00:00'))
            fecha_termino_dt = datetime.fromisoformat(fecha_termino.replace('Z', '+00:00'))
            
            # Verificar disponibilidad
            reserva_conflicto = Reserva.objects.filter(
                sala=sala,
                fecha_hora_inicio__lt=fecha_termino_dt,
                fecha_hora_termino__gt=fecha_inicio_dt
            ).exists()
            
            if reserva_conflicto:
                messages.error(request, 'La sala no está disponible en ese horario.')
            else:
                Reserva.objects.create(
                    rut_reservante=rut,
                    sala=sala,
                    fecha_hora_inicio=fecha_inicio_dt,
                    fecha_hora_termino=fecha_termino_dt
                )
                messages.success(request, 'Reserva creada exitosamente!')
                return redirect('reservas:gestion_reservas')
                
        except Exception as e:
            messages.error(request, f'Error al crear reserva: {str(e)}')
    
    context = {
        'salas': salas,
        'usuario_actual': request.user,
    }
    return render(request, 'crear_reserva_manual.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff)
def eliminar_reserva(request, reserva_id):
    """
    Vista para eliminar una reserva
    """
    reserva = get_object_or_404(Reserva, id=reserva_id)
    info_reserva = f"{reserva.sala.nombre} - {reserva.rut_reservante}"
    
    reserva.delete()
    messages.success(request, f'Reserva "{info_reserva}" eliminada exitosamente!')
    
    return redirect('reservas:gestion_reservas')

@login_required
@user_passes_test(es_staff, login_url='/administracion/login/')
def reducir_tiempo_reserva(request, reserva_id, minutos):
    """
    Reducir el tiempo de una reserva activa
    """
    reserva = get_object_or_404(Reserva, id=reserva_id)
    
    # Verificar que la reserva esté activa
    ahora = timezone.now()
    if reserva.fecha_hora_termino <= ahora:
        messages.error(request, 'Esta reserva ya ha finalizado.')
        return redirect('reservas:gestion_reservas')
    
    # Calcular nueva hora de término
    nueva_hora_termino = reserva.fecha_hora_termino - timedelta(minutes=minutos)
    
    # Verificar que no sea menor a la hora actual
    if nueva_hora_termino <= ahora:
        # Si se reduce más del tiempo restante, terminar la reserva inmediatamente
        reserva.fecha_hora_termino = ahora
        mensaje = f'Reserva de {reserva.sala.nombre} finalizada inmediatamente.'
    else:
        reserva.fecha_hora_termino = nueva_hora_termino
        # Recalcular duración
        nueva_duracion = (reserva.fecha_hora_termino - reserva.fecha_hora_inicio).total_seconds() / 60
        reserva.duracion_minutos = int(nueva_duracion)
        mensaje = f'Tiempo reducido en {minutos} minutos. Nueva hora de término: {reserva.fecha_hora_termino.strftime("%H:%M")}'
    
    reserva.save()
    messages.success(request, mensaje)
    
    return redirect('reservas:gestion_reservas')

def finalizar_reserva_ahora(request, reserva_id):
    """
    Finalizar una reserva inmediatamente
    """
    reserva = get_object_or_404(Reserva, id=reserva_id)
    
    # Verificar que la reserva esté activa
    ahora = timezone.now()
    if reserva.fecha_hora_termino <= ahora:
        messages.error(request, 'Esta reserva ya ha finalizado.')
        return redirect('reservas:gestion_reservas')
    
    sala_nombre = reserva.sala.nombre
    reserva.fecha_hora_termino = ahora
    reserva.save()
    
    messages.success(request, f'Reserva de {sala_nombre} finalizada inmediatamente. Sala ahora disponible.')
    
    return redirect('reservas:gestion_reservas')