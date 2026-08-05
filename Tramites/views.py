from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render

from .models import (
    Departamento, Ventanilla, Funcionario,
    TipoTramite, Ciudadano, Turno, Expediente
)
from .utils_email import (
    enviar_confirmacion_turno,
    enviar_notificacion_llamado,
    enviar_turno_resuelto,
)


# ─────────────────────────────────────────
# INICIO
# ─────────────────────────────────────────
def inicio(request):
    return render(request, 'plantillaPrincipal.html')


# ─────────────────────────────────────────
# AUTENTICACIÓN
# ─────────────────────────────────────────
def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff or request.user.is_superuser:
            return redirect('/turnos/')
        return redirect('/mis-turnos/')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_staff or user.is_superuser:
                return redirect('/turnos/')
            return redirect('/mis-turnos/')
        messages.error(request, 'Usuario o contraseña incorrectos.')
    return render(request, 'auth/login.html')


def registro_view(request):
    if request.user.is_authenticated:
        return redirect('/')
    if request.method == 'POST':
        username  = request.POST.get('username', '').strip()
        password  = request.POST.get('password', '').strip()
        password2 = request.POST.get('password2', '').strip()
        email     = request.POST.get('email', '').strip()
        nombre    = request.POST.get('nombre', '').strip()
        dni       = request.POST.get('dni', '').strip()
        telefono  = request.POST.get('telefono', '').strip()

        if password != password2:
            messages.error(request, 'Las contraseñas no coinciden.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Ese nombre de usuario ya existe.')
        elif Ciudadano.objects.filter(dni=dni).exists():
            messages.error(request, 'Ya existe un ciudadano registrado con ese DNI.')
        else:
            user = User.objects.create_user(username=username, password=password, email=email)
            Ciudadano.objects.create(
                user=user,
                nombre=nombre or username,
                dni=dni,
                email=email,
                telefono=telefono,
            )
            messages.success(request, 'Cuenta creada. Podés iniciar sesión.')
            return redirect('/login/')
    return render(request, 'auth/registro.html')


@login_required(login_url='/login/')
def logout_view(request):
    logout(request)
    return redirect('/login/')


# ══════════════════════════════════════════
# DEPARTAMENTOS
# ══════════════════════════════════════════
@login_required(login_url='/login/')
def listado_departamentos(request):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('/')
    items = Departamento.objects.all()
    return render(request, 'departamentos/listado.html', {'items': items})


@login_required(login_url='/login/')
def nuevo_departamento(request):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('/')
    return render(request, 'departamentos/formulario.html', {'accion': 'Nuevo'})


@login_required(login_url='/login/')
def guardar_departamento(request):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('/')
    Departamento.objects.create(nombre=request.POST['nombre'])
    messages.success(request, 'Departamento guardado correctamente.')
    return redirect('/departamentos/')


@login_required(login_url='/login/')
def editar_departamento(request, id):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('/')
    item = get_object_or_404(Departamento, id=id)
    return render(request, 'departamentos/formulario.html', {'accion': 'Editar', 'item': item})


@login_required(login_url='/login/')
def actualizar_departamento(request, id):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('/')
    item = get_object_or_404(Departamento, id=id)
    item.nombre = request.POST['nombre']
    item.save()
    messages.success(request, 'Departamento actualizado correctamente.')
    return redirect('/departamentos/')


@login_required(login_url='/login/')
def eliminar_departamento(request, id):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('/')
    get_object_or_404(Departamento, id=id).delete()
    messages.success(request, 'Departamento eliminado correctamente.')
    return redirect('/departamentos/')


# ══════════════════════════════════════════
# VENTANILLAS
# ══════════════════════════════════════════
@login_required(login_url='/login/')
def listado_ventanillas(request):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('/')
    items = Ventanilla.objects.select_related('departamento').all()
    return render(request, 'ventanillas/listado.html', {'items': items})


@login_required(login_url='/login/')
def nueva_ventanilla(request):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('/')
    departamentos = Departamento.objects.all()
    return render(request, 'ventanillas/formulario.html',
                  {'accion': 'Nueva', 'departamentos': departamentos})


@login_required(login_url='/login/')
def guardar_ventanilla(request):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('/')
    dep_id = request.POST.get('departamento') or None
    Ventanilla.objects.create(
        numero=request.POST['numero'],
        descripcion=request.POST.get('descripcion', ''),
        departamento_id=dep_id,
        activa='activa' in request.POST,
    )
    messages.success(request, 'Ventanilla guardada correctamente.')
    return redirect('/ventanillas/')


@login_required(login_url='/login/')
def editar_ventanilla(request, id):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('/')
    item = get_object_or_404(Ventanilla, id=id)
    departamentos = Departamento.objects.all()
    return render(request, 'ventanillas/formulario.html',
                  {'accion': 'Editar', 'item': item, 'departamentos': departamentos})


@login_required(login_url='/login/')
def actualizar_ventanilla(request, id):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('/')
    item = get_object_or_404(Ventanilla, id=id)
    dep_id = request.POST.get('departamento') or None
    item.numero = request.POST['numero']
    item.descripcion = request.POST.get('descripcion', '')
    item.departamento_id = dep_id
    item.activa = 'activa' in request.POST
    item.save()
    messages.success(request, 'Ventanilla actualizada correctamente.')
    return redirect('/ventanillas/')


@login_required(login_url='/login/')
def eliminar_ventanilla(request, id):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('/')
    get_object_or_404(Ventanilla, id=id).delete()
    messages.success(request, 'Ventanilla eliminada correctamente.')
    return redirect('/ventanillas/')


# ══════════════════════════════════════════
# FUNCIONARIOS
# ══════════════════════════════════════════
@login_required(login_url='/login/')
def listado_funcionarios(request):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('/')
    items = Funcionario.objects.select_related('ventanilla').all()
    return render(request, 'funcionarios/listado.html', {'items': items})


@login_required(login_url='/login/')
def nuevo_funcionario(request):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('/')
    ventanillas = Ventanilla.objects.filter(activa=True)
    return render(request, 'funcionarios/formulario.html',
                  {'accion': 'Nuevo', 'ventanillas': ventanillas})


@login_required(login_url='/login/')
def guardar_funcionario(request):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('/')
    vent_id = request.POST.get('ventanilla') or None
    Funcionario.objects.create(
        nombre=request.POST['nombre'],
        legajo=request.POST['legajo'],
        email=request.POST.get('email', ''),
        ventanilla_id=vent_id,
        activo='activo' in request.POST,
    )
    messages.success(request, 'Funcionario guardado correctamente.')
    return redirect('/funcionarios/')


@login_required(login_url='/login/')
def editar_funcionario(request, id):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('/')
    item = get_object_or_404(Funcionario, id=id)
    ventanillas = Ventanilla.objects.filter(activa=True)
    return render(request, 'funcionarios/formulario.html',
                  {'accion': 'Editar', 'item': item, 'ventanillas': ventanillas})


@login_required(login_url='/login/')
def actualizar_funcionario(request, id):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('/')
    item = get_object_or_404(Funcionario, id=id)
    vent_id = request.POST.get('ventanilla') or None
    item.nombre = request.POST['nombre']
    item.legajo = request.POST['legajo']
    item.email  = request.POST.get('email', '')
    item.ventanilla_id = vent_id
    item.activo = 'activo' in request.POST
    item.save()
    messages.success(request, 'Funcionario actualizado correctamente.')
    return redirect('/funcionarios/')


@login_required(login_url='/login/')
def eliminar_funcionario(request, id):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('/')
    get_object_or_404(Funcionario, id=id).delete()
    messages.success(request, 'Funcionario eliminado correctamente.')
    return redirect('/funcionarios/')


# ══════════════════════════════════════════
# TIPOS DE TRÁMITE
# ══════════════════════════════════════════
@login_required(login_url='/login/')
def listado_tipos_tramite(request):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('/')
    items = TipoTramite.objects.select_related('departamento').all()
    return render(request, 'tipos_tramite/listado.html', {'items': items})


@login_required(login_url='/login/')
def nuevo_tipo_tramite(request):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('/')
    departamentos = Departamento.objects.all()
    return render(request, 'tipos_tramite/formulario.html',
                  {'accion': 'Nuevo', 'departamentos': departamentos})


@login_required(login_url='/login/')
def guardar_tipo_tramite(request):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('/')
    dep_id = request.POST.get('departamento') or None
    TipoTramite.objects.create(
        nombre=request.POST['nombre'],
        descripcion=request.POST.get('descripcion', ''),
        departamento_id=dep_id,
        duracion_estimada_min=request.POST.get('duracion_estimada_min', 15),
        activo='activo' in request.POST,
    )
    messages.success(request, 'Tipo de trámite guardado correctamente.')
    return redirect('/tipos-tramite/')


@login_required(login_url='/login/')
def editar_tipo_tramite(request, id):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('/')
    item = get_object_or_404(TipoTramite, id=id)
    departamentos = Departamento.objects.all()
    return render(request, 'tipos_tramite/formulario.html',
                  {'accion': 'Editar', 'item': item, 'departamentos': departamentos})


@login_required(login_url='/login/')
def actualizar_tipo_tramite(request, id):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('/')
    item = get_object_or_404(TipoTramite, id=id)
    dep_id = request.POST.get('departamento') or None
    item.nombre = request.POST['nombre']
    item.descripcion = request.POST.get('descripcion', '')
    item.departamento_id = dep_id
    item.duracion_estimada_min = request.POST.get('duracion_estimada_min', 15)
    item.activo = 'activo' in request.POST
    item.save()
    messages.success(request, 'Tipo de trámite actualizado correctamente.')
    return redirect('/tipos-tramite/')


@login_required(login_url='/login/')
def eliminar_tipo_tramite(request, id):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('/')
    get_object_or_404(TipoTramite, id=id).delete()
    messages.success(request, 'Tipo de trámite eliminado correctamente.')
    return redirect('/tipos-tramite/')


# ══════════════════════════════════════════
# CIUDADANOS
# ══════════════════════════════════════════
@login_required(login_url='/login/')
def listado_ciudadanos(request):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('/')
    items = Ciudadano.objects.all()
    return render(request, 'ciudadanos/listado.html', {'items': items})


@login_required(login_url='/login/')
def nuevo_ciudadano(request):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('/')
    return render(request, 'ciudadanos/formulario.html', {'accion': 'Nuevo'})


@login_required(login_url='/login/')
def guardar_ciudadano(request):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('/')
    Ciudadano.objects.create(
        nombre=request.POST['nombre'],
        dni=request.POST['dni'],
        email=request.POST.get('email', ''),
        telefono=request.POST.get('telefono', ''),
    )
    messages.success(request, 'Ciudadano guardado correctamente.')
    return redirect('/ciudadanos/')


@login_required(login_url='/login/')
def editar_ciudadano(request, id):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('/')
    item = get_object_or_404(Ciudadano, id=id)
    return render(request, 'ciudadanos/formulario.html', {'accion': 'Editar', 'item': item})


@login_required(login_url='/login/')
def actualizar_ciudadano(request, id):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('/')
    item = get_object_or_404(Ciudadano, id=id)
    item.nombre   = request.POST['nombre']
    item.dni      = request.POST['dni']
    item.email    = request.POST.get('email', '')
    item.telefono = request.POST.get('telefono', '')
    item.save()
    messages.success(request, 'Ciudadano actualizado correctamente.')
    return redirect('/ciudadanos/')


@login_required(login_url='/login/')
def eliminar_ciudadano(request, id):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('/')
    get_object_or_404(Ciudadano, id=id).delete()
    messages.success(request, 'Ciudadano eliminado correctamente.')
    return redirect('/ciudadanos/')


# ══════════════════════════════════════════
# TURNOS
# ══════════════════════════════════════════
@login_required(login_url='/login/')
def listado_turnos(request):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('/')
    items = Turno.objects.select_related(
        'ciudadano', 'tipo_tramite', 'ventanilla', 'funcionario'
    ).all()
    return render(request, 'turnos/listado.html', {'items': items})


@login_required(login_url='/login/')
def nuevo_turno(request):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('/')
    ctx = {
        'accion':       'Nuevo',
        'ciudadanos':   Ciudadano.objects.all(),
        'tipos':        TipoTramite.objects.filter(activo=True),
        'ventanillas':  Ventanilla.objects.filter(activa=True),
        'funcionarios': Funcionario.objects.filter(activo=True),
    }
    return render(request, 'turnos/formulario.html', ctx)


@login_required(login_url='/login/')
def guardar_turno(request):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('/')
    Turno.objects.create(
        numero_turno   = request.POST['numero_turno'],
        ciudadano_id   = request.POST['ciudadano'],
        tipo_tramite_id= request.POST.get('tipo_tramite') or None,
        ventanilla_id  = request.POST.get('ventanilla') or None,
        funcionario_id = request.POST.get('funcionario') or None,
        estado         = request.POST.get('estado', 'pendiente'),
        fecha_cita     = request.POST.get('fecha_cita') or None,
        observaciones  = request.POST.get('observaciones', ''),
    )
    messages.success(request, 'Turno guardado correctamente.')
    return redirect('/turnos/')


@login_required(login_url='/login/')
def editar_turno(request, id):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('/')
    item = get_object_or_404(Turno, id=id)
    ctx = {
        'accion':       'Editar',
        'item':         item,
        'ciudadanos':   Ciudadano.objects.all(),
        'tipos':        TipoTramite.objects.filter(activo=True),
        'ventanillas':  Ventanilla.objects.filter(activa=True),
        'funcionarios': Funcionario.objects.filter(activo=True),
    }
    return render(request, 'turnos/formulario.html', ctx)


@login_required(login_url='/login/')
def actualizar_turno(request, id):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('/')
    item = get_object_or_404(Turno, id=id)
    estado_anterior = item.estado
    item.numero_turno    = request.POST['numero_turno']
    item.ciudadano_id    = request.POST['ciudadano']
    item.tipo_tramite_id = request.POST.get('tipo_tramite') or None
    item.ventanilla_id   = request.POST.get('ventanilla') or None
    item.funcionario_id  = request.POST.get('funcionario') or None
    item.estado          = request.POST.get('estado', 'pendiente')
    item.fecha_cita      = request.POST.get('fecha_cita') or None
    item.observaciones   = request.POST.get('observaciones', '')
    item.save()

    # Enviar correo si el turno pasó a resuelto
    if estado_anterior != 'resuelto' and item.estado == 'resuelto':
        from django.utils import timezone
        item.fecha_resolucion = timezone.now()
        item.save(update_fields=['fecha_resolucion'])
        enviar_turno_resuelto(item)

    messages.success(request, 'Turno actualizado correctamente.')
    return redirect('/turnos/')


@login_required(login_url='/login/')
def eliminar_turno(request, id):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('/')
    get_object_or_404(Turno, id=id).delete()
    messages.success(request, 'Turno eliminado correctamente.')
    return redirect('/turnos/')


# ══════════════════════════════════════════
# EXPEDIENTES
# ══════════════════════════════════════════
@login_required(login_url='/login/')
def listado_expedientes(request):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('/')
    items = Expediente.objects.select_related('turno', 'ventanilla_actual').all()
    return render(request, 'expedientes/listado.html', {'items': items})


@login_required(login_url='/login/')
def nuevo_expediente(request):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('/')
    ctx = {
        'accion':     'Nuevo',
        'turnos':     Turno.objects.filter(expediente__isnull=True),
        'ventanillas': Ventanilla.objects.filter(activa=True),
    }
    return render(request, 'expedientes/formulario.html', ctx)


@login_required(login_url='/login/')
def guardar_expediente(request):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('/')
    Expediente.objects.create(
        turno_id          = request.POST['turno'],
        numero            = request.POST['numero'],
        ventanilla_actual_id = request.POST.get('ventanilla_actual') or None,
        estado            = request.POST.get('estado', 'iniciado'),
        notas             = request.POST.get('notas', ''),
    )
    messages.success(request, 'Expediente guardado correctamente.')
    return redirect('/expedientes/')


@login_required(login_url='/login/')
def editar_expediente(request, id):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('/')
    item = get_object_or_404(Expediente, id=id)
    ctx = {
        'accion':      'Editar',
        'item':        item,
        'turnos':      Turno.objects.all(),
        'ventanillas': Ventanilla.objects.filter(activa=True),
    }
    return render(request, 'expedientes/formulario.html', ctx)


@login_required(login_url='/login/')
def actualizar_expediente(request, id):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('/')
    item = get_object_or_404(Expediente, id=id)
    item.turno_id             = request.POST['turno']
    item.numero               = request.POST['numero']
    item.ventanilla_actual_id = request.POST.get('ventanilla_actual') or None
    item.estado               = request.POST.get('estado', 'iniciado')
    item.notas                = request.POST.get('notas', '')
    item.save()
    messages.success(request, 'Expediente actualizado correctamente.')
    return redirect('/expedientes/')


@login_required(login_url='/login/')
def eliminar_expediente(request, id):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('/')
    get_object_or_404(Expediente, id=id).delete()
    messages.success(request, 'Expediente eliminado correctamente.')
    return redirect('/expedientes/')


# ══════════════════════════════════════════
# PORTAL CIUDADANO
# ══════════════════════════════════════════

@login_required(login_url='/login/')
def solicitar_turno(request):
    """El ciudadano elige tipo de trámite y fecha/hora para su turno."""
    # Redirigir admin al panel de gestión
    if request.user.is_staff or request.user.is_superuser:
        return redirect('/turnos/')

    try:
        ciudadano = request.user.ciudadano
    except Ciudadano.DoesNotExist:
        messages.error(request, 'Tu cuenta no tiene un perfil de ciudadano. Contactá al municipio.')
        return redirect('/')

    tipos = TipoTramite.objects.filter(activo=True)

    if request.method == 'POST':
        tipo_id   = request.POST.get('tipo_tramite')
        fecha_cita = request.POST.get('fecha_cita') or None

        # Generar número de turno automáticamente
        ultimo = Turno.objects.order_by('-numero_turno').first()
        numero = (ultimo.numero_turno + 1) if ultimo else 1

        turno = Turno.objects.create(
            numero_turno   = numero,
            ciudadano      = ciudadano,
            tipo_tramite_id= tipo_id or None,
            estado         = 'pendiente',
            fecha_cita     = fecha_cita,
        )
        # Enviar correo de confirmación al ciudadano
        enviar_confirmacion_turno(turno)
        messages.success(request, f'Tu turno fue creado con el número #{turno.numero_turno}. Te enviamos una confirmación por correo.')
        return redirect('/mis-turnos/')

    return render(request, 'ciudadano/solicitar_turno.html', {'tipos': tipos})


@login_required(login_url='/login/')
def mis_turnos(request):
    """Muestra todos los turnos del ciudadano logueado."""
    if request.user.is_staff or request.user.is_superuser:
        return redirect('/turnos/')

    try:
        ciudadano = request.user.ciudadano
        turnos = Turno.objects.filter(ciudadano=ciudadano).select_related(
            'tipo_tramite', 'ventanilla', 'funcionario'
        ).order_by('-fecha_solicitud')
    except Ciudadano.DoesNotExist:
        turnos = []
        ciudadano = None

    return render(request, 'ciudadano/mis_turnos.html', {
        'turnos': turnos,
        'ciudadano': ciudadano,
    })


# ══════════════════════════════════════════
# FULLCALENDAR — endpoint JSON de turnos
# ══════════════════════════════════════════
import json
from django.http import JsonResponse
from django.utils import timezone

@login_required(login_url='/login/')
def turnos_json(request):
    """Devuelve los turnos con fecha_cita como eventos JSON para FullCalendar."""
    turnos = Turno.objects.filter(fecha_cita__isnull=False).select_related(
        'ciudadano', 'tipo_tramite'
    )
    eventos = []
    for t in turnos:
        color = {
            'pendiente':   '#f0a500',
            'en_atencion': '#0077b6',
            'derivado':    '#17a2b8',
            'resuelto':    '#28a745',
            'ausente':     '#6c757d',
        }.get(t.estado, '#aaa')

        eventos.append({
            'id':    t.id,
            'title': f'#{t.numero_turno} — {t.ciudadano.nombre}',
            'start': t.fecha_cita.isoformat(),
            'color': color,
            'extendedProps': {
                'tramite': str(t.tipo_tramite) if t.tipo_tramite else '—',
                'estado':  t.get_estado_display(),
            }
        })
    return JsonResponse(eventos, safe=False)


# ══════════════════════════════════════════
# PANEL DEL FUNCIONARIO — Hotkeys-js
# ══════════════════════════════════════════
@login_required(login_url='/login/')
def panel_funcionario(request):
    """Panel del funcionario: cola de turnos pendientes + llamar al siguiente."""
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('/')

    # Intentar obtener la ventanilla del funcionario logueado
    try:
        funcionario = Funcionario.objects.filter(
            email=request.user.email, activo=True
        ).first()
        ventanilla = funcionario.ventanilla if funcionario else None
    except Exception:
        funcionario = None
        ventanilla  = None

    # Cola: turnos pendientes ordenados por fecha de solicitud
    cola = Turno.objects.filter(
        estado='pendiente'
    ).select_related('ciudadano', 'tipo_tramite').order_by('fecha_solicitud')

    # Turno actualmente en atención en esta ventanilla
    en_atencion = None
    if ventanilla:
        en_atencion = Turno.objects.filter(
            ventanilla=ventanilla, estado='en_atencion'
        ).select_related('ciudadano', 'tipo_tramite').first()

    return render(request, 'funcionario/panel.html', {
        'cola':         cola,
        'en_atencion':  en_atencion,
        'funcionario':  funcionario,
        'ventanilla':   ventanilla,
    })


@login_required(login_url='/login/')
def llamar_siguiente(request):
    """Llama al siguiente turno pendiente (llamado por Hotkeys-js via POST)."""
    if not (request.user.is_staff or request.user.is_superuser):
        return JsonResponse({'error': 'Sin permisos'}, status=403)

    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    # Marcar el turno en_atencion actual como resuelto si existe
    ventanilla_id = request.POST.get('ventanilla_id')
    if ventanilla_id:
        Turno.objects.filter(
            ventanilla_id=ventanilla_id, estado='en_atencion'
        ).update(estado='resuelto', fecha_resolucion=timezone.now())

    # Tomar el siguiente pendiente
    siguiente = Turno.objects.filter(
        estado='pendiente'
    ).order_by('fecha_solicitud').first()

    if siguiente:
        siguiente.estado        = 'en_atencion'
        siguiente.fecha_llamado = timezone.now()
        if ventanilla_id:
            siguiente.ventanilla_id = ventanilla_id
        siguiente.save()

        # Enviar notificación de llamado al ciudadano
        enviar_notificacion_llamado(siguiente)

        return JsonResponse({
            'ok':           True,
            'numero_turno': siguiente.numero_turno,
            'ciudadano':    siguiente.ciudadano.nombre,
            'tramite':      str(siguiente.tipo_tramite) if siguiente.tipo_tramite else '—',
            'turno_id':     siguiente.id,
        })

    return JsonResponse({'ok': False, 'mensaje': 'No hay más turnos pendientes.'})


# ══════════════════════════════════════════
# PANEL DRAG & DROP — Derivación de expedientes
# ══════════════════════════════════════════
@login_required(login_url='/login/')
def panel_ventanillas(request):
    """Panel visual de ventanillas con expedientes arrastrables."""
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('/')

    ventanillas = Ventanilla.objects.filter(activa=True).prefetch_related(
        'expedientes__turno__ciudadano',
        'expedientes__turno__tipo_tramite',
    )
    # Expedientes sin ventanilla asignada
    sin_asignar = Expediente.objects.filter(
        ventanilla_actual__isnull=True
    ).select_related('turno__ciudadano', 'turno__tipo_tramite')

    return render(request, 'funcionario/panel_ventanillas.html', {
        'ventanillas': ventanillas,
        'sin_asignar': sin_asignar,
    })


@login_required(login_url='/login/')
def derivar_expediente(request):
    """Recibe el drop y cambia la ventanilla_actual del expediente."""
    if not (request.user.is_staff or request.user.is_superuser):
        return JsonResponse({'error': 'Sin permisos'}, status=403)

    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    data           = json.loads(request.body)
    expediente_id  = data.get('expediente_id')
    ventanilla_id  = data.get('ventanilla_id')   # None = sin asignar

    try:
        exp = Expediente.objects.get(id=expediente_id)
        exp.ventanilla_actual_id = ventanilla_id
        exp.estado = 'derivado' if ventanilla_id else 'en_proceso'
        exp.save()
        return JsonResponse({'ok': True})
    except Expediente.DoesNotExist:
        return JsonResponse({'error': 'Expediente no encontrado'}, status=404)


# ══════════════════════════════════════════
# DASHBOARD — Chart.js
# ══════════════════════════════════════════
from django.db.models import Avg, Count, F, ExpressionWrapper, DurationField

@login_required(login_url='/login/')
def dashboard(request):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('/')

    # ── Tiempo promedio de espera (solicitud → llamado) ──
    espera = Turno.objects.filter(
        fecha_llamado__isnull=False, fecha_solicitud__isnull=False
    ).annotate(
        espera=ExpressionWrapper(
            F('fecha_llamado') - F('fecha_solicitud'),
            output_field=DurationField()
        )
    ).aggregate(promedio=Avg('espera'))

    espera_min = round(
        espera['promedio'].total_seconds() / 60, 1
    ) if espera['promedio'] else 0

    # ── Tiempo promedio de atención (llamado → resolución) ──
    atencion = Turno.objects.filter(
        fecha_llamado__isnull=False, fecha_resolucion__isnull=False
    ).annotate(
        atencion=ExpressionWrapper(
            F('fecha_resolucion') - F('fecha_llamado'),
            output_field=DurationField()
        )
    ).aggregate(promedio=Avg('atencion'))

    atencion_min = round(
        atencion['promedio'].total_seconds() / 60, 1
    ) if atencion['promedio'] else 0

    # ── Volumen de trámites resueltos por departamento ──
    por_departamento = (
        Turno.objects
        .filter(estado='resuelto', tipo_tramite__departamento__isnull=False)
        .values('tipo_tramite__departamento__nombre')
        .annotate(total=Count('id'))
        .order_by('-total')
    )
    dep_labels = [r['tipo_tramite__departamento__nombre'] for r in por_departamento]
    dep_data   = [r['total'] for r in por_departamento]

    # ── Volumen de trámites por estado ──
    por_estado = (
        Turno.objects.values('estado')
        .annotate(total=Count('id'))
        .order_by('estado')
    )
    estado_labels = [r['estado'] for r in por_estado]
    estado_data   = [r['total'] for r in por_estado]

    # ── Totales rápidos ──
    total_turnos    = Turno.objects.count()
    total_resueltos = Turno.objects.filter(estado='resuelto').count()
    total_pendientes= Turno.objects.filter(estado='pendiente').count()
    total_atencion  = Turno.objects.filter(estado='en_atencion').count()

    return render(request, 'funcionario/dashboard.html', {
        'espera_min':     espera_min,
        'atencion_min':   atencion_min,
        'dep_labels':     json.dumps(dep_labels),
        'dep_data':       json.dumps(dep_data),
        'estado_labels':  json.dumps(estado_labels),
        'estado_data':    json.dumps(estado_data),
        'total_turnos':   total_turnos,
        'total_resueltos':total_resueltos,
        'total_pendientes':total_pendientes,
        'total_atencion': total_atencion,
    })


# ══════════════════════════════════════════
# SOLICITAR LICENCIA — con tour Driver.js
# ══════════════════════════════════════════
@login_required(login_url='/login/')
def solicitar_licencia(request):
    """Formulario de solicitud de licencia con tour interactivo Driver.js."""
    if request.user.is_staff or request.user.is_superuser:
        return redirect('/turnos/')

    tipos_licencia = TipoTramite.objects.filter(
        activo=True, nombre__icontains='licencia'
    )
    if request.method == 'POST':
        # Crear el turno como licencia
        try:
            ciudadano = request.user.ciudadano
        except Ciudadano.DoesNotExist:
            messages.error(request, 'Perfil de ciudadano no encontrado.')
            return redirect('/')

        tipo_id   = request.POST.get('tipo_tramite') or None
        fecha_cita = request.POST.get('fecha_cita') or None
        obs       = request.POST.get('observaciones', '')

        ultimo = Turno.objects.order_by('-numero_turno').first()
        numero = (ultimo.numero_turno + 1) if ultimo else 1

        turno = Turno.objects.create(
            numero_turno    = numero,
            ciudadano       = ciudadano,
            tipo_tramite_id = tipo_id,
            estado          = 'pendiente',
            fecha_cita      = fecha_cita,
            observaciones   = obs,
        )
        messages.success(request, f'Solicitud de licencia enviada. Tu turno es #{turno.numero_turno}.')
        return redirect('/mis-turnos/')

    return render(request, 'ciudadano/solicitar_licencia.html', {
        'tipos_licencia': tipos_licencia,
    })


# ══════════════════════════════════════════
# PANEL PÚBLICO — ciudadano solo lectura
# ══════════════════════════════════════════
@login_required(login_url='/login/')
def panel_publico(request):
    """Vista de sala de espera para el ciudadano — solo lectura."""
    # Turno en atención en cada ventanilla activa
    ventanillas = Ventanilla.objects.filter(activa=True).prefetch_related(
        'turnos'
    )
    en_atencion = Turno.objects.filter(
        estado='en_atencion'
    ).select_related('ciudadano', 'tipo_tramite', 'ventanilla').order_by('ventanilla__numero')

    # Cola de espera general
    cola = Turno.objects.filter(
        estado='pendiente'
    ).select_related('ciudadano', 'tipo_tramite').order_by('fecha_solicitud')

    # Turno del ciudadano logueado (si existe)
    mi_turno = None
    try:
        ciudadano = request.user.ciudadano
        mi_turno = Turno.objects.filter(
            ciudadano=ciudadano,
            estado__in=['pendiente', 'en_atencion']
        ).select_related('tipo_tramite', 'ventanilla').order_by('fecha_solicitud').first()
    except Exception:
        pass

    return render(request, 'ciudadano/panel_publico.html', {
        'en_atencion': en_atencion,
        'cola':        cola,
        'mi_turno':    mi_turno,
    })
