# dev-brain — Manuale d'uso

> Manuale utente in italiano. Il codice, i comandi e le skill del kit sono in inglese; questo file è l'unica eccezione documentale.
> Versione: 2026-10-22. Richiede OpenCode V2.

## Indice

- Avvio rapido
- 1. Cos'è
- 2. Installazione e verifica
- 3. Prima adozione di una repository
- 4. Lavoro quotidiano
- 5. I comandi in dettaglio
- 6. I due file di progetto
- 7. Il plugin
- 8. Regole, permessi e sicurezza
- 9. Le skill
- 10. Il reviewer
- 11. Flussi di lavoro tipici
- 12. Manutenzione del kit
- 13. Migrazione dal vecchio dev-brain
- 14. Problemi e domande frequenti
- 15. Limiti noti
- 16. Checklist
- Riferimenti

## Avvio rapido

```bash
# 1. dalla cartella del kit
./install.sh

# 2. apri una nuova sessione OpenCode e verifica
opencode plugin list
opencode api GET /api/command
```

Dopo l'installazione puoi già fare una normale richiesta di codice, per esempio:

```text
Aggiungi la spedizione express al calcolo del totale, mantenendo invariata
la spedizione standard e compatibili le chiamate esistenti.
```

Le regole di leggibilità e manutenibilità sono già attive: non devi aggiungere “scrivilo bene”, invocare una skill o creare prima lo stato. Il kit segue il linguaggio e le convenzioni del progetto, non impone Python.

Se vuoi anche salvare i fatti e lo stato della repository, adottala con:

```text
/start
```

Per riprendere una sessione usando lo stato salvato:

```text
/resume
```

Per aggiornare lo stato alla fine del lavoro:

```text
/handoff
```

I comandi sono strumenti di supporto, non una sequenza obbligatoria per ottenere codice curato. Usa `/plan`, `/impact`, `/learn` e `/review` quando servono. Le spiegazioni dettagliate restano su richiesta e nessun commit è autorizzato da questi comandi.

---

## 1. Cos'è

dev-brain è un harness personale per OpenCode V2. Non è un'applicazione e non è un agente autonomo: è un insieme di istruzioni, comandi, skill e un piccolo plugin che rende il lavoro con OpenCode più prevedibile e continuo tra sessioni e repository.

Il suo obiettivo principale è aiutarti a produrre **codice leggibile, manutenibile e facile da modificare**; gestione dello stato, comandi e skill servono a sostenere questo obiettivo. Le regole di progettazione valgono anche per una normale richiesta di codice: non devi ricordarti di lanciare `/plan` o una skill. Sono indipendenti dal linguaggio: Python va bene, ma il kit si adatta anche agli altri linguaggi e framework del progetto.

Fornisce:

- regole sempre attive, volutamente poche;
- sette comandi per il flusso ricorrente;
- tre skill caricate solo quando servono;
- un reviewer indipendente in sola lettura;
- un plugin che inietta lo stato del progetto nel contesto del modello;
- un metodo di valutazione per capire se una regola funziona davvero.

Non fa queste cose:

- non avvia modifiche autonomamente: è l'agente OpenCode a implementare ciò che chiedi, entro l'ambito autorizzato;
- non decide quando committare;
- non sostituisce git, i test o la revisione umana;
- non garantisce che il modello segua le regole: le regole sono contesto, non un sistema di permessi.

### Cosa cambia in OpenCode

| Componente | Effetto |
| --- | --- |
| `~/.config/opencode/AGENTS.md` | Regole personali caricate in ogni sessione |
| `~/.config/opencode/commands/` | Comandi slash disponibili nella TUI |
| `~/.config/opencode/agents/reviewer.md` | Subagente di review in sola lettura |
| `~/.config/opencode/skills/` | Skill disponibili su richiesta |
| `~/.config/opencode/opencode.json` | Registrazione del plugin `dev-brain` |
| `.dev-brain/STATE.md` in ogni repo | Stato del progetto iniettato dal plugin |

---

## 2. Installazione e verifica

### Prerequisiti

- OpenCode V2 installato e funzionante (`opencode --version`);
- `bash`;
- `git`;
- `python3` — serve solo all'installer per aggiornare `opencode.json`, non a runtime.

### Installazione

```bash
cd <cartella-del-kit>
./install.sh
```

Lo script:

1. crea i collegamenti simbolici da `global/` a `~/.config/opencode/`;
2. registra il percorso assoluto del plugin in `~/.config/opencode/opencode.json`;
3. se trova un file già esistente e non gestito dal kit, lo sposta in `*.bak.<timestamp>` invece di cancellarlo;
4. è idempotente: eseguirlo di nuovo non duplica nulla.

Non riavvia il server e non modifica le tue permission.

### Verifica

```bash
opencode plugin list
opencode debug agents
opencode api GET /api/command
```

Risultati attesi:

- `dev-brain` compare tra i plugin, con sorgente `local`;
- `reviewer` compare tra gli agenti, in modalità `subagent`;
- i sette comandi compaiono nell'elenco, oltre ai comandi integrati di OpenCode.

Se i comandi non compaiono nella TUI:

```bash
# quando non hai sessioni attive
opencode service restart
```

Poi apri una nuova sessione.

### Aggiornamento

```bash
cd <cartella-del-kit>
git pull
./install.sh
```

Le modifiche ai file già collegati (regole, comandi, skill, reviewer) passano dai symlink. Se aggiungi un nuovo comando, agente o skill, riesegui `install.sh` per creare il nuovo collegamento. Se modifichi il plugin o un comando, riavvia il server: il server in esecuzione può usare il template in cache e la modifica non avrebbe effetto.

### Disinstallazione

Non c'è uno script di disinstallazione. Per rimuovere il kit:

```bash
rm ~/.config/opencode/AGENTS.md
rm ~/.config/opencode/commands/{start,resume,handoff,plan,impact,learn,review}.md
rm ~/.config/opencode/agents/reviewer.md
rm -r ~/.config/opencode/skills/{debugging,review-feedback,engineering-risk}
```

Poi togli il percorso del plugin da `~/.config/opencode/opencode.json`. Se l'installer aveva creato dei backup `*.bak.<timestamp>`, ripristinali manualmente. I file dentro i repository (`.dev-brain/STATE.md` e le sezioni dev-brain di `AGENTS.md`) restano: rimuovili solo se vuoi disadottare quei repository.

---

## 3. Prima adozione di una repository

Nella repository, dalla radice:

```text
/start
```

Il comando è pensato per l'adozione iniziale. Ispeziona il repository e crea o aggiorna due file:

```text
<repo>/
├── AGENTS.md            fatti del progetto, meno di 60 righe
└── .dev-brain/
    └── STATE.md         obiettivo, fatto, blocchi, prossime azioni
```

Cosa fa:

- legge codice, configurazione, README e comandi reali;
- se `AGENTS.md` esiste, lo integra preservando le istruzioni già presenti;
- se `.dev-brain/STATE.md` esiste, lo riconcilia invece di sovrascriverlo;
- riporta fatti osservati, incognite e problemi trovati;
- non modifica codice, dipendenze, configurazione o storia git.

Cosa non fa:

- non installa dipendenze;
- non esegue l'applicazione, migrazioni o conversioni;
- non committa;
- non decide al posto tuo se un problema va corretto.

### Privacy

Non aprire e non elencare directory che possono contenere dati personali, clinici o segreti, per esempio `input/`, `output/`, `.env`. Usa README e configurazione. Non copiare mai questi dati in `AGENTS.md`, in `STATE.md` o nella chat.

### Dopo `/start`

Leggi i due file generati e correggi ciò che non è vero. Sono pensati per essere versionati; se e quando decidi tu di committarli, puoi farlo separatamente dal codice. Questi sono comandi manuali, non un'autorizzazione automatica all'agente:

```bash
git diff -- AGENTS.md .dev-brain/STATE.md
git add AGENTS.md .dev-brain/STATE.md
git commit -m "Adopt dev-brain project instructions and state"
```

Se hai lavoro non committato, `/start` non lo tocca. Un albero pulito rende però più chiara l'evidenza nello stato.

---

## 4. Lavoro quotidiano

Il lavoro principale resta una normale richiesta di implementazione o correzione, con il risultato atteso e gli eventuali vincoli. L'agente deve applicare le regole di progettazione sempre attive e rileggere il codice modificato prima di consegnarlo. Non è necessario lanciare tutti i comandi qui sotto.

| Momento | Comando | Cosa ottieni |
| --- | --- | --- |
| Prima volta in una repo | `/start` | `AGENTS.md` + `.dev-brain/STATE.md` |
| Inizio sessione | `/resume` | Stato riconciliato con git e codice |
| Modifica non banale | `/plan <obiettivo>` | Piano in massimo 5 passi, con verifiche |
| Prima di toccare codice condiviso | `/impact <modifica>` | Consumatori, contratti, test, incognite |
| Capire un flusso | `/learn <area>` | Spiegazione basata sul codice reale |
| Prima di committare | `/review [scope]` | Review indipendente del diff |
| Fine lavoro | `/handoff` | Stato aggiornato con evidenza fresca |

Per un progetto adottato, una sequenza utile per la continuità è:

```text
/resume  →  lavora  →  /handoff
```

### Un flusso tipico

1. `/resume` — leggi obiettivo, ultimo risultato verificato, blocchi e prossima azione.
2. Se la modifica è non banale, `/plan` e poi `/impact`.
3. Implementa.
4. Fai eseguire i test o i controlli all'agente principale, oppure eseguili tu; il subagente reviewer non può lanciarli.
5. `/review` sul diff.
6. `/handoff` per chiudere lo stato.
7. Committa solo se hai deciso di farlo.

---

## 5. I comandi in dettaglio

### `/start`

**Quando:** prima adozione di una repository, o quando vuoi riallineare i fatti del progetto.

**Cosa produce:** root `AGENTS.md` e `.dev-brain/STATE.md`.

**Scrive:** sì, solo quei due file (o li aggiorna).

**Non fa:** modifiche al codice, installazioni, conversioni, commit.

**Consiglio:** controlla che i comandi nel file siano quelli veri, che non ci siano path assoluti e che lo stato non contenga dati sensibili.

---

### `/resume`

**Quando:** all'inizio di una sessione, soprattutto dopo una pausa.

**Cosa fa:**

- legge `.dev-brain/STATE.md` e `AGENTS.md`;
- confronta lo stato con `git status`, gli ultimi commit e i file reali;
- se lo stato è vecchio, lo dice prima di proseguire;
- esegue un controllo registrato solo se è sicuro e in sola lettura;
- riporta obiettivo, ultimo risultato verificato, blocchi e una prossima azione.

**Scrive:** no.

**Non fa:** non implementa e non aggiorna lo stato; per quello c'è `/handoff`.

**Nota:** i risultati vecchi non vengono presentati come appena eseguiti.

Il comando deve evitare installazioni e creazione di ambienti o cache. Per esempio, prima di un `uv run` verifica che `.venv` esista; se manca, il controllo va riportato come `NOT RUN`. È un'istruzione al modello, non un blocco tecnico: l'esistenza della directory non prova che ogni comando sia privo di effetti collaterali.

---

### `/handoff`

**Quando:** alla fine di un lavoro significativo, prima di chiudere la sessione o cambiare contesto.

**Cosa fa:**

- legge lo stato attuale;
- ricostruisce cosa è successo davvero da diff, controlli e conversazione;
- riscrive `.dev-brain/STATE.md`: obiettivo, fatto con evidenza, blocchi, prossime azioni;
- aggiorna `AGENTS.md` solo se è cambiato un fatto stabile (stack, comandi, architettura, gotcha);
- riporta cosa ha cambiato e cosa non è verificato.

**Scrive:** sì, lo stato (e raramente `AGENTS.md`).

**Non fa:** non committa e non modifica il codice.

**Regola:** massimo 5 voci in “Fatto”, massimo 3 in “Prossime azioni”. Lo stato non è un diario: sostituisci le righe vecchie.

---

### `/plan <obiettivo>`

**Quando:** una modifica non banale, prima di scrivere codice.

**Cosa fa:** gira con l'agente `plan`, in sola lettura, e produce un piano-contratto con al massimo 5 passi. Ogni passo è un risultato concreto, non un'attività generica, e include:

- file o simboli coinvolti;
- input → output;
- dipendenze;
- controllo che può fallire e risultato atteso.

**Scrive:** no.

**Consiglio:** indica obiettivo, vincoli e criteri di accettazione. Se una decisione cambia comportamento o dati, il piano deve chiedertela prima.

**Nota:** se la sessione resta sull'agente `plan`, riseleziona `build` prima di implementare.

---

### `/impact <modifica>`

**Quando:** prima di cambiare un contratto, un formato, un dato persistito o codice condiviso.

**Cosa fa:** analisi in sola lettura di:

- consumatori diretti: chiamanti, import, endpoint, eventi, query, formati;
- contratti a rischio: firme, errori, effetti collaterali, invarianti, configurazione, schema;
- test, fixture e configurazione che descrivono il comportamento attuale;
- file da modificare e file da rivedere;
- controlli esistenti, senza eseguirli;
- incognite e il più piccolo esperimento per risolverle.

**Scrive:** no.

**Etichette:** `OBSERVED` (visto nel codice), `INFERRED` (dedotto), `UNKNOWN`. Una dipendenza dichiarata non prova un collegamento attivo.

---

### `/learn <area>`

**Quando:** devi capire un flusso, un componente o uno stack che non conosci.

**Cosa fa:** legge il codice reale e procede per strati:

1. ambito e responsabilità;
2. inventario di file e simboli;
3. connessioni reali;
4. un flusso concreto, passo per passo;
5. ordine di lettura.

**Scrive:** no.

**Formato delle connessioni:**

```text
Flow: <file:symbol> -> <file:symbol>: <cosa succede e quali dati passano> -> <file:symbol>: <risultato>
```

**Etichette:** `OBSERVED`, `INFERRED`, `UNKNOWN`. Non è un tutorial generico: se una cosa non è stata verificata, lo dice.

---

### `/review [scope]`

**Quando:** prima di committare o aprire una PR.

**Cosa fa:**

- cattura `git status`, `git diff --stat` e `git diff`;
- delega la review al subagente `reviewer`, che è indipendente e in sola lettura;
- riporta i risultati senza ammorbidirli.

**Scrive:** no.

**Non fa:** non modifica file, non committa e non esegue test.

**Cosa cerca il reviewer:**

- difetti di correttezza, sicurezza, integrità dei dati o requisiti dichiarati, separati da problemi concreti di manutenibilità;
- `file:line`, trigger concreto o scenario di manutenzione, impatto, correzione minima;
- difetti confermati separati da sospetti che richiedono contesto;
- test che provano davvero il comportamento e fallirebbero sul difetto originale.

**Limiti importanti:**

- il reviewer non ha shell: non può eseguire test; li esegue l'agente principale o li lanci tu;
- il diff acquisito è `git diff`, senza `--cached`: le modifiche già in staging non sono incluse automaticamente nel diff passato al reviewer;
- `git diff` non include i file nuovi non tracciati: il comando ne passa anche i nomi al reviewer, che li legge direttamente se sono nello scope; i file ignorati da git non entrano automaticamente nella review;
- se il diff è vuoto, il comando si ferma.

Con soli file non tracciati il diff può essere vuoto: il comando elenca quei file, ma contiene anche l'istruzione di fermarsi sul diff vuoto. Quel caso non è stato verificato; non dare per acquisito che tutti i file siano stati letti, controlla la copertura dichiarata dal reviewer.

---

## 6. I due file di progetto

### `AGENTS.md`

È il file dei fatti stabili del progetto. OpenCode lo carica come istruzioni. Deve restare sotto le 60 righe.

Contenuto consigliato:

```markdown
# <Nome progetto>

<Una riga: cosa fa e per chi.>

## Stack
- <linguaggio e versione, framework, package manager>

## Comandi
- Install: `<comando>` (dalla directory `<...>`)
- Test: `<comando>`
- Lint / type check: `<comando>`
- Build: `<comando>`

## Struttura
- `<path>` — <responsabilità>

## Convenzioni e gotcha
- <convenzione non ovvia>
- <limite operativo o trappola>

## Da non fare
- <operazione distruttiva o vietata>
```

Regole:

- niente consigli generici: le regole globali ci sono già;
- comandi esatti, con directory di lavoro ed effetti collaterali;
- niente path assoluti della tua macchina;
- niente segreti, PHI o dati personali;
- aggiornalo solo quando cambia un fatto stabile, non a ogni modifica.

### `.dev-brain/STATE.md`

È lo stato di lavoro del progetto. Va nella radice della repository ed è pensato per essere versionato; il commit resta una tua decisione esplicita, mai una conseguenza automatica di `/start` o `/handoff`.

Template:

```markdown
# State — <progetto>
Updated: <data> · Branch: <branch>

## Goal
<una riga> — acceptance: <criteri osservabili>

## Done (latest first, max 5)
- <risultato> — evidence: <comando> PASS|FAIL|NOT RUN

## In progress / blockers
- <elemento> — status: implemented|verified|blocked — <perché>

## Known pre-existing failures
- <comando> — <errore> — since <data>

## Next (max 3)
1. <azione eseguibile>
```

Regole:

- il plugin inietta le prime 80 righe: tienilo sotto le 80;
- “Fatto” massimo 5 voci, “Prossime azioni” massimo 3;
- ogni voce “Fatto” ha un comando e un esito reale;
- `PASS` significa eseguito e passato; `NOT RUN` significa non eseguito; non usare “implementato” come se fosse “verificato”;
- sostituisci le righe vecchie, non aggiungerne di nuove in coda;
- non inserire dati sensibili: lo stato viene inviato al provider del modello e finisce nel repository;
- una sola sessione alla volta dovrebbe fare `/handoff`, per evitare sovrascritture.

Lo stato è contesto, non prova e non autorizzazione: l'agente deve sempre verificare con git e con il codice.

---

## 7. Il plugin

Il plugin `plugin/dev-brain/index.ts` fa tre cose.

1. **Iniezione dello stato.** A ogni chiamata al modello legge `.dev-brain/STATE.md` nella radice del progetto e aggiunge le prime 80 righe al contesto di sistema. L'iniezione è transitoria: non modifica il file e non serve ripetere lo stato nella chat.
2. **Repository senza stato.** Se la repository è git e il file non esiste, aggiunge una sola riga che suggerisce `/start`. Non crea il file da solo.
3. **Compaction.** Quando la sessione viene compattata, chiede al riassunto di conservare obiettivo, evidenza verificata, blocchi e prossima azione. Lo stato viene comunque reiniettato alla chiamata successiva.

Dettagli:

- il file va nella radice del repository, non in una sottocartella;
- se è più lungo di 80 righe, la parte eccedente non viene iniettata;
- il plugin non fa chiamate di rete proprie, ma lo stato entra nella richiesta al provider del modello: non metterci segreti o PHI;
- i subagenti ricevono lo stesso contesto di progetto;
- per disattivare l'iniezione in una repository, rimuovi o rinomina `.dev-brain/STATE.md`. Le regole globali restano attive e, se la repo è git, il plugin continuerà a suggerire `/start` finché il file manca.

---

## 8. Regole, permessi e sicurezza

Le regole globali vivono in `global/AGENTS.md` e vengono installate come `~/.config/opencode/AGENTS.md`.

### Precedenza

```text
correttezza > sicurezza e integrità dei dati > compatibilità col progetto > manutenibilità > semplicità > prestazioni misurate
```

### Qualità del codice, sempre attiva

Quando chiedi di scrivere o modificare codice, l'agente deve:

- scegliere la soluzione più semplice che soddisfa davvero i requisiti, non quella con meno righe; niente funzionalità o punti di estensione ipotetici;
- seguire gli idiomi del linguaggio e le convenzioni del progetto, senza imporre classi, framework o livelli architetturali;
- usare nomi che esprimono l'intento, responsabilità coese, dipendenze ed effetti collaterali espliciti; dividere per responsabilità, non per limiti arbitrari di righe;
- mantenere in un solo punto le stesse regole di business, ma non accoppiare concetti diversi solo perché il codice si assomiglia;
- preservare contratti e gestione degli errori, senza nascondere fallimenti dietro fallback silenziosi; commentare motivazioni e vincoli non ovvi, non la sintassi;
- rileggere il codice modificato prima di consegnarlo, cercando complessità inutile, duplicazioni, nomi fuorvianti, effetti nascosti e debug dimenticato, senza avviare un refactor estraneo alla richiesta.

Questo controllo sul codice non comporta una spiegazione lunga in output: il walkthrough resta su richiesta. Le regole guidano il modello, non garantiscono da sole un risultato migliore. Test funzionali e valutazione della manutenibilità restano due verifiche diverse.

### Autorizzazione

- leggere o adottare una repository non autorizza modifiche;
- non creare, emendare o pushare un commit se non hai deciso tu esplicitamente di committare; implementare, correggere, testare, fare review o handoff non è un permesso di commit;
- nessun cambio di branch, operazione distruttiva, migrazione, deploy o pubblicazione senza un permesso esplicito per quell'azione;
- `/handoff` aggiorna lo stato, non autorizza un commit;
- preserva il lavoro non committato; niente pulizie o riformattazioni non richieste;
- non leggere e non elencare file che possono contenere segreti, dati personali o clinici senza necessità: usa documentazione e configurazione.

### Test e debug

- per un bug o un comportamento nuovo, se esiste un harness di test, prima guarda fallire un test mirato per il motivo giusto;
- un errore di setup non è evidenza del difetto;
- annota i fallimenti preesistenti e non attribuirli alla tua modifica;
- dopo 3 tentativi materialmente equivalenti falliti, fermati e riporta cosa hai imparato;
- per un bug non banale carica la skill `debugging`; per sicurezza, persistenza, concorrenza o prestazioni carica `engineering-risk`.

### Reporting

- ogni controllo va riportato come `PASS`, `FAIL`, `NOT RUN` o `N/A`, con il comando reale;
- una build non è comportamento; un mock non è verifica dal vivo;
- “implementato” non significa “verificato”;
- chiudi con ciò che non hai controllato.

### Spiegazione delle modifiche

Non viene aggiunta automaticamente: consuma token di output. L'agente la produce solo se la chiedi esplicitamente (per esempio “spiega la modifica”, “walkthrough”, “Flow/Why/Checks/Read next”). In caso contrario riporta in modo conciso cosa ha cambiato, i controlli eseguiti e cosa non ha controllato.

Quando la chiedi, il formato è:

```text
Flow: <entry path:symbol> -> <next path:symbol>: <cosa succede> -> <changed path:symbol>: <nuovo risultato>
Why: <decisione chiave e alternativa scartata>
Checks: <comando> - <risultato>; prova <caso>, non <limite>
Read next: <path:symbol> - <perché>
```

### Continuità

- a fine lavoro aggiorna `.dev-brain/STATE.md` o chiedi `/handoff`;
- aggiorna `AGENTS.md` solo per fatti stabili;
- non importare evidenza, permessi o lavoro attivo da un'altra repository.

### Cosa significa “permesso”

Significa che hai chiesto esplicitamente quell'azione. Non basta che l'azione sia utile o coerente con l'obiettivo. `--auto` elimina le richieste di conferma: usalo solo su fixture usa e getta, mai su dati reali.

Il kit non modifica le permission globali di OpenCode. Il reviewer ha shell ed edit negati dalla sua configurazione; gli altri agenti seguono le tue impostazioni.

---

## 9. Le skill

Le skill sono istruzioni specializzate che il modello carica quando il compito corrisponde alla descrizione. Non hanno comandi slash propri.

| Skill | Quando si carica | Cosa impone |
| --- | --- | --- |
| `debugging` | Bug, test che fallisce, comportamento inatteso | Riprodurre, localizzare, ipotizzare, testare, correggere la causa, verificare |
| `review-feedback` | Commenti di review, feedback PR, findings di un altro agente | Classificare ogni commento prima di implementarlo |
| `engineering-risk` | Auth, input utente, segreti, dati persistiti, migrazioni, concorrenza, servizi esterni, prestazioni | Leggere solo il riferimento pertinente: sicurezza, dati, prestazioni |

Per richiamarle esplicitamente puoi scrivere, per esempio:

```text
Carica la skill debugging e usa il suo metodo.
```

`review-feedback` classifica ogni osservazione in:

- `SUPPORTED` — il codice o il requisito confermano il problema: correggi con un controllo;
- `UNSUPPORTED` — il codice contraddice la tesi: rispondi con l'evidenza, non cambiare;
- `NEEDS CONTEXT` — manca l'intento: fai la domanda specifica;
- `OUT OF SCOPE` — valido ma estraneo: registralo e proponilo a parte.

---

## 10. Il reviewer

Il reviewer è un subagente indipendente, in sola lettura. Non ha shell e non può modificare file.

Riporta difetti di correttezza, sicurezza, integrità dei dati o requisiti dichiarati e problemi concreti di manutenibilità. Tiene separate le due categorie: un costo futuro di manutenzione non è automaticamente un bug presente. Per ogni finding:

- `file:line` e simbolo;
- trigger concreto: input, stato o sequenza che produce il problema, oppure la modifica o attività di debug resa più difficile;
- impatto;
- correzione minima;
- confidenza: confermato dal codice o sospetto che richiede contesto.

Per la manutenibilità cerca regole di business duplicate, indirezioni non necessarie, responsabilità non correlate accoppiate o flussi che nascondono il contratto. Deve indicare il costo concreto e la semplificazione minima, non proporre un redesign. Non segnala preferenze cosmetiche su stile o nomi, né chiede di astrarre ogni somiglianza. Se non trova nulla che superi la soglia, dice “No correctness or maintainability findings”.

Limiti:

- non esegue test;
- il diff non contiene i file non tracciati; il comando ne passa anche i nomi e il reviewer li legge se sono nello scope, ma i file ignorati restano esclusi;
- non conosce l'intento se non è nel diff o nello scope;
- la sua review non sostituisce i tuoi controlli.

---

## 11. Flussi di lavoro tipici

### Repository nuova

```text
/start
# leggi AGENTS.md e .dev-brain/STATE.md
# committa i due file separatamente solo se lo decidi tu
/resume
```

### Sessione quotidiana

```text
/resume
# lavora
/handoff
```

### Modifica non banale

```text
/plan <obiettivo>
/impact <modifica>
# implementa
# esegui i test
/review
/handoff
# commit manuale, se decidi
```

### Bug

```text
# descrivi sintomo e comando di riproduzione
# carica la skill debugging
# riproduci il fallimento
# test mirato che fallisce per il motivo giusto
# correggi la causa
# verifica
/handoff
```

### Feedback di review

```text
# incolla o descrivi i commenti
# carica la skill review-feedback
# classifica ogni punto
# implementa solo i SUPPORTED
# riesegui i controlli
```

### Capire un flusso

```text
/learn <area o flusso>
# leggi l'ordine di lettura suggerito
# fai domande sulle parti UNKNOWN
```

---

## 12. Manutenzione del kit

### Struttura del repository del kit

```text
global/       regole sempre attive, comandi, agenti, skill
plugin/       plugin OpenCode V2
templates/    template di STATE.md e AGENTS.md
evals/        scenari, fixture, risultati misurati
MANUALE.md    questo manuale
```

### Modificare il kit

1. Apri una modifica piccola e mirata.
2. Se cambia il comportamento, esegui gli scenari in `evals/scenarios/` e registra il baseline.
3. Applica la modifica.
4. Riesegui gli stessi scenari.
5. Tieni la modifica solo se migliora uno scenario o rimuove un costo reale.
6. Registra l'esito in `evals/results.md` con data ed evidenza.

Non aggiungere regole per intuizione. Una regola che il modello già segue è solo costo di contesto.

### Evals

```bash
# Solo dopo aver autorizzato i commit locali delle fixture:
./evals/setup.sh
# copia le fixture in /tmp/opencode/dev-brain-evals e ricrea la storia git
cd /tmp/opencode/dev-brain-evals/bugfix
opencode run --standalone -m <provider/model> "The discount test fails. Fix the code."
```

I comandi slash si provano dalla TUI, non con `opencode run`.

`evals/setup.sh` ricrea la cartella di test e crea commit locali per gli scenari che richiedono una storia git. Lo scenario di manutenibilità (`evals/scenarios/maintainability.md`) può essere eseguito su copie nuove senza storia git e senza commit. Non eseguire il setup per il solo aggiornamento della documentazione.

### Lingua

Tutto il contenuto del kit è in inglese, tranne questo manuale utente.

### Backup e aggiornamenti

- i file non gestiti vengono salvati come `*.bak.<timestamp>`;
- se l'installer sposta un tuo `AGENTS.md`, unisci le tue regole in `global/AGENTS.md` o in un `AGENTS.md` di progetto;
- il plugin è registrato con un percorso assoluto: se sposti la cartella del kit, riesegui `install.sh`;
- non copiare fatti di progetto (stack, comandi, stato) nel repository del kit.

---

## 13. Migrazione dal vecchio dev-brain

La vecchia cartella visibile `dev-brain/` non esiste più in questo repository; il contenuto resta nella storia git al commit `08baebc`.

Per ogni repository che aveva una copia:

1. confronta il suo `RULES.md` con `global/AGENTS.md` e conserva solo le regole specifiche del progetto o realmente utili;
2. sposta i fatti stabili nel root `AGENTS.md`;
3. converti `NOW.md`, `PROJECT_STATE.md` e `PROJECT_MAP.md` in `.dev-brain/STATE.md` e nelle sezioni di `AGENTS.md`;
4. rimuovi i file del vecchio kit;
5. verifica che non ci siano istruzioni contraddittorie: le regole globali nuove si applicano comunque.

Se una repository ha una cartella `harness/` con i vecchi `PROJECT_MAP.md` e `PROJECT_STATE.md`, quei file vanno trattati come il vecchio kit: prima raccogli i fatti, poi li rimuovi solo dopo conferma.

Per recuperare il vecchio contenuto:

```bash
git show 08baebc:dev-brain/RULES.md
git archive 08baebc dev-brain | tar -x -C /tmp
```

---

## 14. Problemi e domande frequenti

| Sintomo | Causa e soluzione |
| --- | --- |
| I comandi non compaiono nella TUI, o una modifica a un comando non ha effetto | Apri una nuova sessione; se il server era già attivo, `opencode service restart` quando non hai sessioni attive |
| `opencode run "/resume"` non espande il comando | Limite della CLI: manda il testo letterale. Usa la TUI |
| Il plugin non compare | Controlla `opencode.json`, il percorso assoluto e `opencode plugin list`; riavvia il server |
| Lo stato non viene iniettato | Verifica `.dev-brain/STATE.md` nella radice, non vuoto, prime 80 righe; apri una nuova sessione |
| L'installer ha spostato il mio `AGENTS.md` | Cerca `AGENTS.md.bak.<timestamp>` e unisci le tue regole |
| `opencode.json` non viene aggiornato | Probabilmente contiene commenti JSONC non gestiti: aggiungi a mano `"plugins": ["<percorso-assoluto>/plugin/dev-brain"]` |
| Edit o shell negati | La tua configurazione OpenCode o il reviewer possono negarli; il reviewer nega shell ed edit per progetto. `--auto` solo su fixture usa e getta |
| `/review` non trova il file nuovo | Il comando elenca gli untracked non ignorati: controlla scope, template aggiornato e copertura dichiarata dal reviewer. Il caso con soli untracked e diff vuoto non è ancora verificato |
| Dopo `/plan` l'agente resta `plan` | Riseleziona `build` prima di implementare |
| Lo stato cresce troppo | Riscrivilo a `/handoff`: massimo 5 voci fatte, 3 prossime azioni, meno di 80 righe |
| Due sessioni si sovrascrivono lo stato | Fai `/handoff` da una sola sessione alla volta |
| Il modello ignora lo stato | Lo stato è contesto, non enforcement: usa `/resume`, verifica con git e chiedi esplicitamente |
| Una sessione API non esegue un comando | Imposta `agent` e `model` alla creazione della sessione; è un limite del test via API, non della TUI |
| Ho dati clinici o segreti in `STATE.md` | Rimuovili subito, valuta la rotazione delle credenziali e non committare; lo stato viene inviato al provider |

---

## 15. Limiti noti

- Le prove usano fixture piccole e pochi run; i risultati dipendono dal modello e non sono una garanzia per ogni progetto. Il dettaglio delle esecuzioni e dei modelli è in `evals/results.md`.
- Nella nuova prova di generazione il codice era già leggibile prima della modifica alle regole e lo è rimasto dopo: non è stato dimostrato un guadagno generale nella qualità del codice prodotto.
- La policy di review ora riconosce una regola di business duplicata come problema di manutenzione, senza proporre di unire politiche indipendenti. La prova era diretta sulla policy: non verifica il nuovo percorso di delega di `/review` né la TUI.
- Le regole sono indipendenti dal linguaggio, ma la nuova fixture di manutenibilità è solo Python: la generazione in altri linguaggi non è stata verificata in quella prova.
- Le regole sono contesto: il modello può non seguirle. I comandi e le skill mirano a ridurre la variabilità, non a eliminarla.
- `opencode run` non espande i comandi slash; il percorso previsto è la TUI. L'espansione è stata verificata via API, non pilotando la TUI automaticamente.
- Il reviewer non esegue test. Il comando gli passa i nomi dei file non tracciati non ignorati, da leggere se nello scope; la copertura con soli untracked e diff vuoto resta non verificata.
- `/resume` dipende dal rispetto delle istruzioni di sola lettura. Il controllo su `.venv` ha funzionato nella copia di test, ma ha fatto saltare anche verifiche innocue: non è una garanzia di isolamento degli effetti collaterali.
- L'hook di compaction è presente nel plugin, ma non è stato osservato durante una compattazione reale.
- Lo stato può diventare vecchio: `/resume` lo riconcilia, ma non è una verità automatica.
- Nessun commit automatico: l'agente non crea, emenda o pusha commit senza la tua decisione esplicita.
- Lo stato viene iniettato a ogni chiamata: tienilo corto.
- La spiegazione dettagliata è su richiesta: di default le risposte restano brevi.
- Una sola sessione dovrebbe aggiornare lo stato alla volta.
- Non c'è uno script di disinstallazione.
- Il percorso del plugin è assoluto: se sposti il kit, reinstalla.
- Richiede OpenCode V2; non è testato su V1.

---

## 16. Checklist

- [ ] `./install.sh` eseguito senza errori
- [ ] `opencode plugin list` mostra `dev-brain`
- [ ] `opencode debug agents` mostra `reviewer`
- [ ] `opencode api GET /api/command` elenca i sette comandi
- [ ] Le regole di progettazione sono presenti in `~/.config/opencode/AGENTS.md`; non servono comandi speciali per applicarle
- [ ] `/start` eseguito su almeno una repository
- [ ] `AGENTS.md` sotto 60 righe, senza path assoluti né dati sensibili
- [ ] `.dev-brain/STATE.md` sotto 80 righe, con evidenza reale
- [ ] I due file di progetto revisionati; eventuale commit separato dal codice solo per tua decisione
- [ ] Nessun commit, amend o push eseguito dall'agente senza una tua decisione esplicita
- [ ] `/resume` e `/handoff` provati in una sessione reale
- [ ] `/review` provato sullo scope desiderato, controllando anche la copertura dei file nuovi
- [ ] Backup `*.bak.*` controllati dopo l'installazione
- [ ] Nessun dato clinico, personale o segreto in stato, istruzioni o chat

---

## Riferimenti

- `README.md` — installazione e panoramica in inglese
- `global/AGENTS.md` — regole sempre attive
- `global/commands/` — codice dei sette comandi
- `global/skills/` — skill e riferimenti
- `plugin/dev-brain/index.ts` — plugin
- `evals/results.md` — cosa è stato misurato e cosa no
