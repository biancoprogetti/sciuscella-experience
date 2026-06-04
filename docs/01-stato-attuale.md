# Stato attuale del progetto

Data: 2026-06-04

## Inventario file

| File | Stato | Ruolo |
|---|---|---|
| `index.html` | attivo | Prototipo originale: reveal con mano singola sopra testi inglesi PD che scorrono |
| `prova2.html` | attivo | Evoluzione editoriale: blocchi colorati con citazioni italiane, 8fps, grana, ticker |
| `prova2.html.bak` | backup | Versione precedente di `prova2.html` |
| `typeset.html` | attivo | Generatore tipografico standalone — il "manifesto". Nessuna camera, nessun reveal |
| `mistaker.html` | sperimentale | Esperimento staccato 10fps con forme piatte. Non usa camera |
| `tipo.html` | sperimentale | Esperimento parole-particella interattive con mouse |

I tre file rilevanti per la nuova direzione sono: **`index.html`**, **`prova2.html`** (per il meccanismo di reveal con camera) e **`typeset.html`** (per il contenuto da rivelare).

---

## Architettura del meccanismo di reveal (`index.html` / `prova2.html`)

### Modello a layer

Il canvas finale è composto da più layer offscreen:

```
┌───────────────────────────────────────────────┐
│  canvas principale (composito visibile)       │
│  ┌─────────────────────────────────────────┐  │
│  │  textLayer  — tipografia generata        │  │
│  └─────────────────────────────────────────┘  │
│  ┌─────────────────────────────────────────┐  │
│  │  maskLayer  — velo opaco color pagina    │  │
│  │             ↑ cancellato dove passa mano │  │
│  └─────────────────────────────────────────┘  │
│  ┌─────────────────────────────────────────┐  │
│  │  grainLayer (solo prova2) — texture       │  │
│  └─────────────────────────────────────────┘  │
└───────────────────────────────────────────────┘
```

Ogni frame:
1. Il `textLayer` viene aggiornato (animazioni del testo)
2. Il `maskLayer` viene cancellato localmente dove la mano è passata (cumulativo, non si rigenera)
3. Il canvas finale fa `drawImage(textLayer)` poi `drawImage(maskLayer)` — il testo si vede solo dove il velo è stato bucato

### Tracking della mano

Libreria: **MediaPipe Hands 0.4** + `camera_utils` (CDN jsdelivr).

```js
var hands = new Hands({
  locateFile: f => 'https://cdn.jsdelivr.net/npm/@mediapipe/hands/' + f
});
hands.setOptions({
  maxNumHands: 1,                  // UNA mano sola
  modelComplexity: 1,
  minDetectionConfidence: 0.7,
  minTrackingConfidence: 0.5
});
hands.onResults(callback);
new Camera(video, { onFrame: () => hands.send({ image: video }),
                    width: 1280, height: 720 }).start();
```

Nel callback:
- Si prende `landmarks[8]` — punta dell'indice
- Coordinate normalizzate [0,1] → moltiplicate per `W,H`
- **Flip orizzontale**: `(1 - x)` perché la webcam frontale è specchio (selfie mode)

### Cancellazione del velo

```js
function stampErase(x, y) {
  mCtx.globalCompositeOperation = 'destination-out';
  // gradiente radiale: alpha 0.22 al centro → 0 al bordo
  var g = mCtx.createRadialGradient(x, y, 0, x, y, ERASER_R);  // ERASER_R = 38
  g.addColorStop(0, 'rgba(0,0,0,0.22)');
  g.addColorStop(1, 'rgba(0,0,0,0)');
  mCtx.fillStyle = g;
  mCtx.beginPath();
  mCtx.arc(x, y, ERASER_R, 0, Math.PI*2);
  mCtx.fill();
}
```

Interpolazione fra `lastErasePos` e nuovo punto, step `ERASER_R * 0.4`, per evitare buchi nella scia durante movimenti veloci.

Salvataggio array `handPath = [{x,y}, ...]` con `null` come marker di lift (mano persa). Usato solo per export SVG.

### Contenuto generato sotto

**`index.html`**: 4 testi PD inglesi (Alice in Wonderland, Moby-Dick, Metamorphosis, Hamlet). Renderizzati come righe orizzontali tipo ticker, font size variabile (10-28 px), velocità diverse, "glitch" di transizione ogni 40s.

**`prova2.html`**: ~30 frasi PD italiane (Dante, Petrarca, Leopardi, Pirandello, ecc.) impaginate in blocchi colorati. 5 colori (rosso, rosa, giallo, menta, azzurro). Font cycle su 16 Google Fonts (serif + sans). Layout a colonne che si aprono/chiudono. Warp "Arco Verticale" sul testo. 8fps + grana fine sopra tutto.

### Export

- **SVG**: ricostruisce il `handPath` come `<path d="M... L... L...">`, esporta file scaricabile
- **A4 PNG trasparente** (solo `prova2.html`): rasterizza la composizione visibile, scala per stampa A4

---

## Architettura di `typeset.html` (il "manifesto")

### Modello

Canvas singolo full-screen, render per tick a 10fps (`setInterval(tick, 100)`). **Nessun layer mask, nessun reveal.** Il manifesto è sempre visibile.

```
┌───────────────────────────────────────────────┐
│  canvas — bande tipografiche                  │
│  ─────────────────────────────────────────    │
│  HERO (parola gigante clippata)               │
│  TICKER (testo che scorre)                    │
│  GRID (parola tessuta come pattern)            │
│  VERTICAL (lettere impilate)                  │
│  STRIPE (banda di colore piena)               │
└───────────────────────────────────────────────┘
```

Ogni tick:
1. Sceglie N bande (slider, 2-12)
2. Per ognuna, una tipologia in base all'altezza
3. Compone tutta la scena da zero — nessuna continuità tra frame

### UI (pannello liquid glass)

- **Textarea** per parole utente (default: "NOTHING / MORE / TO / SAY"). Comma o newline = nuova voce
- **Slider**: FPS (2-10), Bands (2-12), Force (40-180, overflow hero), Chaos (0-100), Palette
- **Palette strip**: 4 strict 2-colori
  - 01: bianco/nero
  - 02: nero/bianco
  - 03: `#E8E8E6` / `#00AAEE` (colori del sito danielbianco.net)
  - 04: invertita
- **Format selector**: FULL / 9:16 / 16:9 (il canvas si ridimensiona, body dark intorno)
- **Buttons**: PAUSE (Spazio), SHUFFLE (S), PNG (P), HIDE (H)
- **SHOW** button + tasto H quando pannello nascosto

### Cosa MANCA in `typeset.html` per integrarsi

- Nessun input camera
- Nessun layer maschera reveal
- Nessuna gestione multi-utente
- Nessun concetto di "permanenza" della scia (ricomporrebbe a ogni tick)

---

## Quadro tecnico riassuntivo

| Aspetto | `index.html` / `prova2.html` | `typeset.html` |
|---|---|---|
| Camera | MediaPipe Hands (1 mano) | nessuna |
| FPS | 30 (index) / 8 (prova2) | 10 |
| Layer maschera | sì, cumulativa | no |
| Reveal | sì, via cancellazione velo | no |
| Multi-utente | no | n/a |
| Contenuto | testi PD letterari | parole utente |
| Pannello controllo | minimale (3-4 bottoni) | completo (sliders + palette) |
| Export | SVG path, PNG A4 | PNG singolo |
| Calibrazione | mirror flip selfie | n/a |

---

## Dipendenze esterne

| Libreria | Versione | Da CDN | Usata in |
|---|---|---|---|
| `@mediapipe/hands` | latest | jsdelivr | index, prova2 |
| `@mediapipe/camera_utils` | latest | jsdelivr | index, prova2 |
| Google Fonts | — | googleapis | prova2 (16 font) |
| nessuna | — | — | typeset (vanilla, solo Helvetica di sistema) |
