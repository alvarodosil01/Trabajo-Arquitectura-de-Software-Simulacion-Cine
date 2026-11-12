#!/usr/bin/env python3
"""Servidor local para el frontend (sin dependencias, solo la librería estándar).

Sirve los ficheros estáticos de esta carpeta y reenvía /api/* al backend, igual
que hace nginx en Docker. Así el navegador no necesita CORS.

    python serve.py                      # frontend en http://127.0.0.1:8080
    BACKEND_URL=http://127.0.0.1:8000 PORT=8080 python serve.py
"""

import json
import os
import urllib.error
import urllib.request
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

BACKEND = os.environ.get("BACKEND_URL", "http://127.0.0.1:8000").rstrip("/")
PORT = int(os.environ.get("PORT", "8080"))
HOST = os.environ.get("HOST", "127.0.0.1")
ROOT = os.path.dirname(os.path.abspath(__file__))


class Handler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store")  # en desarrollo, nunca cachear
        super().end_headers()

    def _proxy(self):
        destino = BACKEND + (self.path[len("/api"):] or "/")
        largo = int(self.headers.get("Content-Length") or 0)
        cuerpo = self.rfile.read(largo) if largo else None
        peticion = urllib.request.Request(destino, data=cuerpo, method=self.command)
        if self.headers.get("Content-Type"):
            peticion.add_header("Content-Type", self.headers["Content-Type"])
        try:
            with urllib.request.urlopen(peticion, timeout=30) as r:
                estado, datos, tipo = r.status, r.read(), r.headers.get("Content-Type")
        except urllib.error.HTTPError as e:
            estado, datos, tipo = e.code, e.read(), e.headers.get("Content-Type")
        except Exception:
            estado, tipo = 502, "application/json"
            datos = json.dumps({"detail": f"No se puede conectar con el backend en {BACKEND}"}).encode()
        self.send_response(estado)
        if tipo:
            self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(datos)))
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(datos)

    def _despachar(self, estatico):
        if self.path.startswith("/api/") or self.path == "/api":
            return self._proxy()
        return estatico()

    def do_GET(self):
        self._despachar(super().do_GET)

    def do_HEAD(self):
        self._despachar(super().do_HEAD)

    def do_POST(self):
        self._despachar(lambda: self.send_error(405))

    do_PUT = do_DELETE = do_POST

    def log_message(self, fmt, *args):
        if not self.path.startswith(("/js/", "/css/")):
            super().log_message(fmt, *args)


if __name__ == "__main__":
    servidor = ThreadingHTTPServer((HOST, PORT), partial(Handler, directory=ROOT))
    print(f"Frontend: http://{HOST}:{PORT}   (API reenviada a {BACKEND})  ·  Ctrl+C para parar")
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido.")
