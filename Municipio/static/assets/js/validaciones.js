/**
 * validaciones.js
 * Reglas de validación personalizadas para Municipio Digital
 * Aplica en todos los formularios del sistema
 */

// ══════════════════════════════════════════
// MÉTODOS PERSONALIZADOS jQuery Validate
// ══════════════════════════════════════════

// ── Solo letras (permite espacios y tildes) ──
$.validator.addMethod('soloLetras', function (value) {
  return this.optional(value) || /^[a-záéíóúüñA-ZÁÉÍÓÚÜÑ\s]+$/.test(value.trim());
}, 'Este campo solo acepta letras, no números.');

// ── Solo números ──
$.validator.addMethod('soloNumeros', function (value) {
  return this.optional(value) || /^\d+$/.test(value.trim());
}, 'Este campo solo acepta números, no letras.');

// ── Cédula ecuatoriana válida ──
$.validator.addMethod('cedulaEcuador', function (value) {
  if (this.optional(value)) return true;
  const cedula = value.trim();

  // Longitud exacta 10
  if (!/^\d{10}$/.test(cedula)) return false;

  // Primer dígito: provincia (01-24)
  const provincia = parseInt(cedula.substring(0, 2));
  if (provincia < 1 || provincia > 24) return false;

  // Tercer dígito < 6 (persona natural)
  const tercero = parseInt(cedula[2]);
  if (tercero >= 6) return false;

  // Algoritmo de verificación (módulo 10)
  const coef   = [2, 1, 2, 1, 2, 1, 2, 1, 2];
  let suma     = 0;
  for (let i = 0; i < 9; i++) {
    let val = parseInt(cedula[i]) * coef[i];
    if (val >= 10) val -= 9;
    suma += val;
  }
  const verificador = suma % 10 === 0 ? 0 : 10 - (suma % 10);
  if (verificador !== parseInt(cedula[9])) return false;

  // No acepta dígitos repetidos (1111111111, 2222222222, etc.)
  if (/^(\d)\1{9}$/.test(cedula)) return false;

  return true;
}, 'La cédula ingresada no es válida.');

// ── Teléfono ecuatoriano ──
// Formatos válidos: 09XXXXXXXX (celular) o 0[2-7]XXXXXXX (fijo)
$.validator.addMethod('telefonoEcuador', function (value) {
  if (this.optional(value)) return true;
  const tel = value.trim().replace(/[\s\-()]/g, '');

  // Solo dígitos
  if (!/^\d+$/.test(tel)) return false;

  // Celular: 10 dígitos, empieza con 09
  if (/^09\d{8}$/.test(tel)) return true;

  // Fijo: 9 dígitos, empieza con 02-07
  if (/^0[2-7]\d{7}$/.test(tel)) return true;

  return false;
}, 'Ingresá un teléfono ecuatoriano válido (ej: 0991234567 o 022345678).');

// ── No repetidos (no acepta 111111, aaa, etc.) ──
$.validator.addMethod('noRepetido', function (value) {
  if (this.optional(value)) return true;
  const v = value.trim();
  // Si todos los caracteres son iguales
  return !v.split('').every(c => c === v[0]);
}, 'Este campo no puede tener caracteres todos iguales.');

// ── Legajo: alfanumérico sin espacios ──
$.validator.addMethod('legajoValido', function (value) {
  return this.optional(value) || /^[a-zA-Z0-9\-]+$/.test(value.trim());
}, 'El legajo solo acepta letras, números y guiones.');


// ══════════════════════════════════════════
// OPCIONES GLOBALES jQuery Validate
// ══════════════════════════════════════════
$.validator.setDefaults({
  errorClass:  'text-danger small d-block mt-1',
  validClass:  'is-valid',
  highlight:   function (el) { $(el).addClass('is-invalid').removeClass('is-valid'); },
  unhighlight: function (el) { $(el).removeClass('is-invalid').addClass('is-valid'); },
  errorPlacement: function (error, element) {
    error.insertAfter(element.closest('.input-group, .form-select, input, textarea') );
  }
});


// ══════════════════════════════════════════
// BLOQUEO EN TIEMPO REAL (keypress / input)
// ══════════════════════════════════════════
$(document).ready(function () {

  // Campos que solo aceptan letras: nombre, descripcion de ventanilla, notas
  $('input[name="nombre"], input[name="descripcion"]').each(function () {
    // Solo bloquear si el campo es claramente de texto (no número, no email)
    if ($(this).attr('type') === 'text' || !$(this).attr('type')) {
      $(this)
        .on('keypress', function (e) {
          const char = String.fromCharCode(e.which);
          if (/[0-9]/.test(char)) {
            e.preventDefault();
            mostrarAviso(this, '⚠️ Solo se permiten letras');
          }
        })
        .on('input', function () {
          if (/[0-9]/.test(this.value)) {
            this.value = this.value.replace(/[0-9]/g, '');
            mostrarAviso(this, '⚠️ Solo se permiten letras');
          }
        });
    }
  });

  // Campos que solo aceptan números: numero_turno, numero (ventanilla)
  $('input[name="numero_turno"], input[name="numero"][type="number"]').on('input', function () {
    if (!/^\d*$/.test(this.value)) {
      this.value = this.value.replace(/\D/g, '');
    }
  });

  // Teléfono: solo dígitos, guiones, paréntesis y espacios
  $('input[name="telefono"]').on('input', function () {
    this.value = this.value.replace(/[^0-9\s\-()]/g, '');
  });

  // DNI / Cédula: solo números
  $('input[name="dni"]').on('input', function () {
    this.value = this.value.replace(/\D/g, '');
  });

  // Costo: no negativo
  $('input[name="costo"], input[name="duracion_estimada_min"]').on('input', function () {
    if (parseFloat(this.value) < 0) this.value = 0;
  });

});

// ── Helper: muestra aviso temporal bajo el campo ──
function mostrarAviso(campo, texto) {
  const id  = 'aviso-' + ($(campo).attr('name') || 'field');
  let $aviso = $('#' + id);
  if (!$aviso.length) {
    $aviso = $('<small>')
      .attr('id', id)
      .addClass('text-warning small d-block mt-1');
    $(campo).after($aviso);
  }
  $aviso.text(texto).stop(true).fadeIn(150).delay(2000).fadeOut(400);
}
