from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from Tramites.views import (
    inicio,
    login_view, registro_view, logout_view,
    solicitar_turno, mis_turnos, turnos_json,
    panel_funcionario, llamar_siguiente,
    panel_ventanillas, derivar_expediente,
    dashboard, solicitar_licencia,
    panel_publico,
    # Departamentos
    listado_departamentos, nuevo_departamento, guardar_departamento,
    editar_departamento, actualizar_departamento, eliminar_departamento,
    # Ventanillas
    listado_ventanillas, nueva_ventanilla, guardar_ventanilla,
    editar_ventanilla, actualizar_ventanilla, eliminar_ventanilla,
    # Funcionarios
    listado_funcionarios, nuevo_funcionario, guardar_funcionario,
    editar_funcionario, actualizar_funcionario, eliminar_funcionario,
    # Tipos de Trámite
    listado_tipos_tramite, nuevo_tipo_tramite, guardar_tipo_tramite,
    editar_tipo_tramite, actualizar_tipo_tramite, eliminar_tipo_tramite,
    # Ciudadanos
    listado_ciudadanos, nuevo_ciudadano, guardar_ciudadano,
    editar_ciudadano, actualizar_ciudadano, eliminar_ciudadano,
    # Turnos
    listado_turnos, nuevo_turno, guardar_turno,
    editar_turno, actualizar_turno, eliminar_turno,
    # Expedientes
    listado_expedientes, nuevo_expediente, guardar_expediente,
    editar_expediente, actualizar_expediente, eliminar_expediente,
)

urlpatterns = [
    path('', inicio, name='inicio'),
    path('admin/', admin.site.urls),

    # ── Autenticación ──────────────────────────────
    path('login/',          login_view,    name='login'),
    path('registro/',       registro_view, name='registro'),
    path('logout/',         logout_view,   name='logout'),

    # ── Portal ciudadano ───────────────────────────
    path('solicitar-turno/',  solicitar_turno,  name='solicitar_turno'),
    path('mis-turnos/',       mis_turnos,        name='mis_turnos'),
    path('turnos-json/',      turnos_json,        name='turnos_json'),
    path('sala-espera/',      panel_publico,      name='panel_publico'),

    # ── Panel funcionario ──────────────────────────
    path('panel-funcionario/',  panel_funcionario, name='panel_funcionario'),
    path('llamar-siguiente/',   llamar_siguiente,  name='llamar_siguiente'),

    # ── Panel ventanillas drag & drop ──────────────
    path('panel-ventanillas/',  panel_ventanillas, name='panel_ventanillas'),
    path('derivar-expediente/', derivar_expediente,name='derivar_expediente'),

    # ── Dashboard ──────────────────────────────────
    path('dashboard/',          dashboard,          name='dashboard'),
    path('solicitar-licencia/', solicitar_licencia, name='solicitar_licencia'),

    # ── Departamentos ──────────────────────────────
    path('departamentos/',                        listado_departamentos,    name='listado_departamentos'),
    path('departamentos/nuevo/',                  nuevo_departamento,       name='nuevo_departamento'),
    path('departamentos/guardar/',                guardar_departamento,     name='guardar_departamento'),
    path('departamentos/editar/<int:id>/',        editar_departamento,      name='editar_departamento'),
    path('departamentos/actualizar/<int:id>/',    actualizar_departamento,  name='actualizar_departamento'),
    path('departamentos/eliminar/<int:id>/',      eliminar_departamento,    name='eliminar_departamento'),

    # ── Ventanillas ────────────────────────────────
    path('ventanillas/',                          listado_ventanillas,      name='listado_ventanillas'),
    path('ventanillas/nueva/',                    nueva_ventanilla,         name='nueva_ventanilla'),
    path('ventanillas/guardar/',                  guardar_ventanilla,       name='guardar_ventanilla'),
    path('ventanillas/editar/<int:id>/',          editar_ventanilla,        name='editar_ventanilla'),
    path('ventanillas/actualizar/<int:id>/',      actualizar_ventanilla,    name='actualizar_ventanilla'),
    path('ventanillas/eliminar/<int:id>/',        eliminar_ventanilla,      name='eliminar_ventanilla'),

    # ── Funcionarios ───────────────────────────────
    path('funcionarios/',                         listado_funcionarios,     name='listado_funcionarios'),
    path('funcionarios/nuevo/',                   nuevo_funcionario,        name='nuevo_funcionario'),
    path('funcionarios/guardar/',                 guardar_funcionario,      name='guardar_funcionario'),
    path('funcionarios/editar/<int:id>/',         editar_funcionario,       name='editar_funcionario'),
    path('funcionarios/actualizar/<int:id>/',     actualizar_funcionario,   name='actualizar_funcionario'),
    path('funcionarios/eliminar/<int:id>/',       eliminar_funcionario,     name='eliminar_funcionario'),

    # ── Tipos de Trámite ───────────────────────────
    path('tipos-tramite/',                        listado_tipos_tramite,    name='listado_tipos_tramite'),
    path('tipos-tramite/nuevo/',                  nuevo_tipo_tramite,       name='nuevo_tipo_tramite'),
    path('tipos-tramite/guardar/',                guardar_tipo_tramite,     name='guardar_tipo_tramite'),
    path('tipos-tramite/editar/<int:id>/',        editar_tipo_tramite,      name='editar_tipo_tramite'),
    path('tipos-tramite/actualizar/<int:id>/',    actualizar_tipo_tramite,  name='actualizar_tipo_tramite'),
    path('tipos-tramite/eliminar/<int:id>/',      eliminar_tipo_tramite,    name='eliminar_tipo_tramite'),

    # ── Ciudadanos ─────────────────────────────────
    path('ciudadanos/',                           listado_ciudadanos,       name='listado_ciudadanos'),
    path('ciudadanos/nuevo/',                     nuevo_ciudadano,          name='nuevo_ciudadano'),
    path('ciudadanos/guardar/',                   guardar_ciudadano,        name='guardar_ciudadano'),
    path('ciudadanos/editar/<int:id>/',           editar_ciudadano,         name='editar_ciudadano'),
    path('ciudadanos/actualizar/<int:id>/',       actualizar_ciudadano,     name='actualizar_ciudadano'),
    path('ciudadanos/eliminar/<int:id>/',         eliminar_ciudadano,       name='eliminar_ciudadano'),

    # ── Turnos ─────────────────────────────────────
    path('turnos/',                               listado_turnos,           name='listado_turnos'),
    path('turnos/nuevo/',                         nuevo_turno,              name='nuevo_turno'),
    path('turnos/guardar/',                       guardar_turno,            name='guardar_turno'),
    path('turnos/editar/<int:id>/',               editar_turno,             name='editar_turno'),
    path('turnos/actualizar/<int:id>/',           actualizar_turno,         name='actualizar_turno'),
    path('turnos/eliminar/<int:id>/',             eliminar_turno,           name='eliminar_turno'),

    # ── Expedientes ────────────────────────────────
    path('expedientes/',                          listado_expedientes,      name='listado_expedientes'),
    path('expedientes/nuevo/',                    nuevo_expediente,         name='nuevo_expediente'),
    path('expedientes/guardar/',                  guardar_expediente,       name='guardar_expediente'),
    path('expedientes/editar/<int:id>/',          editar_expediente,        name='editar_expediente'),
    path('expedientes/actualizar/<int:id>/',      actualizar_expediente,    name='actualizar_expediente'),
    path('expedientes/eliminar/<int:id>/',        eliminar_expediente,      name='eliminar_expediente'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,  document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
