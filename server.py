#!/usr/bin/env python3
"""
Server-ponte per l'installazione Sciuscella.

Fa due cose:
  1. Serve i file statici (come `python -m http.server`)
  2. Fa da relay tra finestra operatore (Mac) e finestra proiezione
     (proiettore Android), che stanno su dispositivi diversi:
        - operatore  → POST /state  (invia le scie, ~30 volte/sec)
        - proiezione → GET  /state  (legge le scie, ~30 volte/sec)

Solo libreria standard, nessuna installazione. Avvio:
    python3 server.py
Ascolta su 0.0.0.0:8000 → raggiungibile sia da 127.0.0.1 (Mac) sia
dall'IP di rete (proiettore).
"""

import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

PORT = 8000

# Stato condiviso in memoria: l'ultimo "frame" di scie inviato dall'operatore.
state = {
    "frame": 0,        # contatore frame (cresce a ogni invio operatore)
    "stamps": [],      # [{id, nx, ny, nr}] coordinate normalizzate 0..1
    "clearSeq": 0,     # bump quando l'operatore preme Clear
    "revealSeq": 0,    # bump quando l'operatore preme Reveal
    "calib": 0,        # 1 = modalità calibrazione (proiezione mostra gli angoli)
}


class Handler(SimpleHTTPRequestHandler):
    # Silenzia il log: a 30Hz POST+GET intaserebbe il terminale
    def log_message(self, *args):
        pass

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self):
        if self.path.split("?")[0] == "/state":
            body = json.dumps(state).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-store")
            self._cors()
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        # altrimenti servi i file statici normalmente
        super().do_GET()

    def do_POST(self):
        if self.path.split("?")[0] == "/state":
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length) if length else b"{}"
            try:
                incoming = json.loads(raw.decode("utf-8"))
                # aggiorna lo stato condiviso
                state["frame"] = incoming.get("frame", state["frame"])
                state["stamps"] = incoming.get("stamps", [])
                state["clearSeq"] = incoming.get("clearSeq", state["clearSeq"])
                state["revealSeq"] = incoming.get("revealSeq", state["revealSeq"])
                state["calib"] = incoming.get("calib", state["calib"])
            except (ValueError, KeyError):
                pass
            self.send_response(200)
            self._cors()
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        self.send_response(404)
        self.end_headers()


if __name__ == "__main__":
    httpd = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"Server-ponte Sciuscella su http://0.0.0.0:{PORT}")
    print(f"  Mac (operatore):  http://127.0.0.1:{PORT}/prova2-persone-blob.html")
    print(f"  Proiettore:       http://<IP-del-mac>:{PORT}/p.html?proj=1")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer fermato.")
