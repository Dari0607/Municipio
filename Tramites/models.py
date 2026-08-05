import os
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver


class Departamento(models.Model):
    id     = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)

    class Meta:
        verbose_name        = 'Departamento'
        verbose_name_plural = 'Departamentos'
        ordering            = ['nombre']

    def __str__(self):
        return self.nombre


class Ventanilla(models.Model):
    id           = models.AutoField(primary_key=True)
    numero       = models.PositiveIntegerField(unique=True)
    descripcion  = models.CharField(max_length=200, blank=True)
    departamento = models.ForeignKey(
        Departamento,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='ventanillas'
    )
    activa = models.BooleanField(default=True)

    class Meta:
        verbose_name        = 'Ventanilla'
        verbose_name_plural = 'Ventanillas'
        ordering            = ['numero']

    def __str__(self):
        return f"Ventanilla {self.numero} — {self.departamento}"


class Funcionario(models.Model):
    id         = models.AutoField(primary_key=True)
    nombre     = models.CharField(max_length=200)
    legajo     = models.CharField(max_length=50, unique=True)
    email      = models.EmailField(blank=True)
    ventanilla = models.ForeignKey(
        Ventanilla,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='funcionarios'
    )
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name        = 'Funcionario'
        verbose_name_plural = 'Funcionarios'
        ordering            = ['nombre']

    def __str__(self):
        return f"{self.nombre} (Legajo: {self.legajo})"


class TipoTramite(models.Model):
    """Catálogo de tipos de trámite: licencia, certificado, habilitación, etc."""
    id           = models.AutoField(primary_key=True)
    nombre       = models.CharField(max_length=200)
    descripcion  = models.TextField(blank=True)
    departamento = models.ForeignKey(
        Departamento,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='tipos_tramite'
    )
    duracion_estimada_min = models.PositiveIntegerField(
        default=15,
        help_text='Duración estimada de atención en minutos'
    )
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name        = 'Tipo de Trámite'
        verbose_name_plural = 'Tipos de Trámite'
        ordering            = ['nombre']

    def __str__(self):
        return self.nombre


class Ciudadano(models.Model):
    id       = models.AutoField(primary_key=True)
    user     = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='ciudadano',
        verbose_name='Usuario'
    )
    nombre   = models.CharField(max_length=200)
    dni      = models.CharField(max_length=20, unique=True)
    email    = models.EmailField(blank=True)
    telefono = models.CharField(max_length=20, blank=True)

    class Meta:
        verbose_name        = 'Ciudadano'
        verbose_name_plural = 'Ciudadanos'
        ordering            = ['nombre']

    def __str__(self):
        return f"{self.nombre} (DNI: {self.dni})"


class Turno(models.Model):
    ESTADO_CHOICES = [
        ('pendiente',   'Pendiente'),
        ('en_atencion', 'En Atención'),
        ('derivado',    'Derivado'),
        ('resuelto',    'Resuelto'),
        ('ausente',     'Ausente'),
    ]

    id              = models.AutoField(primary_key=True)
    numero_turno    = models.PositiveIntegerField()
    ciudadano       = models.ForeignKey(
        Ciudadano,
        on_delete=models.CASCADE,
        related_name='turnos'
    )
    tipo_tramite    = models.ForeignKey(
        TipoTramite,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='turnos'
    )
    ventanilla      = models.ForeignKey(
        Ventanilla,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='turnos'
    )
    funcionario     = models.ForeignKey(
        Funcionario,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='turnos'
    )
    estado          = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='pendiente'
    )
    # Tiempos para el dashboard
    fecha_solicitud = models.DateTimeField(auto_now_add=True)   # cuando sacó el turno
    fecha_llamado   = models.DateTimeField(null=True, blank=True)  # cuando el funcionario lo llamó
    fecha_resolucion = models.DateTimeField(null=True, blank=True) # cuando se marcó resuelto
    # Fecha/hora preferida para cita previa (FullCalendar)
    fecha_cita      = models.DateTimeField(null=True, blank=True)
    observaciones   = models.TextField(blank=True)

    class Meta:
        verbose_name        = 'Turno'
        verbose_name_plural = 'Turnos'
        ordering            = ['fecha_solicitud']

    def clean(self):
        super().clean()
        if self.fecha_llamado and self.fecha_solicitud:
            if self.fecha_llamado < self.fecha_solicitud:
                raise ValidationError({
                    'fecha_llamado': 'La fecha de llamado no puede ser anterior a la solicitud.'
                })

    def tiempo_espera_minutos(self):
        """Minutos entre solicitud y llamado."""
        if self.fecha_llamado and self.fecha_solicitud:
            delta = self.fecha_llamado - self.fecha_solicitud
            return round(delta.total_seconds() / 60, 1)
        return None

    def tiempo_atencion_minutos(self):
        """Minutos entre llamado y resolución."""
        if self.fecha_resolucion and self.fecha_llamado:
            delta = self.fecha_resolucion - self.fecha_llamado
            return round(delta.total_seconds() / 60, 1)
        return None

    def __str__(self):
        return f"Turno #{self.numero_turno} — {self.ciudadano.nombre} ({self.get_estado_display()})"


class Expediente(models.Model):
    """Documento/expediente asociado a un turno, derivable entre ventanillas."""
    ESTADO_CHOICES = [
        ('iniciado',   'Iniciado'),
        ('en_proceso', 'En Proceso'),
        ('derivado',   'Derivado'),
        ('cerrado',    'Cerrado'),
    ]

    id           = models.AutoField(primary_key=True)
    turno        = models.OneToOneField(
        Turno,
        on_delete=models.CASCADE,
        related_name='expediente'
    )
    numero       = models.CharField(max_length=50, unique=True)
    ventanilla_actual = models.ForeignKey(
        Ventanilla,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='expedientes'
    )
    estado       = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='iniciado'
    )
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    notas        = models.TextField(blank=True)

    class Meta:
        verbose_name        = 'Expediente'
        verbose_name_plural = 'Expedientes'
        ordering            = ['-fecha_inicio']

    def __str__(self):
        return f"Expediente {self.numero} — {self.estado}"
