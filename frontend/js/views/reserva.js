// Entrada / justificante de una reserva (imprimible).
import { api } from '../api.js';
import { poster } from '../components.js';
import {
  cmpButacas, diaCompleto, eur, fechaHora, h, hora, parseDate, setTitle,
} from '../utils.js';

export async function reservaView(id) {
  const reserva = await api.reserva(id);
  const sesion = await api.sesion(reserva.sesion_id);
  const [pelicula, salas] = await Promise.all([api.pelicula(sesion.pelicula_id), api.salas()]);
  const sala = salas.find((s) => s.id === sesion.sala_id);
  const fecha = parseDate(sesion.fecha);
  const codigo = reserva.id.slice(0, 8).toUpperCase();
  const butacas = [...reserva.butacas_reservadas].sort(cmpButacas);
  setTitle(`Entrada ${codigo}`);

  const dato = (etiqueta, valor) =>
    h('div', { class: 'ticket-item' }, h('dt', {}, etiqueta), h('dd', {}, valor));

  return h(
    'div',
    { class: 'container page narrow' },
    h(
      'div',
      { class: 'ticket-intro no-print' },
      h('span', { class: 'check', 'aria-hidden': 'true' }, '✓'),
      h('h1', {}, 'Reserva confirmada'),
      h('p', { class: 'muted' }, 'Guarda este código: lo necesitarás en taquilla.'),
    ),
    h(
      'article',
      { class: 'ticket', 'aria-label': `Entrada ${codigo}` },
      h(
        'div',
        { class: 'ticket-main' },
        poster(pelicula, 'poster-sm'),
        h(
          'div',
          {},
          h('p', { class: 'eyebrow' }, 'Web Cine'),
          h('h2', {}, pelicula.nombre),
          h('p', { class: 'muted' }, `${pelicula.genero}`),
        ),
      ),
      h(
        'dl',
        { class: 'ticket-grid' },
        dato('Fecha', diaCompleto(fecha)),
        dato('Hora', hora(fecha)),
        dato('Sala', sala ? `Sala ${sala.numero}` : '—'),
        dato('Total', eur(reserva.precio_total)),
        h(
          'div',
          { class: 'ticket-item wide' },
          h('dt', {}, `Butacas (${butacas.length})`),
          h('dd', {}, h('span', { class: 'chips' }, ...butacas.map((b) => h('span', { class: 'chip chip-seat' }, b)))),
        ),
      ),
      h(
        'div',
        { class: 'ticket-stub' },
        h('div', {},
          h('p', { class: 'small muted' }, 'Código de reserva'),
          h('p', { class: 'code' }, codigo)),
        h('div', { class: 'barcode', 'aria-hidden': 'true' }),
      ),
      h('p', { class: 'small muted ticket-foot' }, `Reservado el ${fechaHora(parseDate(reserva.fecha_reserva))}`),
    ),
    h(
      'div',
      { class: 'actions center no-print' },
      h('button', { class: 'btn btn-primary', type: 'button', onclick: () => window.print() }, 'Imprimir entrada'),
      h('a', { class: 'btn btn-ghost', href: '#/reservas' }, 'Mis reservas'),
      h('a', { class: 'btn btn-ghost', href: '#/' }, 'Volver a la cartelera'),
    ),
  );
}
