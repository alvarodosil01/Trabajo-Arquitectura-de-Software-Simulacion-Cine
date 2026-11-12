// Detalle de una película y sus próximas sesiones agrupadas por día.
import { api } from '../api.js';
import { emptyState, poster } from '../components.js';
import {
  dayKey, diaLargo, duracion, eur, etiquetaRelativa, h, hora, parseDate, setTitle,
} from '../utils.js';

export async function peliculaView(id) {
  const [pelicula, sesiones, salas] = await Promise.all([api.pelicula(id), api.sesiones(id), api.salas()]);
  setTitle(pelicula.nombre);

  const salaPorId = new Map(salas.map((s) => [s.id, s]));
  const ahora = new Date();
  const futuras = sesiones
    .map((s) => ({ ...s, _d: parseDate(s.fecha) }))
    .filter((s) => s._d > ahora)
    .sort((a, b) => a._d - b._d);

  const dias = new Map();
  for (const s of futuras) {
    const k = dayKey(s._d);
    if (!dias.has(k)) dias.set(k, []);
    dias.get(k).push(s);
  }

  function sesionCard(s) {
    const sala = salaPorId.get(s.sala_id);
    const aforo = sala ? sala.filas * sala.columnas : 0;
    const libres = Math.max(aforo - s.butacas_ocupadas.length, 0);
    const agotada = libres === 0;
    const etiqueta = `${hora(s._d)}, ${sala ? `sala ${sala.numero}, ` : ''}${agotada ? 'agotada' : `${libres} butacas libres`}`;
    return h(
      agotada ? 'div' : 'a',
      {
        class: `session${agotada ? ' soldout' : ''}`,
        href: agotada ? null : `#/sesion/${encodeURIComponent(s.id)}`,
        'aria-label': etiqueta,
        'aria-disabled': agotada ? 'true' : null,
      },
      h('span', { class: 'session-time' }, hora(s._d)),
      h('span', { class: 'session-meta' }, sala ? `Sala ${sala.numero}` : 'Sala'),
      h('span', { class: 'session-price' }, eur(s.precio)),
      h(
        'span',
        { class: `session-free${libres > 0 && libres <= 5 ? ' low' : ''}${agotada ? ' none' : ''}` },
        agotada ? 'Agotada' : `${libres} libres`,
      ),
    );
  }

  return h(
    'div',
    { class: 'container page' },
    h('a', { class: 'back', href: '#/' }, '← Cartelera'),
    h(
      'section',
      { class: 'film-header' },
      poster(pelicula, 'poster-lg'),
      h(
        'div',
        {},
        h('p', { class: 'eyebrow' }, pelicula.genero),
        h('h1', {}, pelicula.nombre),
        h('p', { class: 'muted' }, `Duración: ${duracion(pelicula.duracion)}`),
      ),
    ),
    h('h2', { class: 'section-title' }, 'Próximas sesiones'),
    futuras.length
      ? h(
        'div',
        { class: 'days' },
        ...[...dias.values()].map((lista) => {
          const rel = etiquetaRelativa(lista[0]._d);
          return h(
            'section',
            { class: 'day' },
            h('h3', {}, diaLargo(lista[0]._d), rel && h('span', { class: 'badge' }, rel)),
            h('div', { class: 'session-list' }, ...lista.map(sesionCard)),
          );
        }),
      )
      : emptyState('Sin sesiones programadas', 'Esta película aún no tiene sesiones futuras.'),
  );
}
