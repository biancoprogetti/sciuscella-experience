# Sciuscella — Riepilogo completo del progetto

> Documento di passaggio. Serve per riprendere il lavoro o per avviare una nuova
> conversazione (anche da telefono) avendo tutto il contesto. Copialo/incollalo
> all'inizio di una chat e di' "questo è il contesto del mio progetto".

---

## 1. Cos'è il progetto

**Sciuscella** è un'**installazione interattiva** per uno spazio espositivo. Un
**manifesto tipografico** (frasi della letteratura italiana di pubblico dominio:
Dante, Leopardi, Petrarca, Pirandello…) viene **proiettato a terra** e tenuto
nascosto sotto un **velo** uniforme color pagina. Le **persone che camminano**
nell'area, viste da una **telecamera dall'alto**, **rivelano progressivamente il
testo** lasciando una scia dove passano. A fine percorso l'idea è restituire a
ciascuno un **poster personale** (frasi + la traccia del proprio movimento).

Tema di fondo: resistenza culturale, il testo che si scopre solo attraversandolo,
contro il consumo veloce.

Tutto è realizzato come **applicazione web** (HTML/CSS/JavaScript) eseguibile in
un browser, senza dipendenze installate.

---

## 2. Repository e file principali

Repo GitHub: **https://github.com/biancoprogetti/sciuscella-experience**

- `prova2-persone-blob.html` → **il file principale attuale** dell'installazione
  (tracciamento persone + rivelazione + proiezione + calibrazione).
- `p.html` → copia di `prova2-persone-blob.html` con nome corto (per il
  proiettore).
- `proj.html` → reindirizza a `p.html?proj=1` (URL facile da digitare sul
  proiettore col telecomando).
- `server.py` → piccolo **server-ponte** in Python (solo libreria standard):
  serve i file e fa da relay delle scie tra Mac e proiettore.
- `typeset.html`, `prova2.html`, `index.html` → prototipi precedenti
  (generatore tipografico, reveal con la mano). Archivio.
- `docs/01-stato-attuale.md`, `docs/02-evoluzione.md`, `docs/tesi-capitolo.md`,
  `docs/RIEPILOGO.md` (questo file) → documentazione.

---

## 3. Come funziona, in breve

### Architettura a due finestre
- **Finestra operatore** (sul Mac, URL `http://127.0.0.1:8000/prova2-persone-blob.html`):
  gestisce la telecamera, il tracciamento, i controlli, il pannello diagnostico.
- **Finestra proiezione** (sul proiettore, URL `http://<IP-del-mac>:8000/proj.html`):
  mostra **solo l'installazione pulita**, senza interfaccia.
- Comunicano via **server-ponte** (`server.py`): l'operatore invia le coordinate
  delle scie (normalizzate 0–1), la proiezione le applica. Funziona anche tra
  due dispositivi diversi sulla stessa rete WiFi.

> Importante: sul Mac usare **127.0.0.1** (la webcam funziona solo in "contesto
> sicuro"); il proiettore usa l'**IP di rete** (es. 192.168.1.5), dove la camera
> non serve.

### Tracciamento delle persone — sottrazione dello sfondo (niente IA)
Si è scelta la **background subtraction**, la tecnica classica per telecamere
fisse, dopo aver scartato i modelli di intelligenza artificiale (pose estimation
e object detection: troppi falsi positivi e identità instabili dall'alto).
- Si "fotografa" la **scena vuota** come riferimento (tasto **B** / 🎯 Sfondo).
- Ogni fotogramma viene confrontato: ciò che cambia è una **massa in movimento**
  (centroide + raggio d'ingombro).
- Accorgimenti: compensazione dell'esposizione, erosione/dilatazione per togliere
  rumore e **ricomporre un corpo frammentato**, fusione di blob vicini, soglia
  regolabile (slider SOGLIA nel diag).

### Identità persistenti
- **Conferma di nascita**: una massa riceve un ID solo dopo alcuni fotogrammi
  (il rumore non genera ID spuri).
- **Predizione del movimento**: ogni traccia ricorda la velocità; quando due
  persone si incrociano e si fondono, gli ID si mantengono e si ricollocano
  all'uscita.
- Limite noto: due corpi **fisicamente sovrapposti** non sono separabili (manca
  l'informazione nel dato RGB).

### Calibrazione (fondamentale per far cadere la scia dove passi)
- **Sfondo** (B): acquisisce la scena vuota.
- **Area / geometria** (G / ◳ Area): si trascinano **4 maniglie** sui 4 angoli
  dell'area proiettata viste nel feed della camera. Durante la calibrazione la
  proiezione mostra **4 numeri** (1=alto-sx, 2=alto-dx, 3=basso-dx, 4=basso-sx):
  si trascina la maniglia N sul numero N → corrispondenza e direzione sempre
  corrette, anche con camera ruotata. Da qui si calcola un'**omografia**
  (trasformazione prospettica) che raddrizza ogni posizione.
- **Reset angoli** (K / ↺ Angoli): rimette le maniglie ai bordi.
- L'area calibrata fa anche da **zona attiva (ROI)**: il movimento fuori
  dall'area viene ignorato (con un margine del 18% per chi è sul bordo).
- **Specchia** (M / ⇄ Specchia): ribalta sinistra/destra l'uscita, perché la
  camera dall'alto è speculare alla proiezione. L'impostazione si salva.

### Proiezione e fullscreen
- Bottone **▶/⛶ Schermo** (F) sul Mac → manda/toglie il tutto schermo sulla
  proiezione (toggle). Sul proiettore basta anche **toccare lo schermo o premere
  OK** del telecomando per entrare a tutto schermo; **Esc** per uscire.
- La calibrazione e le impostazioni (omografia, specchio) si salvano nel browser
  (localStorage), restano tra le sessioni.

---

## 4. Controlli (tasti, finestra operatore)

- **B** = calibra sfondo (esci dall'area prima di premere)
- **G** = calibra area (trascina le 4 maniglie sui numeri proiettati)
- **K** = reset dei 4 angoli
- **M** = specchia sinistra/destra
- **F** = tutto schermo proiezione (on/off)
- **C** = clear (pulisci le scie) · **R** = reveal (svela tutto)
- **D** = mostra/nascondi pannello diagnostico · **V** = cambia telecamera
- **S** = esporta SVG · **A** = esporta poster A4 · **P** = apri finestra
  proiezione di test sul Mac
- Slider **SOGLIA** nel diag = sensibilità (alta = meno sensibile)
- Il pannello diag si **ridimensiona** trascinando l'angolo in basso a sinistra.

---

## 5. Allestimento fisico attuale

- Al soffitto è montato un **cestello che regge uno smartphone** rivolto verso il
  basso, usato come **telecamera zenitale** (collegato al Mac via WiFi con l'app
  **Iriun Webcam**).
- Accanto è montato un **proiettore** (Android, con browser Brave) anch'esso al
  soffitto, orientato verso il pavimento.
- Mac e proiettore sulla **stessa rete WiFi**.

---

## 6. Problemi noti e limiti

1. **Retroazione del proiettore**: con una telecamera ottica normale, la camera
   vede anche l'immagine proiettata che si muove (ticker, animazioni) e la
   scambia per movimento di persone → falsi rilevamenti, difficoltà a fare clear.
2. **Stanza buia + esposizione automatica del telefono**: poco contrasto e
   immagine "ballerina" → tracciamento poco affidabile.
3. **Sovrapposizione di più persone**: corpi attaccati = un blob solo
   (non separabile in RGB).
4. **Lag**: parte è intrinseca al WiFi tra Mac e proiettore.

**La soluzione decisa per i punti 1–2 è passare a una telecamera a infrarossi**
(vedi sotto): l'IR non vede la proiezione e funziona al buio.

---

## 7. Prossimo passo hardware: telecamera a infrarossi (wireless)

Vincolo richiesto: **zero cavi nello spazio** (alimentazione compresa) e ponte
software accettato.

Soluzione individuata:
- **Telecamera IP WiFi da interno con visione notturna (IR) e supporto RTSP**,
  alimentata a **5V USB**. Candidato: **Reolink E1** (~50–60€).
- Alimentata da un **power bank 20.000mAh+** (~20–30€) montato accanto a lei al
  soffitto → unità autonoma, niente cavi nello spazio, ~15–20h di autonomia,
  si ricarica la notte.
- **OBS** (gratuito) sul Mac fa da **ponte**: apre lo stream RTSP della
  telecamera e lo espone come **webcam virtuale** → la nostra app la seleziona
  con **V**, codice invariato.
- L'IR integrato della camera dovrebbe bastare per illuminare i ~3×4m da ~3m di
  altezza (al tracciamento serve contrasto, non immagine perfetta).

Le telecamere **a batteria** di sorveglianza NON vanno bene: si attivano solo al
movimento e la batteria non regge lo streaming continuo. Per questo si usa una
camera "wired" 5V alimentata da power bank.

Spazio previsto: **area ~3×4m, telecamera a ~3m** di altezza.

---

## 8. Idee di interazione da valutare (per il futuro)

- **Il velo si richiude** col tempo (decadimento): l'opera non si esaurisce mai.
- **Premiare la sosta**: chi si ferma fermo apre completamente il testo sotto di
  sé (gesto contro il consumo veloce).
- **Memoria del pavimento**: sentieri consumati dove passano in molti.
- **Solo vs folla**: il manifesto reagisce alla densità di persone.
- **Incrocio tra persone**: una frase/linea compare quando due scie si toccano.
- **Voce del corpus**: la frase scoperta viene letta ad alta voce (sintesi
  vocale) quando ci si ferma.
- **Lascia una parola**: un totem dove scrivere una parola che entra nel corpus
  per i visitatori successivi (opera collettiva nel tempo).
- **Poster personale** finale (già in piano).

Le due più forti e più facili da fare ora: *velo che si richiude* e *premiare la
sosta*.

---

## 9. Come avviare il sistema

1. Sul Mac, nel terminale, nella cartella del progetto:
   `python3 server.py` (oppure resta attivo in background).
2. Operatore: apri `http://127.0.0.1:8000/prova2-persone-blob.html`.
3. Proiettore (Brave, stessa rete WiFi): apri `http://<IP-del-mac>:8000/proj.html`,
   poi tocca lo schermo / OK per il tutto schermo.
4. Calibra: **B** (sfondo, scena vuota) → **G** (trascina le 4 maniglie sui
   numeri) → regola **SOGLIA** → eventualmente **M** (specchia).
5. Cammina nell'area: la scia rivela il manifesto.

L'IP del Mac si trova con `ipconfig getifaddr en0`.

---

## 10. Stato attuale in una riga

Prototipo **funzionante end-to-end** (tracciamento multi-persona dall'alto con
sottrazione dello sfondo, rivelazione in tempo reale, proiezione su finestra
dedicata, calibrazione prospettica dell'area). In attesa dell'upgrade a
**telecamera IR wireless** per renderlo affidabile in condizioni reali (stanza
buia + proiettore acceso). La tesi è in scrittura; il sistema continuerà a essere
modificato nelle prossime settimane.
