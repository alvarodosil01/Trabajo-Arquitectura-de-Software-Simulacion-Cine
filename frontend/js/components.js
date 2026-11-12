// Piezas de interfaz reutilizables.
import { h, iniciales, posterStyle } from './utils.js';

export function poster(pelicula, extra = '') {
  return h(
    'div',
    { class: `poster ${extra}`.trim(), style: posterStyle(pelicula.nombre, pelicula.genero), 'aria-hidden': 'true' },
    h('span', { class: 'poster-initials' }, iniciales(pelicula.nombre)),
    h('span', { class: 'poster-genre' }, pelicula.genero),
  );
}

export function loading(texto = 'Cargando…') {
  return h(
    'div',
    { class: 'container loading', 'aria-busy': 'true' },
    h('span', { class: 'spinner', 'aria-hidden': 'true' }),
    h('span', {}, texto),
  );
}

export function emptyState(titulo, texto, accion) {
  return h(
    'div',
    { class: 'empty' },
    h('div', { class: 'empty-icon', 'aria-hidden': 'true' }, '🎞️'),
    h('h3', {}, titulo),
    texto && h('p', { class: 'muted' }, texto),
    accion,
  );
}

export function errorState(error, onRetry) {
  const noEncontrado = error?.status === 404;
  return h(
    'div',
    { class: 'container page' },
    h(
      'div',
      { class: 'empty', role: 'alert' },
      h('div', { class: 'empty-icon', 'aria-hidden': 'true' }, noEncontrado ? '🔎' : '⚠️'),
      h('h2', {}, noEncontrado ? 'No encontrado' : 'Algo ha fallado'),
      h('p', { class: 'muted' }, error?.message ?? 'Error desconocido'),
      h(
        'div',
        { class: 'actions center' },
        h('a', { class: 'btn btn-ghost', href: '#/' }, 'Ir a la cartelera'),
        !noEncontrado && h('button', { class: 'btn btn-primary', type: 'button', onclick: onRetry }, 'Reintentar'),
      ),
    ),
  );
}

export function field(label, input, hint) {
  const id = input.id || `f-${Math.random().toString(36).slice(2, 8)}`;
  input.id = id;
  return h(
    'div',
    { class: 'field' },
    h('label', { for: id }, label),
    input,
    hint && h('small', { class: 'muted' }, hint),
  );
}

export const alertBox = () => h('div', { class: 'alert alert-error', role: 'alert', hidden: true });

export function showAlert(box, message) {
  box.textContent = message;
  box.hidden = !message;
}
