// Gestión del catálogo: películas, sesiones y salas (la API no exige login en esta versión).
import { api, loadCatalog } from '../api.js';
import { alertBox, emptyState, field, showAlert } from '../components.js';
import {
  confirmDialog, duracion, eur, fechaHora, h, openDialog, parseDate, setTitle, toInputValue, toast,
} from '../utils.js';

const TABS = [
  ['peliculas', 'Películas'],
  ['sesiones', 'Sesiones'],
  ['salas', 'Salas'],
];

export async function gestionView(tab) {
  const activa = TABS.some(([k]) => k === tab) ? tab : 'peliculas';
  setTitle('Gestión');

  const stats = h('div', { class: 'stats' });
  const panel = h('div', { class: 'panel-body' });

  async function cargar() {
    const cat = await loadCatalog();
    const ahora = new Date();
    const futuras = cat.sesiones.filter((s) => parseDate(s.fecha) > ahora);
    const vendidas = cat.sesiones.reduce((n, s) => n + s.butacas_ocupadas.length, 0);
    const aforoFuturas = futuras.reduce((n, s) => {
      const sala = cat.salaPorId.get(s.sala_id);
      return n + (sala ? sala.filas * sala.columnas : 0);
    }, 0);
    const ocupadasFuturas = futuras.reduce((n, s) => n + s.butacas_ocupadas.length, 0);
    const media = aforoFuturas ? Math.round((ocupadasFuturas / aforoFuturas) * 100) : 0;

    stats.replaceChildren(
      stat(cat.peliculas.length, 'Películas'),
      stat(futuras.length, 'Sesiones futuras'),
      stat(vendidas, 'Butacas vendidas'),
      stat(`${media}%`, 'Ocupación media (futuras)'),
    );

    panel.replaceChildren(
      activa === 'peliculas' ? panelPeliculas(cat, cargar)
        : activa === 'sesiones' ? panelSesiones(cat, cargar)
          : panelSalas(cat),
    );
  }

  await cargar();

  return h(
    'div',
    { class: 'container page' },
    h('p', { class: 'eyebrow' }, 'Administración'),
    h('h1', {}, 'Gestión del cine'),
    h('p', { class: 'muted' }, 'Zona de gestión de acceso abierto en esta versión: cualquier visitante puede modificar el catálogo.'),
    stats,
    h(
      'nav',
      { class: 'tabs', 'aria-label': 'Secciones de gestión' },
      ...TABS.map(([k, nombre]) =>
        h('a', { href: `#/gestion/${k}`, 'aria-current': k === activa ? 'page' : null }, nombre)),
    ),
    panel,
  );
}

const stat = (valor, etiqueta) =>
  h('div', { class: 'stat' }, h('strong', {}, String(valor)), h('span', { class: 'muted small' }, etiqueta));

// ======================= Películas =======================
function panelPeliculas(cat, recargar) {
  const sesionesDe = (id) => cat.sesiones.filter((s) => s.pelicula_id === id).length;
  const lista = [...cat.peliculas].sort((a, b) => a.nombre.localeCompare(b.nombre, 'es'));

  const cabecera = h(
    'div',
    { class: 'panel-actions' },
    h('h2', {}, `Películas (${lista.length})`),
    h('button', { class: 'btn btn-primary', type: 'button', onclick: () => dialogoPelicula(null, cat, recargar) }, '+ Nueva película'),
  );

  if (!lista.length) {
    return h('div', {}, cabecera, emptyState('No hay películas', 'Crea la primera para poder programar sesiones.'));
  }

  return h(
    'div',
    {},
    cabecera,
    h(
      'div',
      { class: 'table-wrap' },
      h(
        'table',
        { class: 'table' },
        h('thead', {}, h('tr', {}, ...['Nombre', 'Género', 'Duración', 'Sesiones', ''].map((t) => h('th', { scope: 'col' }, t)))),
        h(
          'tbody',
          {},
          ...lista.map((p) => {
            const n = sesionesDe(p.id);
            return h(
              'tr',
              {},
              h('td', { 'data-label': 'Nombre' }, h('strong', {}, p.nombre)),
              h('td', { 'data-label': 'Género' }, p.genero),
              h('td', { 'data-label': 'Duración' }, duracion(p.duracion)),
              h('td', { 'data-label': 'Sesiones' }, String(n)),
              h(
                'td',
                { class: 'row-actions' },
                h('button', { class: 'btn btn-ghost btn-sm', type: 'button', onclick: () => dialogoPelicula(p, cat, recargar) }, 'Editar'),
                h('button', {
                  class: 'btn btn-danger-ghost btn-sm',
                  type: 'button',
                  disabled: n > 0,
                  title: n > 0 ? 'No se puede eliminar una película con sesiones' : null,
                  'aria-label': `Eliminar ${p.nombre}`,
                  onclick: () => eliminarPelicula(p, recargar),
                }, 'Eliminar'),
              ),
            );
          }),
        ),
      ),
    ),
  );
}

async function eliminarPelicula(p, recargar) {
  const ok = await confirmDialog({
    title: 'Eliminar película',
    message: `¿Eliminar «${p.nombre}»? Esta acción no se puede deshacer.`,
    confirmLabel: 'Eliminar',
    danger: true,
  });
  if (!ok) return;
  try {
    await api.eliminarPelicula(p.id);
    toast('Película eliminada', 'success');
    await recargar();
  } catch (err) {
    toast(err.message, 'error');
  }
}

function dialogoPelicula(pelicula, cat, recargar) {
  const editando = Boolean(pelicula);
  const nombre = h('input', { class: 'input', maxlength: '200', required: true, value: pelicula?.nombre ?? '' });
  const genero = h('input', {
    class: 'input', maxlength: '100', required: true, list: 'lista-generos', value: pelicula?.genero ?? '',
  });
  const dur = h('input', {
    class: 'input', type: 'number', min: '1', max: '1440', step: '1', inputmode: 'numeric', required: true,
    value: pelicula?.duracion ?? '',
  });
  const generos = [...new Set(cat.peliculas.map((p) => p.genero))];
  const error = alertBox();
  const guardar = h('button', { class: 'btn btn-primary', type: 'submit' }, editando ? 'Guardar cambios' : 'Crear película');

  const form = h(
    'form',
    { class: 'form', novalidate: true },
    field('Nombre', nombre),
    field('Género', genero),
    h('datalist', { id: 'lista-generos' }, ...generos.map((g) => h('option', { value: g }))),
    field('Duración (minutos)', dur, editando && cat.sesiones.some((s) => s.pelicula_id === pelicula.id)
      ? 'No se puede cambiar la duración porque la película ya tiene sesiones.' : null),
    error,
    h(
      'div',
      { class: 'actions' },
      h('button', { class: 'btn btn-ghost', type: 'button', onclick: () => dlg.close() }, 'Cancelar'),
      guardar,
    ),
  );

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    showAlert(error, '');
    const datos = { nombre: nombre.value.trim(), genero: genero.value.trim(), duracion: Number(dur.value) };
    if (!datos.nombre) return showAlert(error, 'El nombre es obligatorio.');
    if (!datos.genero) return showAlert(error, 'El género es obligatorio.');
    if (!Number.isInteger(datos.duracion) || datos.duracion < 1 || datos.duracion > 1440) {
      return showAlert(error, 'La duración debe ser un número entero de minutos entre 1 y 1440.');
    }
    guardar.disabled = true;
    try {
      if (editando) await api.actualizarPelicula(pelicula.id, datos);
      else await api.crearPelicula(datos);
      dlg.close();
      toast(editando ? 'Película actualizada' : 'Película creada', 'success');
      await recargar();
    } catch (err) {
      showAlert(error, err.message);
      guardar.disabled = false;
    }
  });

  const dlg = openDialog({ title: editando ? 'Editar película' : 'Nueva película', body: form });
  nombre.focus();
}

// ======================= Sesiones =======================
function panelSesiones(cat, recargar) {
  const filtro = h(
    'select',
    { class: 'input', 'aria-label': 'Filtrar por película', onchange: (e) => pintar(e.target.value) },
    h('option', { value: '' }, 'Todas las películas'),
    ...[...cat.peliculas].sort((a, b) => a.nombre.localeCompare(b.nombre, 'es'))
      .map((p) => h('option', { value: p.id }, p.nombre)),
  );
  const tabla = h('div', {});

  const nueva = h('button', {
    class: 'btn btn-primary',
    type: 'button',
    disabled: !cat.peliculas.length,
    title: cat.peliculas.length ? null : 'Crea antes una película',
    onclick: () => dialogoSesion(null, cat, recargar),
  }, '+ Nueva sesión');

  function pintar(peliculaId) {
    const ahora = new Date();
    const lista = cat.sesiones
      .filter((s) => !peliculaId || s.pelicula_id === peliculaId)
      .map((s) => ({ ...s, _d: parseDate(s.fecha) }))
      .sort((a, b) => a._d - b._d);

    if (!lista.length) {
      tabla.replaceChildren(emptyState('No hay sesiones', cat.peliculas.length ? 'Programa una sesión con el botón «Nueva sesión».' : 'Crea primero una película.'));
      return;
    }

    tabla.replaceChildren(
      h(
        'div',
        { class: 'table-wrap' },
        h(
          'table',
          { class: 'table' },
          h('thead', {}, h('tr', {}, ...['Película', 'Sala', 'Fecha y hora', 'Precio', 'Ocupación', ''].map((t) => h('th', { scope: 'col' }, t)))),
          h(
            'tbody',
            {},
            ...lista.map((s) => {
              const peli = cat.peliculaPorId.get(s.pelicula_id);
              const sala = cat.salaPorId.get(s.sala_id);
              const aforo = sala ? sala.filas * sala.columnas : 0;
              const ocup = s.butacas_ocupadas.length;
              const pasada = s._d <= ahora;
              const conReservas = ocup > 0;
              const motivo = conReservas ? 'No se puede modificar una sesión con reservas' : pasada ? 'La sesión ya ha comenzado' : null;
              return h(
                'tr',
                {},
                h('td', { 'data-label': 'Película' }, h('strong', {}, peli?.nombre ?? '—')),
                h('td', { 'data-label': 'Sala' }, sala ? `Sala ${sala.numero}` : '—'),
                h('td', { 'data-label': 'Fecha' }, fechaHora(s._d), pasada && h('span', { class: 'badge badge-off' }, 'Finalizada')),
                h('td', { 'data-label': 'Precio' }, eur(s.precio)),
                h(
                  'td',
                  { 'data-label': 'Ocupación' },
                  h('div', { class: 'meter', role: 'img', 'aria-label': `${ocup} de ${aforo} butacas ocupadas` },
                    h('span', { style: `width:${aforo ? Math.round((ocup / aforo) * 100) : 0}%` })),
                  h('small', { class: 'muted' }, `${ocup}/${aforo}`),
                ),
                h(
                  'td',
                  { class: 'row-actions' },
                  h('button', {
                    class: 'btn btn-ghost btn-sm',
                    type: 'button',
                    disabled: Boolean(motivo),
                    title: motivo,
                    onclick: () => dialogoSesion(s, cat, recargar),
                  }, 'Editar'),
                  h('button', {
                    class: 'btn btn-danger-ghost btn-sm',
                    type: 'button',
                    disabled: conReservas,
                    title: conReservas ? 'No se puede eliminar una sesión con reservas' : null,
                    onclick: () => eliminarSesion(s, peli, recargar),
                  }, 'Eliminar'),
                ),
              );
            }),
          ),
        ),
      ),
    );
  }

  pintar('');
  return h(
    'div',
    {},
    h('div', { class: 'panel-actions' }, h('h2', {}, 'Sesiones'), h('div', { class: 'panel-actions-right' }, filtro, nueva)),
    tabla,
  );
}

async function eliminarSesion(s, peli, recargar) {
  const ok = await confirmDialog({
    title: 'Eliminar sesión',
    message: `¿Eliminar la sesión de «${peli?.nombre ?? 'película'}» del ${fechaHora(parseDate(s.fecha))}?`,
    confirmLabel: 'Eliminar',
    danger: true,
  });
  if (!ok) return;
  try {
    await api.eliminarSesion(s.id);
    toast('Sesión eliminada', 'success');
    await recargar();
  } catch (err) {
    toast(err.message, 'error');
  }
}

function dialogoSesion(sesion, cat, recargar) {
  const editando = Boolean(sesion);
  const selPeli = h(
    'select',
    { class: 'input', required: true, value: sesion?.pelicula_id ?? cat.peliculas[0]?.id },
    ...cat.peliculas.map((p) => h('option', { value: p.id }, `${p.nombre} (${duracion(p.duracion)})`)),
  );
  const selSala = h(
    'select',
    { class: 'input', required: true, value: sesion?.sala_id ?? cat.salas[0]?.id },
    ...cat.salas.map((s) => h('option', { value: s.id }, `Sala ${s.numero} · ${s.filas * s.columnas} butacas`)),
  );

  const manana = new Date();
  manana.setDate(manana.getDate() + 1);
  manana.setHours(18, 0, 0, 0);
  const fecha = h('input', {
    class: 'input',
    type: 'datetime-local',
    required: true,
    min: toInputValue(new Date()),
    value: sesion ? sesion.fecha.slice(0, 16) : toInputValue(manana),
  });
  const precio = h('input', {
    class: 'input', type: 'number', min: '0.01', step: '0.01', inputmode: 'decimal', required: true,
    value: sesion?.precio ?? '8.50',
  });
  const error = alertBox();
  const guardar = h('button', { class: 'btn btn-primary', type: 'submit' }, editando ? 'Guardar cambios' : 'Crear sesión');

  const form = h(
    'form',
    { class: 'form', novalidate: true },
    field('Película', selPeli),
    field('Sala', selSala),
    field('Fecha y hora', fecha, 'Hora local del cine. Debe ser futura y no solaparse con otra sesión de la sala.'),
    field('Precio por butaca (€)', precio),
    error,
    h(
      'div',
      { class: 'actions' },
      h('button', { class: 'btn btn-ghost', type: 'button', onclick: () => dlg.close() }, 'Cancelar'),
      guardar,
    ),
  );

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    showAlert(error, '');
    const valorPrecio = Number(precio.value);
    if (!fecha.value) return showAlert(error, 'Indica la fecha y la hora.');
    if (parseDate(fecha.value) <= new Date()) return showAlert(error, 'La fecha de la sesión debe ser futura.');
    if (!(valorPrecio > 0) || Math.round(valorPrecio * 100) / 100 !== valorPrecio) {
      return showAlert(error, 'El precio debe ser positivo y con un máximo de dos decimales.');
    }
    const datos = {
      pelicula_id: selPeli.value,
      sala_id: selSala.value,
      fecha: fecha.value.length === 16 ? `${fecha.value}:00` : fecha.value,
      precio: valorPrecio,
    };
    guardar.disabled = true;
    try {
      if (editando) await api.actualizarSesion(sesion.id, datos);
      else await api.crearSesion(datos);
      dlg.close();
      toast(editando ? 'Sesión actualizada' : 'Sesión creada', 'success');
      await recargar();
    } catch (err) {
      showAlert(error, err.message);
      guardar.disabled = false;
    }
  });

  const dlg = openDialog({ title: editando ? 'Editar sesión' : 'Nueva sesión', body: form });
}

// ======================= Salas =======================
function panelSalas(cat) {
  return h(
    'div',
    {},
    h('div', { class: 'panel-actions' }, h('h2', {}, 'Salas'), h('span', { class: 'muted small' }, 'Las salas son fijas y no se pueden modificar.')),
    h(
      'div',
      { class: 'room-grid' },
      ...cat.salas.map((s) => {
        const sesiones = cat.sesiones.filter((x) => x.sala_id === s.id).length;
        return h(
          'article',
          { class: 'room-card' },
          h('h3', {}, `Sala ${s.numero}`),
          h('p', { class: 'muted' }, `${s.filas} filas × ${s.columnas} butacas = ${s.filas * s.columnas}`),
          h(
            'div',
            { class: 'mini-room', style: `--cols:${s.columnas}`, 'aria-hidden': 'true' },
            ...Array.from({ length: s.filas * s.columnas }, () => h('i', {})),
          ),
          h('p', { class: 'small muted' }, `${sesiones} ${sesiones === 1 ? 'sesión programada' : 'sesiones programadas'}`),
        );
      }),
    ),
  );
}
