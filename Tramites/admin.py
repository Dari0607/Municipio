from django.contrib import admin
from .models import (
    Departamento, Ventanilla, Funcionario,
    TipoTramite, Ciudadano, Turno, Expediente
)


@admin.register(Departamento)
class DepartamentoAdmin(admin.ModelAdmin):
    list_display  = ('id', 'nombre')
    search_fields = ('nombre',)


@admin.register(Ventanilla)
class VentanillaAdmin(admin.ModelAdmin):
    list_display  = ('numero', 'descripcion', 'departamento', 'activa')
    search_fields = ('descripcion',)
    list_filter   = ('activa', 'departamento')


@admin.register(Funcionario)
class FuncionarioAdmin(admin.ModelAdmin):
    list_display  = ('nombre', 'legajo', 'email', 'ventanilla', 'activo')
    search_fields = ('nombre', 'legajo')
    list_filter   = ('activo', 'ventanilla')


@admin.register(TipoTramite)
class TipoTramiteAdmin(admin.ModelAdmin):
    list_display  = ('nombre', 'departamento', 'duracion_estimada_min', 'activo')
    search_fields = ('nombre', 'descripcion')
    list_filter   = ('activo', 'departamento')


@admin.register(Ciudadano)
class CiudadanoAdmin(admin.ModelAdmin):
    list_display  = ('nombre', 'dni', 'email', 'telefono')
    search_fields = ('nombre', 'dni', 'email')


@admin.register(Turno)
class TurnoAdmin(admin.ModelAdmin):
    list_display  = (
        'numero_turno', 'ciudadano', 'tipo_tramite',
        'ventanilla', 'funcionario', 'estado', 'fecha_solicitud'
    )
    search_fields = ('ciudadano__nombre', 'ciudadano__dni')
    list_filter   = ('estado', 'ventanilla', 'tipo_tramite', 'fecha_solicitud')


@admin.register(Expediente)
class ExpedienteAdmin(admin.ModelAdmin):
    list_display  = ('numero', 'turno', 'ventanilla_actual', 'estado', 'fecha_inicio')
    search_fields = ('numero',)
    list_filter   = ('estado', 'ventanilla_actual')
