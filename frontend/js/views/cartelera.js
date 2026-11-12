// Pantalla principal: cartelera con buscador, filtro por género y próxima sesión destacada.
import { loadCatalog } from '../api.js';
import { emptyState, poster } from '../components.js';
import { diaCorto, diaLargo, duracion, eur, h, hora, parseDate, setTitle } from '../utils.js';

export async function cartelera() {
  setTitle('Cartelera');
  const cat = await loadCatalog();
  const ahora = new Date();

  const futuras = cat.sesiones
    .map((s) => ({ ...s, _d: parseDate(s.fecha) }))
    .filter((s) => s._d > ahora)
    .sort((a, b) => a._d - b._d);

  const porPelicula = new Map();
  for (const s of futuras) {
    if (!porPelicula.has(s.pelicula_id)) porPelicula.set(s.pelicula_id, []);
    porPelicula.get(s.pelicula_id).push(s);
  }

  // Primero las películas con sesiones (la más próxima antes), luego el resto por nombre.
  const ordenadas = [...cat.peliculas].sort((a, b) => {
    const sa = porPelicula.get(a.id)?.[0]?._d;
    const sb = porPelicula.get(b.id)?.[0]?._d;
    if (sa && sb) return sa - sb;
    if (sa) return -1;
    if (sb) return 1;
    return a.nombre.localeCompare(b.nombre, 'es');
  });

  const generos = [...new Set(cat.peliculas.map((p) => p.genero))].sort((a, b) => a.localeCompare(b, 'es'));
  const estado = { q: '', genero: '' };

  // ----- Cabecera destacada -----
  const proxima = futuras[0];
  let hero;
  if (proxima) {
    const peli = cat.peliculaPorId.get(proxima.pelicula_id);
    const sala = cat.salaPorId.get(proxima.sala_id);
    hero = h(
      'section',
      { class: 'hero', 'aria-labelledby': 'hero-title' },
      h('p', { class: 'eyebrow' }, 'Próxima sesión'),
      h('h1', { id: 'hero-title' }, peli?.nombre ?? 'Sesión'),
      h(
        'p',
        { class: 'hero-meta' },
        `${diaCorto(proxima._d)} · ${hora(proxima._d)}`,
        sala ? ` · Sala ${sala.numero}` : '',
        ` · ${eur(proxima.precio)} por butaca`,
      ),
      h(
        'div',
        { class: 'actions' },
        h('a', { class: 'btn btn-primary', href: `#/sesion/${encodeURIComponent(proxima.id)}` }, 'Elegir butacas'),
        peli && h('a', { class: 'btn btn-ghost', href: `#/pelicula/${encodeURIComponent(peli.id)}` }, 'Ver todas las sesiones'),
      ),
    );
  } else {
    hero = h(
      'section',
      { class: 'hero' },
      h('p', { class: 'eyebrow' }, 'Web Cine'),
      h('h1', {}, 'Cartelera'),
      h('p', { class: 'hero-meta' }, 'Todavía no hay sesiones programadas. Vuelve pronto.'),
    );
  }

  // ----- Filtros -----
  const grid = h('div', { class: 'film-grid' });
  const contador = h('p', { class: 'muted small', 'aria-live': 'polite' });
  const buscador = h('input', {
    class: 'input',
    type: 'search',
    placeholder: 'Buscar película…',
    'aria-label': 'Buscar película',
    oninput: (e) => { estado.q = e.target.value; dibujar(); },
  });
  const chips = h('div', { class: 'chips', role: 'group', 'aria-label': 'Filtrar por género' });

  function dibujarChips() {
    chips.replaceChildren(
      ...['', ...generos].map((g) =>
        h('button', {
          class: 'chip chip-btn',
          type: 'button',
          'aria-pressed': String(estado.genero === g),
          onclick: () => { estado.genero = g; dibujarChips(); dibujar(); },
        }, g || 'Todos'),
      ),
    );
  }

  function tarjeta(p) {
    const sesiones = porPelicula.get(p.id) ?? [];
    return h(
      'article',
      { class: 'film-card' },
      poster(p),
      h(
        'div',
        { class: 'film-body' },
        h('h3', {}, h('a', { class: 'stretched', href: `#/pelicula/${encodeURIComponent(p.id)}` }, p.nombre)),
        h('p', { class: 'muted small' }, `${p.genero} · ${duracion(p.duracion)}`),
        sesiones.length
          ? h(
            'div',
            { class: 'chips' },
            ...sesiones.slice(0, 3).map((s) =>
              h('a', {
                class: 'chip chip-link',
                href: `#/sesion/${encodeURIComponent(s.id)}`,
                'aria-label': `Reservar sesión del ${diaLargo(s._d)} a las ${hora(s._d)}`,
              }, `${diaCorto(s._d)} ${hora(s._d)}`),
            ),
            sesiones.length > 3 && h('span', { class: 'chip chip-more' }, `+${sesiones.length - 3}`),
          )
          : h('p', { class: 'small muted' }, 'Sin sesiones programadas'),
      ),
    );
  }

  function dibujar() {
    const q = estado.q.trim().toLowerCase();
    const lista = ordenadas.filter(
      (p) => (!q || p.nombre.toLowerCase().includes(q)) && (!estado.genero || p.genero === estado.genero),
    );
    contador.textContent = `${lista.length} ${lista.length === 1 ? 'película' : 'películas'}`;
    if (!lista.length) {
      grid.replaceChildren(
        emptyState(
          cat.peliculas.length ? 'Sin resultados' : 'La cartelera está vacía',
          cat.peliculas.length ? 'Prueba con otra búsqueda o género.' : 'Aún no se ha añadido ninguna película.',
          !cat.peliculas.length && h('a', { class: 'btn btn-primary', href: '#/gestion/peliculas' }, 'Añadir películas'),
        ),
      );
      return;
    }
    grid.replaceChildren(...lista.map(tarjeta));
  }

  dibujarChips();
  dibujar();

  return h(
    'div',
    { class: 'container page' },
    hero,
    cat.peliculas.length > 0 && h(
      'div',
      { class: 'toolbar' },
      h('div', { class: 'toolbar-search' }, buscador),
      chips,
    ),
    contador,
    grid,
  );
}
