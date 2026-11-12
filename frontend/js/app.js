// Punto de entrada: enrutador por hash (#/...) y gestión de errores de carga.
import { errorState, loading } from './components.js';
import { cartelera } from './views/cartelera.js';
import { gestionView } from './views/gestion.js';
import { misReservasView } from './views/misreservas.js';
import { peliculaView } from './views/pelicula.js';
import { reservaView } from './views/reserva.js';
import { sesionView } from './views/sesion.js';
import { setTitle } from './utils.js';

// [expresión, vista, opción activa del menú]
const RUTAS = [
  [/^#\/?$/, cartelera, 'cartelera'],
  [/^#\/pelicula\/([^/]+)$/, peliculaView, 'cartelera'],
  [/^#\/sesion\/([^/]+)$/, sesionView, 'cartelera'],
  [/^#\/reserva\/([^/]+)$/, reservaView, 'reservas'],
  [/^#\/reservas$/, misReservasView, 'reservas'],
  [/^#\/gestion(?:\/([^/]+))?$/, gestionView, 'gestion'],
];

const main = document.getElementById('main');
let token = 0;

function marcarMenu(clave) {
  document.querySelectorAll('nav a[data-route]').forEach((a) => {
    if (a.dataset.route === clave) a.setAttribute('aria-current', 'page');
    else a.removeAttribute('aria-current');
  });
}

async function render() {
  const mio = ++token;
  const hash = location.hash || '#/';
  const ruta = RUTAS.find(([re]) => re.test(hash));

  if (!ruta) {
    marcarMenu('');
    setTitle('Página no encontrada');
    main.replaceChildren(errorState({ status: 404, message: 'Esta página no existe.' }, render));
    return;
  }

  const [re, vista, clave] = ruta;
  const args = hash.match(re).slice(1).map((x) => (x ? decodeURIComponent(x) : x));
  marcarMenu(clave);
  main.replaceChildren(loading());

  let contenido;
  try {
    contenido = await vista(...args);
  } catch (err) {
    contenido = errorState(err, render);
    setTitle('Error');
  }
  if (mio !== token) return; // el usuario ya ha navegado a otra pantalla
  main.replaceChildren(contenido);
  window.scrollTo({ top: 0 });
  main.focus({ preventScroll: true });
}

window.addEventListener('hashchange', render);
render();
