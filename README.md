# Sciuscella Experience

Esperimenti tipografici interattivi per un'installazione di rivelazione del manifesto **Sciuscella**.

## File principali

| File | Descrizione | Apri in browser |
|---|---|---|
| [`typeset.html`](typeset.html) | Generatore tipografico del manifesto. Bande a 10fps, sliders, palette, formato 9:16 / 16:9. Pannello "liquid glass" in inglese. Standalone, niente camera. | doppio click |
| [`prova2.html`](prova2.html) | Reveal interattivo: tracking mano (MediaPipe Hands) che cancella un velo per scoprire blocchi di citazioni italiane. 8fps + grana. Export SVG e A4 PNG. | richiede webcam |
| [`index.html`](index.html) | Primo prototipo reveal: una mano cancella il velo sopra testi PD inglesi che scorrono. | richiede webcam |

## Documentazione

- [`docs/01-stato-attuale.md`](docs/01-stato-attuale.md) — Architettura attuale dei tre prototipi
- [`docs/02-evoluzione.md`](docs/02-evoluzione.md) — Piano di evoluzione verso installazione con camera dall'alto e multi-persona

## Esperimenti archiviati

In [`old/`](old/) ci sono prototipi precedenti (`mistaker.html`, `tipo.html`, backup di `prova2`).

## Setup

Niente build, niente dipendenze locali. Apri i file `.html` in Chrome/Safari. Per i file che usano la webcam (`index.html`, `prova2.html`) serve un browser moderno con accesso camera consentito.

## Stack

- HTML/CSS/JS vanilla
- [MediaPipe Hands](https://google.github.io/mediapipe/solutions/hands.html) via CDN per il tracking mano
- Google Fonts (solo `prova2.html`)
- Helvetica/Helvetica Neue di sistema per `typeset.html`
