# Evoluzione: installazione con camera dall'alto

Data: 2026-06-04

## Obiettivo

Trasformare il sistema da **prototipo desktop con mano singola davanti a webcam frontale** a **installazione live con camera zenitale**, dove:

1. La fotocamera è montata sopra una zona di calpestio, riprende il pavimento dall'alto
2. Più persone si muovono nell'area
3. Ogni persona ha una propria scia che cancella un velo
4. Sotto al velo c'è il manifesto generato da `typeset.html`
5. Camminando, le persone "rivelano" pezzi del manifesto

## Differenze chiave rispetto allo stato attuale

| Aspetto | Ora | Target |
|---|---|---|
| Camera | frontale, selfie | zenitale, planimetrica |
| Soggetto tracciato | mano (5 dita) | persone intere viste da sopra |
| Numero soggetti | 1 | N (3-10) |
| Identità nel tempo | non serve (1 sola mano) | **ID persistente per ogni persona** |
| Contenuto rivelato | testi PD scrolling / blocchi citazioni | manifesto generato da typeset |
| Mirror flip | sì (`1-x`) | no (vista dall'alto non è specchio) |
| Pannello UI | sempre visibile | nascosto durante la live |

---

## Decisioni critiche (con raccomandazione)

### 1. Algoritmo di tracking persone dall'alto

Le opzioni e i trade-off:

#### a) Frame differencing + blob tracking *(minimal, vanilla)*
- **Come**: confronto pixel tra frame consecutivi → soglia luminanza → connected components → centroidi
- **Pro**: zero librerie, nativo browser, leggerissimo, funziona su qualsiasi hardware. Dall'alto una persona = un blob compatto pulito
- **Contro**: persona ferma scompare (no movimento = no diff). Soluzione: background subtraction (modello a media mobile o MoG2)
- **Costo dev**: ~50 righe JS

#### b) MoveNet MultiPose (TensorFlow.js) *(raccomandato)*
- **Come**: ML su GPU via WebGL, fino a 6 persone, 17 keypoint ciascuna
- **Dall'alto**: usiamo solo il keypoint #0 (testa). Torso/gambe spesso falliscono dall'alto, ma la testa si vede sempre
- **Pro**: stabile su persone ferme, ID assistito, fps decente (15-25 su Mac/portatile recente)
- **Contro**: ~3MB di modello da scaricare; serve GPU/WebGL
- **Costo dev**: ~80 righe JS + setup TFJS

#### c) COCO-SSD / YOLO via TFJS
- **Come**: detection di bounding box "person"
- **Pro**: molto robusto
- **Contro**: pesante (~30MB), latenza alta, overkill per il caso d'uso

> **Raccomandazione**: **(b) MoveNet MultiPose**. Se le performance in target sono un problema, fallback a (a) blob tracking.

### 2. ID persistente per multi-persona

Le detection di un singolo frame sono anonime: una lista `[{x, y, conf}, ...]`. Per dare a ogni persona la SUA scia stabile servono ID che sopravvivono ai frame.

**Algoritmo proposto**: **greedy nearest-neighbor tracker** (semplice e sufficiente per <10 persone)
- Ad ogni frame: per ogni track esistente, trova la detection più vicina entro raggio `MAX_MATCH_DIST`
- Detection non matchate → nuovi track (nasceranno dopo `BIRTH_FRAMES` di conferma)
- Track senza match per `DEATH_FRAMES` → eliminati

> Hungarian sarebbe ottimale ma overkill per <10 persone. Skip.

```js
// Struttura
tracks = {
  3: { id: 3, x, y, lastSeen, trail: [...], color: hue3 },
  7: { id: 7, x, y, lastSeen, trail: [...], color: hue7 },
  ...
}
```

### 3. Identità visiva della scia

Vogliamo che le scie siano distinguibili tra loro?

- **A) Anonime**: tutte cancellano allo stesso modo, l'osservatore non distingue chi è chi. Mantiene la disciplina 2-colori del manifesto
- **B) Colorate per ID**: ogni persona ha la sua tinta nella scia. Rompe però i 2-colori del manifesto sottostante

> **Raccomandazione**: **(A) anonime**. Le persone si distinguono per movimento e posizione, non per colore. Estetica più pulita, fedele al typeset. Il "fatto" che siano persone diverse è implicito nel comportamento delle scie (non si fondono in una sola).

### 4. Velo: rivelazione permanente o si "guarisce"?

- **Permanente**: una volta cancellato, sempre rivelato → dopo qualche minuto tutto il velo è bucato e il manifesto è visibile per intero (interesse cala)
- **Decay temporale**: dopo X secondi senza nuove cancellazioni in un'area, il velo si "richiude" lentamente in quella zona → l'installazione resta interessante in eterno

> **Raccomandazione**: **decay graduale**. Ogni N secondi (parametrizzabile) un layer di velo viene re-dipinto con alpha basso sopra il maskLayer → riempie pian piano i buchi inattivi. Le aree calpestate frequentemente restano sempre aperte.

### 5. Manifesto dinamico o statico?

Il `typeset.html` rigenera la composizione a 10fps. Lasciato così, mentre uno cammina il contenuto sotto cambia.

- **Dinamico** (10fps come ora): la scia rivela qualcosa che cambia → effetto "non riesco mai a leggere"
- **Statico** per sessione: una volta generato, resta fisso. La scia svela qualcosa di stabile
- **Lento** (1 cambio ogni 30-60s): via di mezzo. Composizione resta abbastanza per leggerla, poi si trasforma

> **Raccomandazione**: **lento**. 1 cambio ogni 30-60s rispetta l'estetica dei cut ma permette la rivelazione progressiva. Le animazioni che dipendono da `frame++` per scorrere (ticker, grid) possono continuare a girare a 10fps senza ricomposizione.

### 6. Calibrazione camera ↔ canvas

- **1:1**: la coordinata camera (1280×720) viene scalata al canvas. Funziona se la camera vede esattamente l'area utile. Semplice
- **4-point perspective transform**: l'utente clicca 4 angoli dell'area di calpestio nella vista camera, e si calcola una matrice 3×3 di trasformazione prospettica → i centroidi tracciati vengono "raddrizzati" sull'area canvas. Necessario se la camera non è perfettamente perpendicolare o se l'area è un trapezio nella vista

> **Raccomandazione**: **iniziare con 1:1**. Aggiungere calibrazione 4-punti in fase 2 se serve.

---

## Architettura proposta

```
┌──────────────────────────────────────────────────────────┐
│ <video> camera zenitale (hidden)                         │
└──────────┬───────────────────────────────────────────────┘
           │ frame
           ▼
┌────────────────────────────┐
│ MoveNet MultiPose          │ → [{x, y, confidence}, ...]
│ (TFJS, GPU/WebGL)          │   (solo keypoint testa)
└──────────┬─────────────────┘
           │
           ▼
┌────────────────────────────┐
│ Greedy NN Tracker          │ → tracks {id → {trail, lastSeen, ...}}
│ (birth/death lifecycle)    │
└──────────┬─────────────────┘
           │ per ogni track con detection corrente
           ▼
┌────────────────────────────┐   ┌──────────────────────────────┐
│ maskLayer (offscreen)      │   │ textLayer (offscreen)        │
│ stampErase(x,y) per ogni   │   │ typeset bands               │
│ track attivo               │   │ ricomposto raramente         │
│ + decay layer alpha basso  │   │ (1× ogni 30-60s)             │
└──────────┬─────────────────┘   └──────────┬───────────────────┘
           │                                │
           ▼                                ▼
        ┌──────────────────────────────────────┐
        │ canvas finale                        │
        │ drawImage(textLayer)                 │
        │ drawImage(maskLayer)                 │
        └──────────────────────────────────────┘
```

---

## Piano di implementazione (fasi)

### Fase 0 — Setup
- Nuovo file `installazione.html` come fork di `typeset.html`
- Mantiene tutto il rendering tipografico, pannello, palette
- Cambio: rallenta i tick di ricomposizione a 1 ogni 30s (slider o config)

### Fase 1 — Velo + reveal con MOUSE
- Aggiungi `maskLayer` opaco color palette[0] sopra le bande
- Mouse move → `stampErase(x, y)` (stesso meccanismo di `prova2.html`)
- Verifica visiva: la rivelazione è leggibile su tutte le palette?
- Decidi alpha del velo (0.85? 0.95?)
- Decidi ERASER_R (38 forse troppo piccolo per camera dall'alto su tutto schermo)

### Fase 2 — Singola persona via webcam
- Sostituisci mouse con MoveNet single-pose
- Test reale con persona vista dall'alto
- Calibra: alpha velo, raggio gomma, soglia confidence keypoint

### Fase 3 — Multi-persona
- MoveNet MultiPose, `maxPoses: 6`
- Implementa `tracker.update(detections)` con ID stabili (greedy NN)
- Per ogni track attivo: `stampErase(track.x, track.y)`
- Visualizzazione debug (cerchi numerati sui centroidi) — solo in setup mode

### Fase 4 — Decay del velo
- Ogni N frame, ridipingi `maskLayer` con un layer di velo `alpha = DECAY_RATE`
- Parametro nel pannello: DECAY (slider 0=mai, 100=veloce)
- Test estetico: le zone "in transito" restano sempre aperte, le zone trascurate si chiudono in 30-60s

### Fase 5 — Modalità installazione
- Tasto **GO LIVE** che:
  - Nasconde pannello + readout
  - Mette canvas full-screen senza margini
  - Disattiva tutti i cursori
  - Pulisce log/console
- Tasto **Esc** per uscire dalla modalità live

### Fase 6 — Calibrazione 4-punti (opzionale, se serve)
- Modalità "calibra" — mostra il feed camera + 4 marker draggable
- Salva i 4 angoli in `localStorage`
- Calcola matrice perspective transform (cv2-style 3×3)
- Trasforma ogni detection prima di passarla al tracker

### Fase 7 — Refinement per live (opzionale)
- Soglia movimento minima (ignora drift di tracking)
- Smoothing della traiettoria (filtro esponenziale o Kalman)
- Logging eventi (n. persone medie, durata sessione)
- Auto-restart in caso di crash camera

---

## Open questions (decisioni da prendere prima di partire)

1. **Manifesto sotto: dinamico, statico per sessione, o lento (1 cambio ogni 30-60s)?**
2. **Decay del velo: attivo? Con che tempistica?**
3. **Colore scia: anonimo come raccomandato, o ID colorato?**
4. **Hardware target**: che computer girerà l'installazione (Mac mini? PC con GPU? Raspberry?)
5. **Camera fisica**: USB webcam, GoPro, IP camera? Risoluzione disponibile?
6. **Spazio fisico**: dimensioni area calpestabile? Altezza camera? Lunghezza ottica?
7. **Massimo persone attese simultaneamente?** (3, 6, 10+)
8. **Calibrazione**: dal giorno 1 o in fase 2 dopo i primi test?
9. **Manifesto: testo fisso definito a priori, o ancora configurabile da textarea?**
10. **Dove va il computer/cavo durante l'installazione?** Influenza UI (es. serve tasto fisico o remoto?)

---

## Rischi tecnici noti

| Rischio | Probabilità | Mitigazione |
|---|---|---|
| MoveNet fps insufficienti dall'alto | media | fallback a blob tracking (frame diff) |
| Persone ferme che "scompaiono" dal tracking | alta | preferire MoveNet su blob tracking. Background subtraction se si va su blob |
| ID swap tra persone vicine | media | aumentare `MAX_MATCH_DIST` se serve; in pratica con scia anonima non è un problema visibile |
| Webcam frontale vs camera USB esterna | bassa | API è la stessa (`getUserMedia`), eventualmente UI per selezione device |
| Lag visibile tra movimento e scia | media | minimizzare lavoro per frame; rendering bande in worker se serve |
| Memoria che cresce (trails infiniti) | alta | limitare lunghezza trail (es. ultimi 200 punti) o non salvare l'array, solo il maskLayer cumulativo |
| Background luminoso variabile (luce ambientale) | alta per blob tracking | usare MoveNet che è meno sensibile |

---

## Cosa NON va cambiato

Per scelta:
- L'estetica del manifesto (`typeset.html` rendering) resta uguale
- Le 4 palette restano (per ora)
- Il modello a layer (text + mask compositing) di `prova2.html` è già perfetto, lo riusiamo identico
- L'effetto `stampErase` con gradiente radiale `destination-out` resta uguale (è già ottimo)

---

## Checklist pre-implementazione

Prima di scrivere `installazione.html`, mi servono le risposte alle Open Questions, in particolare:

- [ ] Manifesto: dinamico / statico / lento?
- [ ] Decay velo: sì/no/parametro?
- [ ] Hardware + camera target
- [ ] Spazio fisico (altezza camera, area)
- [ ] Max persone simultanee
- [ ] Quando posso testare con una camera vera dall'alto?
