// Utilidades compartidas: DOM, fechas, formato, avisos y diálogos.

// ---------- DOM ----------
// h('div', {class: 'x', onclick: fn}, 'texto', otroNodo). Nunca usa innerHTML,
// así que nada de lo que venga de la API puede inyectar HTML.
export function h(tag, attrs, ...children) {
  const el = document.createElement(tag);
  let value;
  let hasValue = false;
  for (const [key, val] of Object.entries(attrs || {})) {
    if (val === null || val === undefined || val === false) continue;
    if (key === 'class') el.className = val;
    else if (key === 'dataset') Object.assign(el.dataset, val);
    else if (key === 'value') { value = val; hasValue = true; }
    else if (key.startsWith('on') && typeof val === 'function') el.addEventListener(key.slice(2).toLowerCase(), val);
    else if (['checked', 'selected', 'disabled', 'hidden'].includes(key)) el[key] = val;
    else el.setAttribute(key, val === true ? '' : String(val));
  }
  append(el, children);
  if (hasValue) el.value = value; // después de crear las <option> de un <select>
  return el;
}

export function append(el, children) {
  for (const child of children.flat(Infinity)) {
    if (child === null || child === undefined || child === false || child === true) continue;
    el.append(child instanceof Node ? child : document.createTextNode(String(child)));
  }
  return el;
}

export function setTitle(title) {
  document.title = title ? `${title} · Web Cine` : 'Web Cine · Reserva de entradas';
}

// ---------- Fechas ----------
// La API devuelve fechas "ingenuas" (hora local del cine, sin zona): 2027-01-15T18:00:00
export function parseDate(value) {
  return new Date(String(value).replace(/(\.\d{3})\d+/, '$1'));
}

const fmt = (opts) => new Intl.DateTimeFormat('es-ES', opts);
const fDia = fmt({ weekday: 'long', day: 'numeric', month: 'long' });
const fCorto = fmt({ weekday: 'short', day: 'numeric', month: 'short' });
const fHora = fmt({ hour: '2-digit', minute: '2-digit' });
const fCompleta = fmt({ weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' });
const fFechaHora = fmt({ day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' });
const fMoneda = new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' });

export const cap = (s) => s.charAt(0).toUpperCase() + s.slice(1);
export const eur = (n) => fMoneda.format(n);
export const hora = (d) => fHora.format(d);
export const diaLargo = (d) => cap(fDia.format(d));
export const diaCompleto = (d) => cap(fCompleta.format(d));
export const fechaHora = (d) => fFechaHora.format(d);

const pad = (n) => String(n).padStart(2, '0');
export const dayKey = (d) => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
export const toInputValue = (d) => `${dayKey(d)}T${pad(d.getHours())}:${pad(d.getMinutes())}`;

export function etiquetaRelativa(d) {
  const hoy = new Date();
  const manana = new Date();
  manana.setDate(hoy.getDate() + 1);
  if (dayKey(d) === dayKey(hoy)) return 'Hoy';
  if (dayKey(d) === dayKey(manana)) return 'Mañana';
  return '';
}

export function diaCorto(d) {
  return etiquetaRelativa(d) || cap(fCorto.format(d));
}

export function duracion(min) {
  if (min < 60) return `${min} min`;
  const horas = Math.floor(min / 60);
  const resto = min % 60;
  return resto ? `${horas} h ${resto} min` : `${horas} h`;
}

// ---------- Butacas ----------
export function parseButaca(id) {
  const m = /^([A-Z]+)(\d+)$/.exec(id);
  return { fila: m ? m[1] : id, num: m ? Number(m[2]) : 0 };
}

export function cmpButacas(a, b) {
  const x = parseButaca(a);
  const y = parseButaca(b);
  return x.fila.localeCompare(y.fila) || x.num - y.num;
}

export const nombreButaca = (id) => {
  const { fila, num } = parseButaca(id);
  return `Fila ${fila} · Butaca ${num}`;
};

// ---------- Carteles generados (la API no tiene imágenes) ----------
function hue(str) {
  let x = 0;
  for (const c of str) x = (x * 31 + c.charCodeAt(0)) >>> 0;
  return x % 360;
}

export function posterStyle(nombre, genero) {
  const base = hue(`${nombre}|${genero}`);
  return `background: linear-gradient(155deg, hsl(${base} 58% 34%), hsl(${(base + 48) % 360} 62% 13%))`;
}

export function iniciales(nombre) {
  const palabras = nombre.trim().split(/\s+/).filter(Boolean);
  const texto = palabras.length > 1 ? palabras[0][0] + palabras[1][0] : nombre.trim().slice(0, 2);
  return texto.toUpperCase();
}

// ---------- Avisos y diálogos ----------
export function toast(message, type = 'info') {
  const box = document.getElementById('toasts');
  const el = h('div', { class: `toast toast-${type}` }, message);
  box.append(el);
  setTimeout(() => {
    el.classList.add('out');
    setTimeout(() => el.remove(), 300);
  }, type === 'error' ? 7000 : 4000);
}

export function openDialog({ title, body, onClose }) {
  const dlg = h(
    'dialog',
    { class: 'dialog', 'aria-labelledby': 'dlg-title' },
    h(
      'div',
      { class: 'dialog-head' },
      h('h2', { id: 'dlg-title' }, title),
      h('button', { class: 'icon-btn', type: 'button', 'aria-label': 'Cerrar', onclick: () => dlg.close() }, '×'),
    ),
    h('div', { class: 'dialog-body' }, body),
  );
  dlg.addEventListener('close', () => {
    dlg.remove();
    onClose?.();
  });
  dlg.addEventListener('click', (e) => {
    if (e.target === dlg) dlg.close(); // clic en el fondo
  });
  document.body.append(dlg);
  dlg.showModal();
  return dlg;
}

export function confirmDialog({ title, message, confirmLabel = 'Confirmar', danger = false }) {
  return new Promise((resolve) => {
    let result = false;
    const dlg = openDialog({
      title,
      onClose: () => resolve(result),
      body: h(
        'div',
        {},
        h('p', {}, message),
        h(
          'div',
          { class: 'actions' },
          h('button', { class: 'btn btn-ghost', type: 'button', onclick: () => dlg.close() }, 'Cancelar'),
          h('button', {
            class: `btn ${danger ? 'btn-danger' : 'btn-primary'}`,
            type: 'button',
            onclick: () => { result = true; dlg.close(); },
          }, confirmLabel),
        ),
      ),
    });
  });
}

// ---------- Almacenamiento local (datos del cliente) ----------
const CLAVE_CLIENTE = 'cine.cliente';

export function leerCliente() {
  try {
    return JSON.parse(localStorage.getItem(CLAVE_CLIENTE)) ?? {};
  } catch {
    return {};
  }
}

export function guardarCliente(cliente) {
  try {
    localStorage.setItem(CLAVE_CLIENTE, JSON.stringify(cliente));
  } catch {
    /* modo privado: no pasa nada */
  }
}
