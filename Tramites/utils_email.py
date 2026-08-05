"""
utils_email.py
Funciones de envío de correo para el sistema de turnos municipales.
"""
from django.core.mail import send_mail
from django.conf import settings


def _enviar(asunto, mensaje, destinatario):
    """Helper interno: envía un correo y silencia errores."""
    if not destinatario:
        return
    try:
        send_mail(
            subject        = asunto,
            message        = mensaje,
            from_email     = None,          # usa DEFAULT_FROM_EMAIL
            recipient_list = [destinatario],
            fail_silently  = True,
        )
    except Exception:
        pass  # En producción loguear con logging.exception(...)


# ══════════════════════════════════════════
# 1. Confirmación de turno
# ══════════════════════════════════════════
def enviar_confirmacion_turno(turno):
    """
    Se envía cuando el ciudadano solicita un turno.
    Destinatario: email del ciudadano.
    """
    ciudadano = turno.ciudadano
    email     = ciudadano.email or (ciudadano.user.email if ciudadano.user else None)
    if not email:
        return

    fecha_cita = turno.fecha_cita
    if fecha_cita and isinstance(fecha_cita, str):
        from datetime import datetime
        try:
            fecha_cita = datetime.fromisoformat(fecha_cita)
        except ValueError:
            fecha_cita = None

    fecha_cita_str = (
        fecha_cita.strftime('%d/%m/%Y a las %H:%M')
        if fecha_cita else 'A confirmar por el municipio'
    )
    tramite = str(turno.tipo_tramite) if turno.tipo_tramite else 'Sin especificar'

    asunto = f'✅ Turno #{turno.numero_turno} confirmado — Municipio Digital'
    mensaje = (
        f'Estimado/a {ciudadano.nombre},\n\n'
        f'Su turno ha sido registrado exitosamente.\n\n'
        f'══════════════════════════════════\n'
        f'     CONFIRMACIÓN DE TURNO\n'
        f'══════════════════════════════════\n'
        f'Número de turno : #{turno.numero_turno}\n'
        f'Trámite         : {tramite}\n'
        f'Fecha de cita   : {fecha_cita_str}\n'
        f'Estado          : Pendiente\n'
        f'══════════════════════════════════\n\n'
        f'Preséntese con su DNI el día indicado.\n'
        f'Si tiene consultas comuníquese con nosotros.\n\n'
        f'Municipio Digital — Atención Ciudadana\n'
        f'atencion@municipio.gob'
    )
    _enviar(asunto, mensaje, email)


# ══════════════════════════════════════════
# 2. Notificación de llamado
# ══════════════════════════════════════════
def enviar_notificacion_llamado(turno):
    """
    Se envía cuando el funcionario llama al ciudadano.
    Destinatario: email del ciudadano.
    """
    ciudadano = turno.ciudadano
    email     = ciudadano.email or (ciudadano.user.email if ciudadano.user else None)
    if not email:
        return

    ventanilla = f'Ventanilla {turno.ventanilla.numero}' if turno.ventanilla else 'la ventanilla asignada'
    tramite    = str(turno.tipo_tramite) if turno.tipo_tramite else 'Sin especificar'

    asunto = f'🔔 ¡Su turno #{turno.numero_turno} está siendo llamado!'
    mensaje = (
        f'Estimado/a {ciudadano.nombre},\n\n'
        f'¡Es su turno! Diríjase inmediatamente a {ventanilla}.\n\n'
        f'══════════════════════════════════\n'
        f'     LLAMADO DE TURNO\n'
        f'══════════════════════════════════\n'
        f'Número de turno : #{turno.numero_turno}\n'
        f'Trámite         : {tramite}\n'
        f'Diríjase a      : {ventanilla}\n'
        f'══════════════════════════════════\n\n'
        f'Si no se presenta en los próximos minutos,\n'
        f'su turno podrá ser reasignado.\n\n'
        f'Municipio Digital — Atención Ciudadana'
    )
    _enviar(asunto, mensaje, email)


# ══════════════════════════════════════════
# 3. Turno resuelto
# ══════════════════════════════════════════
def enviar_turno_resuelto(turno):
    """
    Se envía cuando el trámite queda resuelto.
    Destinatario: email del ciudadano.
    """
    ciudadano = turno.ciudadano
    email     = ciudadano.email or (ciudadano.user.email if ciudadano.user else None)
    if not email:
        return

    tramite    = str(turno.tipo_tramite) if turno.tipo_tramite else 'Sin especificar'
    funcionario = turno.funcionario.nombre if turno.funcionario else 'el equipo municipal'
    tiempo_aten = turno.tiempo_atencion_minutos()
    tiempo_esp  = turno.tiempo_espera_minutos()

    asunto = f'✅ Trámite resuelto — Turno #{turno.numero_turno}'
    mensaje = (
        f'Estimado/a {ciudadano.nombre},\n\n'
        f'Su trámite ha sido resuelto satisfactoriamente.\n\n'
        f'══════════════════════════════════\n'
        f'     COMPROBANTE DE ATENCIÓN\n'
        f'══════════════════════════════════\n'
        f'Número de turno  : #{turno.numero_turno}\n'
        f'Trámite          : {tramite}\n'
        f'Atendido por     : {funcionario}\n'
    )
    if tiempo_esp is not None:
        mensaje += f'Tiempo de espera : {tiempo_esp} min\n'
    if tiempo_aten is not None:
        mensaje += f'Tiempo atención  : {tiempo_aten} min\n'
    mensaje += (
        f'══════════════════════════════════\n\n'
        f'Gracias por utilizar los servicios del Municipio Digital.\n'
        f'Este correo es su comprobante de atención.\n\n'
        f'Municipio Digital — Atención Ciudadana\n'
        f'atencion@municipio.gob'
    )
    _enviar(asunto, mensaje, email)
