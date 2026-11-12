// Reserva: mapa de butacas interactivo, resumen y datos del cliente.
import { api } from '../api.js';
import { alertBox, field, poster, showAlert } from '../components.js';
import {
  cmpButacas, diaCompleto, eur, guardarCliente, h, hora, leerCliente, nombreButaca,
  parseDate, setTitle, toast,
} from '../utils.js';

export async function sesionView(id) {
  const sesion = await api.sesion(id);
  const [pelicula, salas, disp] = await Promise.all([
    api.pelicula(sesion.pelicula_id),
    api.salas(),
    api.butacas(id),
  ]);
  const sala = salas.find((s) => s.id === sesion.sala_id);
  const fecha = parseDate(sesion.fecha);
  const empezada = fecha <= new Date();
  setTitle(`Reservar · ${pelicula.nombre}`);

  let ocupadas = new Set(disp.ocupadas);
  const seleccion = new Set();
  const precioCent = Math.round(sesion.precio * 100);

  // ----- Cabecera -----
  const cabecera = h(
    'section',
    { class: 'film-header compact' },
    poster(pelicula, 'poster-sm'),
    h(
      'div',
      {},
      h('p', { class: 'eyebrow' }, 'Reserva de butacas'),
      h('h1', {}, pelicula.nombre),
      h(
        'p',
        { class: 'muted' },
        `${diaCompleto(fecha)} · ${hora(fecha)} · Sala ${sala?.numero ?? '?'} · ${eur(sesion.precio)} por butaca`,
      ),
    ),
  );
  const volver = h('a', { class: 'back', href: `#/pelicula/${encodeURIComponent(pelicula.id)}` }, `← ${pelicula.nombre}`);

  if (empezada || !sala) {
    return h(
      'div',
      { class: 'container page' },
      volver,
      cabecera,
      h('div', { class: 'alert alert-error', role: 'alert' },
        empezada ? 'Esta sesión ya ha comenzado y no admite más reservas.' : 'No se ha podido cargar la sala de esta sesión.'),
      h('a', { class: 'btn btn-primary', href: '#/' }, 'Ver la cartelera'),
    );
  }

  // ----- Mapa de butacas -----
  const mapa = h('div', { class: 'seatmap', style: `--cols:${sala.columnas}` });
  let matriz = [];

  function construirMapa() {
    matriz = [];
    const filas = [];
    for (let f = 0; f < sala.filas; f++) {
      const letra = String.fromCharCode(65 + f);
      const botones = [];
      for (let c = 1; c <= sala.columnas; c++) {
        const butaca = `${letra}${c}`;
        const ocupada = ocupadas.has(butaca);
        const elegida = seleccion.has(butaca);
        botones.push(
          h('button', {
            type: 'button',
            class: `seat${ocupada ? ' taken' : ''}${elegida ? ' selected' : ''}`,
            'aria-pressed': String(elegida),
            'aria-label': `${nombreButaca(butaca)}${ocupada ? ', ocupada' : ''}`,
            disabled: ocupada,
            dataset: { id: butaca, f, c: c - 1 },
          }, String(c)),
        );
      }
      matriz.push(botones);
      filas.push(
        h(
          'div',
          { class: 'seat-row', role: 'group', 'aria-label': `Fila ${letra}` },
          h('span', { class: 'row-label', 'aria-hidden': 'true' }, letra),
          ...botones,
          h('span', { class: 'row-label', 'aria-hidden': 'true' }, letra),
        ),
      );
    }
    mapa.replaceChildren(...filas);
  }

  mapa.addEventListener('click', (e) => {
    const btn = e.target.closest('.seat');
    if (!btn || btn.disabled) return;
    const id = btn.dataset.id;
    if (seleccion.has(id)) seleccion.delete(id);
    else seleccion.add(id);
    const activa = seleccion.has(id);
    btn.classList.toggle('selected', activa);
    btn.setAttribute('aria-pressed', String(activa));
    actualizarResumen();
  });

  // Navegación con flechas entre butacas libres
  mapa.addEventListener('keydown', (e) => {
    const delta = { ArrowLeft: [0, -1], ArrowRight: [0, 1], ArrowUp: [-1, 0], ArrowDown: [1, 0] }[e.key];
    const btn = e.target.closest('.seat');
    if (!delta || !btn) return;
    e.preventDefault();
    let f = Number(btn.dataset.f);
    let c = Number(btn.dataset.c);
    for (;;) {
      f += delta[0];
      c += delta[1];
      const destino = matriz[f]?.[c];
      if (!destino) return;
      if (!destino.disabled) { destino.focus(); return; }
    }
  });

  // ----- Resumen y formulario -----
  const cliente = leerCliente();
  const chipsSeleccion = h('div', { class: 'chips' });
  const total = h('strong', { class: 'total' });
  const inputNombre = h('input', {
    class: 'input', name: 'nombre', autocomplete: 'name', maxlength: '200', required: true, value: cliente.nombre ?? '',
  });
  const inputEmail = h('input', {
    class: 'input', name: 'email', type: 'email', autocomplete: 'email', required: true, value: cliente.email ?? '',
  });
  const error = alertBox();
  const botonReservar = h('button', { class: 'btn btn-primary btn-block', type: 'submit' }, 'Elige tus butacas');
  const libresTexto = h('span', { class: 'muted small', 'aria-live': 'polite' });

  function actualizarResumen() {
    const lista = [...seleccion].sort(cmpButacas);
    const n = lista.length;
    chipsSeleccion.replaceChildren(
      ...(n
        ? lista.map((b) => h('span', { class: 'chip chip-seat' }, b))
        : [h('span', { class: 'muted small' }, 'Ninguna butaca seleccionada')]),
    );
    total.textContent = eur((precioCent * n) / 100);
    botonReservar.disabled = n === 0;
    botonReservar.textContent = n
      ? `Reservar ${n} ${n === 1 ? 'butaca' : 'butacas'} · ${eur((precioCent * n) / 100)}`
      : 'Elige tus butacas';
    const libres = sala.filas * sala.columnas - ocupadas.size;
    libresTexto.textContent = `${libres} de ${sala.filas * sala.columnas} butacas libres`;
  }

  async function refrescar({ avisar = false } = {}) {
    const nueva = await api.butacas(id);
    ocupadas = new Set(nueva.ocupadas);
    const perdidas = [...seleccion].filter((b) => ocupadas.has(b));
    perdidas.forEach((b) => seleccion.delete(b));
    construirMapa();
    actualizarResumen();
    if (avisar && perdidas.length) {
      toast(`Se han ocupado mientras elegías: ${perdidas.sort(cmpButacas).join(', ')}`, 'error');
    }
    return perdidas;
  }

  const form = h('form', { class: 'summary', novalidate: true });
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    showAlert(error, '');
    [inputNombre, inputEmail].forEach((i) => i.removeAttribute('aria-invalid'));

    const nombre = inputNombre.value.trim();
    const email = inputEmail.value.trim();
    if (!seleccion.size) return showAlert(error, 'Selecciona al menos una butaca.');
    if (!nombre) {
      inputNombre.setAttribute('aria-invalid', 'true');
      inputNombre.focus();
      return showAlert(error, 'Escribe tu nombre.');
    }
    if (!inputEmail.checkValidity() || !email) {
      inputEmail.setAttribute('aria-invalid', 'true');
      inputEmail.focus();
      return showAlert(error, 'Escribe un email válido.');
    }

    botonReservar.disabled = true;
    botonReservar.textContent = 'Reservando…';
    try {
      const reserva = await api.crearReserva({
        sesion_id: id,
        butacas: [...seleccion].sort(cmpButacas),
        email,
        nombre,
      });
      guardarCliente({ nombre, email });
      toast('¡Reserva confirmada!', 'success');
      location.hash = `#/reserva/${encodeURIComponent(reserva.id)}`;
    } catch (err) {
      showAlert(error, err.message);
      if (err.status === 409) {
        try { await refrescar({ avisar: true }); } catch { /* el aviso ya está visible */ }
      } else {
        actualizarResumen();
      }
    }
  });

  form.append(
    h('h2', {}, 'Tu selección'),
    chipsSeleccion,
    h('div', { class: 'total-row' }, h('span', {}, 'Total'), total),
    field('Nombre', inputNombre),
    field('Email', inputEmail, 'Con tu email podrás consultar la reserva en «Mis reservas».'),
    error,
    botonReservar,
  );

  const leyenda = h(
    'ul',
    { class: 'legend', 'aria-label': 'Leyenda' },
    h('li', {}, h('span', { class: 'seat sample' }), 'Libre'),
    h('li', {}, h('span', { class: 'seat sample selected' }), 'Seleccionada'),
    h('li', {}, h('span', { class: 'seat sample taken' }), 'Ocupada'),
  );

  construirMapa();
  actualizarResumen();

  return h(
    'div',
    { class: 'container page' },
    volver,
    cabecera,
    h(
      'div',
      { class: 'booking' },
      h(
        'section',
        { class: 'panel', 'aria-label': 'Mapa de butacas' },
        h(
          'div',
          { class: 'panel-head' },
          h('h2', {}, `Sala ${sala.numero}`),
          libresTexto,
          h('button', {
            class: 'btn btn-ghost btn-sm',
            type: 'button',
            onclick: async (e) => {
              e.currentTarget.disabled = true;
              try { await refrescar({ avisar: true }); toast('Disponibilidad actualizada'); }
              catch (err) { toast(err.message, 'error'); }
              e.currentTarget.disabled = false;
            },
          }, 'Actualizar'),
        ),
        h('div', { class: 'screen', 'aria-hidden': 'true' }, h('span', {}, 'PANTALLA')),
        h('div', { class: 'seatmap-wrap' }, mapa),
        leyenda,
      ),
      form,
    ),
  );
}
