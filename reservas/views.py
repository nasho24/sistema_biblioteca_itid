from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib import messages
from .models import Sala, Reserva
from .forms import ReservaForm
from datetime import timedelta
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test

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
    Vista para realizar una reserva
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
            reserva.save()
            
            messages.success(request, f'¡Reserva realizada con éxito para la sala {sala.nombre}!')
            return redirect('reservas:index')
    else:
        form = ReservaForm()
    
    context = {
        'sala': sala,
        'form': form
    }
    return render(request, 'reservar_sala.html', context)   

def admin_panel(request):
    """
    Panel de administración personalizado para bibliotecarios
    """
    # Quitar la verificación de staff si quieres acceso libre
    # if not request.user.is_staff:
    #     messages.error(request, 'Acceso restringido al personal autorizado.')
    #     return redirect('reservas:index')
    
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
    # Si ya está autenticado, redirigir al panel
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('reservas:admin_panel')  # ← Usar nombre de URL
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.is_staff:
            login(request, user)
            messages.success(request, f'¡Bienvenido/a, {user.username}!')
            return redirect('reservas:admin_panel')  # ← Redirigir a NUESTRO panel
        else:
            messages.error(request, 'Usuario o contraseña incorrectos. Acceso restringido al personal autorizado.')
    
    return render(request, 'admin_login.html')

def admin_logout(request):
    """
    Cerrar sesión del panel de administración
    """
    logout(request)
    messages.success(request, 'Sesión cerrada correctamente.')
    return redirect('reservas:admin_login')  # ← Redirigir a NUESTRO login

@login_required
@user_passes_test(lambda u: u.is_staff)
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
        # Aquí puedes agregar funcionalidad para crear/editar salas
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
@user_passes_test(lambda u: u.is_staff)
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