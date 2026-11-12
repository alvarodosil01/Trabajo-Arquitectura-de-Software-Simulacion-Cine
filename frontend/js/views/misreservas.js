// Consulta de reservas por email.
import { api, loadCatalog } from '../api.js';
import { alertBox, emptyState, poster, showAlert } from '../components.js';
import {
  cmpButacas, diaCorto, eur, h, hora, leerCliente, parseDate, setTitle, guardarCliente,
} from '../utils.js';

export async function misReservasView() {
  setTitle('Mis reservas');
  const cliente = leerCliente();
  const resultados = h('div', { class: 'results', 'aria-live': 'polite' });
  const error = alertBox();
  const input = h('input', {
    class: 'input',
    type: 'email',
    name: 'email',
    autocomplete: 'email',
    required: true,
    placeholder: 'tu@email.com',
    'aria-label': 'Email de la reserva',
    value: cliente.email ?? '',
  });
  const boton = h('button', { class: 'btn btn-primary', type: 'submit' }, 'Buscar reservas');

  async function buscar(e) {
    e.preventDefault();
    showAlert(error, '');
    const email = input.value.trim();
    if (!email || !input.checkValidity()) {
      input.setAttribute('aria-invalid', 'true');
      input.focus();
      return showAlert(error, 'Escribe un email válido.');
    }
    input.removeAttribute('aria-invalid');
    boton.disabled = true;
    boton.textContent = 'Buscando…';
    try {
      const [reservas, cat] = await Promise.all([api.reservasPorEmail(email), loadCatalog()]);
      guardarCliente({ ...leerCliente(), email });
      pintar(reservas, cat);
    } catch (err) {
      resultados.replaceChildren();
      showAlert(error, err.message);
    } finally {
      boton.disabled = false;
      boton.textContent = 'Buscar reservas';
    }
  }

  function pintar(reservas, cat) {
    if (!reservas.length) {
      resultados.replaceChildren(
        emptyState('No hay reservas con ese email', 'Comprueba que lo has escrito igual que al reservar.',
          h('a', { class: 'btn btn-primary', href: '#/' }, 'Ver la cartelera')),
      );
      return;
    }
    const ahora = new Date();
    const filas = reservas
      .map((r) => {
        const sesion = cat.sesiones.find((s) => s.id === r.sesion_id);
        return { r, sesion, d: sesion ? parseDate(sesion.fecha) : null };
      })
      .sort((a, b) => {
        const fa = a.d > ahora;
        const fb = b.d > ahora;
        if (fa !== fb) return fa ? -1 : 1;
        return fa ? a.d - b.d : b.d - a.d; // próximas: antes la más cercana; pasadas: la más reciente
      });

    resultados.replaceChildren(
      h('p', { class: 'muted small' }, `${filas.length} ${filas.length === 1 ? 'reserva' : 'reservas'}`),
      ...filas.map(({ r, sesion, d }) => {
        const peli = sesion && cat.peliculaPorId.get(sesion.pelicula_id);
        const sala = sesion && cat.salaPorId.get(sesion.sala_id);
        const proxima = d && d > ahora;
        return h(
          'article',
          { class: 'booking-card' },
          peli && poster(peli, 'poster-sm'),
          h(
            'div',
            { class: 'booking-info' },
            h('h3', {}, peli?.nombre ?? 'Película'),
            h('p', { class: 'muted' }, d ? `${diaCorto(d)} · ${hora(d)}` : '', sala ? ` · Sala ${sala.numero}` : ''),
            h('div', { class: 'chips' }, ...[...r.butacas_reservadas].sort(cmpButacas).map((b) => h('span', { class: 'chip chip-seat' }, b))),
          ),
          h(
            'div',
            { class: 'booking-side' },
            h('span', { class: `badge ${proxima ? 'badge-ok' : 'badge-off'}` }, proxima ? 'Próxima' : 'Finalizada'),
            h('strong', {}, eur(r.precio_total)),
            h('a', { class: 'btn btn-ghost btn-sm', href: `#/reserva/${encodeURIComponent(r.id)}` }, 'Ver entrada'),
          ),
        );
      }),
    );
  }

  return h(
    'div',
    { class: 'container page narrow' },
    h('p', { class: 'eyebrow' }, 'Consulta'),
    h('h1', {}, 'Mis reservas'),
    h('p', { class: 'muted' }, 'Introduce el email con el que hiciste la reserva.'),
    h('form', { class: 'inline-form', novalidate: true, onsubmit: buscar }, input, boton),
    error,
    resultados,
  );
}
