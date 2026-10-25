# dev-brain — Manuale d'uso

> Manuale utente in italiano. Il codice, i workflow e le skill del kit sono in inglese; questo file è l'unica eccezione.
> Versione: 2026-10-25. Funziona con OpenCode (provato su 2.1.4), Claude Code (2.1.310), Codex CLI (0.164) e Cursor (non provato: nessuna CLI disponibile nell'ambiente di test). Indipendente dal provider del modello.

## Indice

- Avvio rapido
- 1. Cos'è
- 2. Come è costruito
- 3. Installazione e verifica
- 4. Prima adozione di una repository
- 5. Lavoro quotidiano
- 6. I workflow in dettaglio
- 7. I due file di progetto
- 8. Lo stato nel contesto dell'agente
- 9. Regole, permessi e sicurezza
- 10. Le skill
- 11. Il reviewer
- 12. Manutenzione del kit
- 13. Problemi e domande frequenti
- 14. Limiti noti
- 15. Checklist

---

## Avvio rapido

```bash
# dalla cartella del kit: installa per ogni agente trovato sulla macchina
./install.sh
# oppure solo quelli che vuoi
./install.sh opencode claude-code codex cursor
```

Poi fai una normale richiesta di codice. Le regole di leggibilità e manutenibilità sono già attive: non devi scrivere “fallo bene”, né invocare una skill.

I workflow si invocano con la sintassi del tuo agente:

| Agente | Esempio |
| --- | --- |
| OpenCode | `/review` |
| Claude Code | `/dev-brain:review` |
| Codex CLI | `$dev-brain:review` |
| Cursor | `/review` |

Sequenza tipica per un progetto adottato: `start` la prima volta, poi `resume` → lavoro → `review` → `handoff`.

---

## 1. Cos'è

dev-brain è un harness personale per agenti di coding. Non è un'applicazione e non è un agente autonomo: è un insieme di regole, workflow, skill, un reviewer e un meccanismo di stato. Rende il lavoro più prevedibile e continuo tra sessioni, repository e strumenti.

L'obiettivo principale è **codice leggibile, manutenibile e facile da modificare**. Stato e workflow servono a sostenerlo.

Fornisce:

- regole sempre attive, volutamente poche;
- sette workflow invocati da te: `start`, `resume`, `handoff`, `plan`, `impact`, `learn`, `review`;
- tre skill che il modello carica quando servono: `debugging`, `review-feedback`, `engineering-risk`;
- un reviewer indipendente in sola lettura;
- lo stato del progetto iniettato nel contesto, con un budget di dimensione;
- un controllo offline a costo zero e un metodo di valutazione per capire se una regola funziona davvero.

Non fa queste cose:

- non decide quando committare;
- non sostituisce git, i test o la tua revisione;
- non garantisce che il modello segua le regole: le regole sono contesto. Dove l'agente lo permette (permessi, sandbox), alcune cose sono anche imposte; vedi sezione 2.

---

## 2. Come è costruito

**`core/` è l'unica fonte.** Usa i due formati che tutti gli agenti condividono:

- `AGENTS.md` per le regole;
- Agent Skills (`SKILL.md`) per workflow e skill.

`install.py` collega o traduce `core/` in ciò che ogni agente legge. Nessuna regola vive negli adattatori: se cambi una regola in `core/`, cambia per tutti.

| | OpenCode | Claude Code | Codex CLI | Cursor |
| --- | --- | --- | --- | --- |
| Regole globali | `AGENTS.md` (link) | `CLAUDE.md` importa `core/AGENTS.md` | `AGENTS.md` (link) | `rules/dev-brain.mdc` (copia) |
| Workflow | comandi `/review` | plugin, `/dev-brain:review` | plugin, `$dev-brain:review` | skill, `/review` |
| Skill | `skills/` (link) | plugin | plugin | `skills/` (link) |
| Reviewer in sola lettura | **imposto**: solo `git diff/log/show/status`, `>` e `--output` bloccati | **imposto**: altri comandi chiedono la tua approvazione | **solo istruzione**: `sandbox_mode` non vale per i subagenti (Codex 0.164) | `readonly: true` (non provato) |
| Stato nel contesto | plugin, a ogni chiamata della sessione principale | hook `SessionStart` | hook `SessionStart`, dopo che lo approvi una volta | hook `sessionStart` (bug di Cursor) + regola di riserva |

**Regola di riserva:** se l'agente non riesce a iniettare lo stato, le regole globali gli dicono di leggere `.dev-brain/STATE.md` prima di continuare un lavoro iniziato. Funziona con qualsiasi agente che legge `AGENTS.md`, ma costa una lettura e dipende dal modello.

**Perché Claude Code e Codex usano un plugin:** è l'unico canale che porta skill, workflow e hook senza toccare le loro impostazioni a mano, ed è namespaced (`dev-brain:`), quindi non collide con i comandi integrati come `/review`. L'installer costruisce un marketplace locale in `build/` e lo installa con la CLI dell'agente. Codex copia il plugin e ignora i link simbolici, per questo il build contiene copie vere.

---

## 3. Installazione e verifica

### Prerequisiti

- almeno uno tra OpenCode V2, Claude Code, Codex CLI, Cursor;
- `python3` e `git`.

### Installazione

```bash
cd <cartella-del-kit>
./install.sh                  # agenti trovati: CLI nel PATH o cartella di configurazione presente
./install.sh opencode codex   # solo questi
```

Lo script:

1. collega le regole o le traduce nel formato dell'agente;
2. genera comandi, agenti e hook dove servono;
3. per Claude Code e Codex costruisce e installa il plugin `dev-brain`;
4. se trova un file non gestito dal kit, lo sposta in `*.bak.<timestamp>` invece di cancellarlo;
5. è idempotente: rieseguirlo non duplica nulla.

Passi manuali, una volta sola:

- **OpenCode:** `opencode service restart` quando non hai sessioni attive, altrimenti il server usa i template in cache.
- **Codex:** approva l'hook `SessionStart` nella TUI. Codex non esegue hook nuovi finché non li hai rivisti.
- **Cursor:** se l'agente ignora le regole, incolla `core/AGENTS.md` in Settings > Rules. Le regole globali su file non sempre vengono caricate (bug noto di Cursor).

### Verifica

```bash
python3 evals/offline/check.py
```

Deve stampare `ALL PASS`. Verifica ogni agente installato senza spendere token (sezione 12).

### Aggiornamento

```bash
git pull
./install.sh
```

Rieseguire l'installer serve sempre: Codex e Cursor ricevono copie, e il plugin cambia versione quando cambia il contenuto.

### Disinstallazione

Non c'è uno script. In breve:

- OpenCode: rimuovi `AGENTS.md`, `commands/{start,resume,handoff,plan,impact,learn,review}.md`, `agents/reviewer.md`, `skills/{debugging,review-feedback,engineering-risk}` da `~/.config/opencode/` e il percorso del plugin da `opencode.json`;
- Claude Code: `claude plugin uninstall dev-brain@dev-brain` e togli la riga `@.../core/AGENTS.md` da `~/.claude/CLAUDE.md`;
- Codex: `codex plugin remove dev-brain@dev-brain`, rimuovi `~/.codex/AGENTS.md`, `~/.codex/agents/reviewer.toml` e la voce `dev-brain-context` da `~/.codex/hooks.json`;
- Cursor: rimuovi `~/.cursor/rules/dev-brain.mdc`, `~/.cursor/agents/reviewer.md`, i link in `~/.cursor/skills/` e la voce `dev-brain-context` da `~/.cursor/hooks.json`.

Ripristina eventuali backup `*.bak.<timestamp>`. I file nei repository (`AGENTS.md`, `.dev-brain/STATE.md`) restano.

---

## 4. Prima adozione di una repository

Lancia il workflow `start` nella radice della repository. Crea o aggiorna due file:

```text
<repo>/
├── AGENTS.md            fatti del progetto, meno di 60 righe
└── .dev-brain/
    └── STATE.md         obiettivo, fatto, blocchi, prossime azioni, meno di 3000 caratteri
```

Cosa fa:

- legge codice, configurazione, README e comandi reali;
- se `AGENTS.md` esiste, lo integra preservando le istruzioni presenti;
- se `.dev-brain/STATE.md` esiste, lo riconcilia invece di sovrascriverlo;
- se trova file del vecchio kit (`harness/PROJECT_STATE.md`, `harness/PROJECT_MAP.md`, `NOW.md`, `RULES.md`), li usa come fonte e te li elenca da eliminare, senza cancellarli;
- riporta fatti osservati, incognite, file legacy e problemi trovati;
- non modifica codice, dipendenze, configurazione o storia git, non installa nulla, non committa.

**Esempio reale:** in hph i 21 KB di `harness/` sono diventati un `AGENTS.md` di 3,1 KB e uno stato di 1,3 KB.

### Privacy

Non aprire e non elencare directory che possono contenere dati personali, clinici o segreti (`input/`, `output/`, `.env`). Usa README e configurazione. Non copiare mai questi dati in `AGENTS.md`, nello stato o nella chat: lo stato viene inviato al provider del modello.

### Dopo `start`

Leggi i due file e correggi ciò che non è vero. Sono pensati per essere versionati; se e quando decidi tu, committali separatamente dal codice:

```bash
git diff -- AGENTS.md .dev-brain/STATE.md
git add AGENTS.md .dev-brain/STATE.md
git commit -m "Adopt dev-brain project instructions and state"
```

---

## 5. Lavoro quotidiano

Il lavoro principale resta una normale richiesta di implementazione o correzione, con risultato atteso e vincoli. I workflow sono strumenti di supporto, non una sequenza obbligatoria.

| Momento | Workflow | Cosa ottieni |
| --- | --- | --- |
| Prima volta in una repo | `start` | `AGENTS.md` + `.dev-brain/STATE.md` |
| Inizio sessione | `resume` | Stato riconciliato con git e codice |
| Modifica non banale | `plan` | Piano in massimo 5 passi, con verifiche |
| Prima di toccare codice condiviso | `impact` | Consumatori, contratti, test, incognite |
| Capire un flusso | `learn` | Spiegazione basata sul codice reale |
| Prima di committare | `review` | Review indipendente delle modifiche |
| Fine lavoro | `handoff` | Stato aggiornato con evidenza fresca |

Un flusso tipico:

1. `resume`: obiettivo, ultimo risultato verificato, blocchi, prossima azione.
2. Se la modifica è non banale, `plan` e poi `impact`.
3. Implementa.
4. Fai eseguire test e controlli all'agente principale, o eseguili tu: il reviewer non li lancia.
5. `review`.
6. `handoff`.
7. Committa solo se hai deciso di farlo.

---

## 6. I workflow in dettaglio

Ogni workflow è una skill in `core/workflows/<nome>/SKILL.md` con `disable-model-invocation: true`: parte solo quando lo chiedi tu. Il testo che scrivi dopo il nome del workflow è l'argomento (obiettivo, area, scope).

### `start`

Prima adozione, o riallineamento dei fatti del progetto. **Scrive:** solo `AGENTS.md` e `.dev-brain/STATE.md`. Dettagli nella sezione 4.

### `resume`

**Quando:** all'inizio di una sessione, soprattutto dopo una pausa.

- legge stato e `AGENTS.md`, esegue `git status` e `git log`;
- se lo stato è vecchio, lo dice prima di proseguire;
- esegue un controllo registrato solo se è veloce e in sola lettura. Riporta come `NOT RUN`, senza eseguirlo, ciò che installa, scarica, compila o crea ambienti (`uv sync`, `pip install`, `npm install`, `uv run` senza `.venv`, `cargo test`, build complete);
- riporta obiettivo, ultimo risultato verificato, blocchi e una prossima azione.

**Scrive:** no. È un'istruzione al modello, non un blocco tecnico.

### `handoff`

**Quando:** alla fine di un lavoro significativo.

- ricostruisce cosa è successo davvero da diff, controlli e conversazione;
- riscrive lo stato: obiettivo, fatto con evidenza (massimo 5), blocchi, prossime azioni (massimo 3), meno di 3000 caratteri;
- aggiorna `AGENTS.md` solo se è cambiato un fatto stabile.

**Scrive:** lo stato. Non committa. Lo stato non è un diario: sostituisci le righe vecchie.

### `plan`

**Quando:** una modifica non banale, prima di scrivere codice. Produce un piano-contratto in sola lettura, massimo 5 passi. Ogni passo è un risultato concreto con file o simboli, input → output, dipendenze e un controllo che può fallire. Le decisioni che cambiano comportamento o dati ti vengono chieste prima.

Non cambia agente: dopo il piano puoi chiedere subito di implementare. Prima, in OpenCode, la sessione restava bloccata in modalità `plan`.

### `impact`

**Quando:** prima di cambiare un contratto, un formato, un dato persistito o codice condiviso. Analisi in sola lettura di consumatori, contratti a rischio, test e configurazione, file da modificare e da rivedere, controlli esistenti, incognite. Etichette `OBSERVED`, `INFERRED`, `UNKNOWN`.

### `learn`

**Quando:** devi capire un flusso, un componente o uno stack nuovo. Procede per strati: ambito, inventario, connessioni reali, un flusso concreto, ordine di lettura. Formato:

```text
Flow: <file:symbol> -> <file:symbol>: <cosa succede e quali dati passano> -> <file:symbol>: <risultato>
```

### `review`

**Quando:** prima di committare o aprire una PR.

- l'agente principale esegue `git status` e `git diff HEAD --stat`: nomi e conteggi, non il contenuto;
- delega al reviewer, che legge da solo le modifiche con git;
- riporta i risultati senza ammorbidirli.

Senza scope copre tutto ciò che non è committato: in staging, non in staging e file nuovi. Con uno scope (per esempio “ultimo commit”) il reviewer usa `git show` o `git log`.

**Perché così:** prima il diff completo entrava nel contesto principale, veniva ricopiato come output nel prompt del subagente e riletto dal reviewer: si pagava tre volte. Su un diff di 5,9 KB in hph il messaggio di review è sceso da 7005 a 1101 caratteri.

---

## 7. I due file di progetto

### `AGENTS.md`

Tutti e quattro gli agenti lo leggono nella radice del progetto. Contiene solo fatti che l'agente non può dedurre in fretta:

```markdown
# <Nome progetto>
<Una riga: cosa fa e per chi.>

## Stack
## Comandi        (con directory ed effetti collaterali)
## Struttura
## Convenzioni e gotcha
## Da non fare
```

Meno di 60 righe. Niente consigli generici (stanno nelle regole globali), niente path assoluti della tua macchina.

### `.dev-brain/STATE.md`

```markdown
# State — <progetto>
Updated: <data> · Branch: <branch>

## Goal
<una riga> — acceptance: <criteri osservabili>

## Done (latest first, max 5)
- <risultato> — evidence: <comando> PASS|FAIL|NOT RUN

## In progress / blockers
- <voce> — status: implemented|verified|blocked — <perché>

## Known pre-existing failures
- <comando> — <errore> — since <data>

## Next (max 3)
1. <azione eseguibile>
```

Regole: meno di 3000 caratteri (oltre viene iniettato solo un avviso); ogni voce “Done” ha un comando e un esito reale; `PASS` significa eseguito e passato; sostituisci le righe vecchie; niente dati sensibili; una sola sessione alla volta fa `handoff`.

---

## 8. Lo stato nel contesto dell'agente

Uno script unico, `core/bin/dev-brain-context`, produce il testo per tutti gli agenti:

- con uno stato valido: un blocco `<dev-brain-state>` con l'avviso che è contesto, non prova né permesso;
- oltre i 3000 caratteri: una riga che dice al modello di leggerlo quando serve e di proporti `handoff` per compattarlo. Non viene troncato, perché il taglio eliminerebbe proprio “Next”, che sta in fondo;
- in una repo git senza stato: una riga che suggerisce `start`, senza creare nulla;
- fuori da una repo: niente.

Come arriva all'agente:

- **OpenCode:** il plugin lo aggiunge a ogni chiamata della sessione principale; i subagenti non lo ricevono. Rilegge il file solo quando cambia. In compattazione chiede al riassunto di conservare obiettivo, evidenza, blocchi e prossima azione.
- **Claude Code:** hook `SessionStart` all'avvio, al resume, dopo `/clear` e dopo la compattazione.
- **Codex:** stesso hook, dopo la tua approvazione nella TUI.
- **Cursor:** hook `sessionStart`. Cursor ha un bug aperto che scarta questo contesto, quindi vale la regola di riserva.

Per disattivarlo in una repository, rinomina `.dev-brain/STATE.md`.

---

## 9. Regole, permessi e sicurezza

Le regole globali vivono in `core/AGENTS.md`.

### Precedenza

```text
correttezza > sicurezza e integrità dei dati > compatibilità col progetto > manutenibilità > semplicità > prestazioni misurate
```

### Qualità del codice, sempre attiva

- la soluzione più semplice che soddisfa davvero i requisiti, non quella con meno righe; niente funzionalità ipotetiche;
- idiomi del linguaggio e convenzioni del progetto, senza imporre classi o livelli;
- nomi che esprimono l'intento, responsabilità coese, effetti espliciti; divisione per responsabilità;
- una sola fonte per la stessa regola di business, senza accoppiare concetti diversi solo perché il codice si assomiglia;
- contratti e gestione degli errori preservati, niente fallback silenziosi;
- rilettura del codice modificato prima della consegna, senza refactor estranei.

### Autorizzazione

- leggere o adottare una repository non autorizza modifiche;
- nessun commit, amend o push se non lo decidi tu; implementare, testare, fare review o handoff non è un permesso di commit;
- nessun cambio di branch, operazione distruttiva, migrazione, deploy o pubblicazione senza un permesso esplicito;
- il lavoro non committato si preserva; niente pulizie non richieste;
- niente letture di segreti, dati personali o clinici senza necessità.

### Test, debug e reporting

- per un bug o un comportamento nuovo, prima un test mirato che fallisce per il motivo giusto;
- dopo 3 tentativi equivalenti falliti, fermarsi e riportare;
- ogni controllo come `PASS`, `FAIL`, `NOT RUN` o `N/A`, con il comando reale; “implementato” non è “verificato”;
- la spiegazione dettagliata (Flow / Why / Checks / Read next) solo se la chiedi: consuma token.

### Cosa significa “permesso”

Che hai chiesto esplicitamente quell'azione. Non basta che sia utile. Il kit non modifica le permission globali dei tuoi agenti: impone restrizioni solo al reviewer.

---

## 10. Le skill

Il modello le carica quando il compito corrisponde alla descrizione; puoi anche chiederle per nome.

| Skill | Quando | Cosa impone |
| --- | --- | --- |
| `debugging` | Bug, test che fallisce, comportamento inatteso | Riprodurre, localizzare, ipotizzare, testare, correggere la causa, verificare |
| `review-feedback` | Commenti di review o findings di un altro agente | Classificare ogni commento prima di implementarlo |
| `engineering-risk` | Auth, input, segreti, dati persistiti, migrazioni, concorrenza, servizi esterni, prestazioni | Leggere solo il riferimento pertinente |

`review-feedback` classifica in `SUPPORTED` (correggi con un controllo), `UNSUPPORTED` (rispondi con l'evidenza), `NEEDS CONTEXT` (fai la domanda), `OUT OF SCOPE` (registra e proponi a parte).

---

## 11. Il reviewer

Subagente indipendente, in sola lettura. Riporta difetti di correttezza, sicurezza, integrità dei dati o requisiti, separati dai problemi concreti di manutenibilità. Per ogni finding: `file:line`, trigger o scenario di manutenzione, impatto, correzione minima, confidenza. Niente preferenze cosmetiche. Se non trova nulla, lo dice.

Quanto è davvero “in sola lettura” dipende dall'agente (verificato nel controllo offline):

- **OpenCode:** imposto. Sono permessi solo `git diff`, `git log`, `git show`, `git status`. Bloccati `>`, `--output` e i comandi concatenati che contengono altro. OpenCode non blocca da solo la redirezione `>`, per questo c'è una regola esplicita.
- **Claude Code:** imposto con una lista di strumenti. Ogni comando che crea o modifica file chiede la tua approvazione: rispondi no.
- **Codex:** solo istruzione. Il file del reviewer dichiara `sandbox_mode = "read-only"`, ma Codex 0.164 non lo applica ai subagenti generati: con il genitore in `workspace-write` il reviewer ha scritto un file nel test.
- **Cursor:** `readonly: true`, che secondo la documentazione blocca modifiche e comandi che cambiano lo stato. Non provato.

Non esegue test o build e non conosce l'intento se non è nello scope.

---

## 12. Manutenzione del kit

### Struttura

```text
core/         unica fonte: AGENTS.md, workflows/, skills/, agents/reviewer.md, bin/, templates/
adapters/     codice specifico che non si può esprimere come file (plugin OpenCode)
install.py    collega o traduce core/ per ogni agente; install.sh è un wrapper
evals/        scenari, fixture, risultati, controllo offline
MANUALE.md    questo manuale
```

### Modificare il kit

1. Una modifica piccola e mirata, in `core/` se riguarda il comportamento del modello.
2. Se cambia il comportamento, esegui gli scenari in `evals/scenarios/` e registra il baseline.
3. Applica la modifica e riesegui gli stessi scenari.
4. Esegui `python3 evals/offline/check.py`.
5. Tieni la modifica solo se migliora uno scenario o rimuove un costo reale; registra l'esito in `evals/results.md`.

Non aggiungere regole per intuizione: una regola che il modello già segue è solo costo di contesto. Niente sintassi specifica di un agente in `core/` (`$ARGUMENTS`, espansioni `!`).

### Controllo offline, a costo zero

```bash
python3 evals/offline/check.py        # OPENCODE / CLAUDE / CODEX=<binario> se non sono nel PATH
```

Per ogni CLI trovata installa il kit in una home temporanea e sostituisce il modello con un server locale finto che registra ogni richiesta. In circa 10 secondi, senza spendere token, verifica:

- regole globali caricate;
- stato nella sessione principale (e non nei subagenti, in OpenCode);
- stato troppo lungo sostituito dall'avviso;
- workflow che si espandono;
- reviewer che legge il diff ma non scrive.

Per Cursor controlla solo i file generati. Non valuta la qualità delle risposte: per quella restano gli scenari.

### Scenari con un modello reale

```bash
# Solo dopo aver autorizzato i commit locali delle fixture:
./evals/setup.sh
cd /tmp/opencode/dev-brain-evals/bugfix
opencode run --standalone -m <provider/model> "The discount test fails. Fix the code." < /dev/null
```

Negli script chiudi lo stdin (`< /dev/null`): `opencode run` legge lo stdin quando non è un terminale e resta in attesa.

### Backup

- i file non gestiti vengono salvati come `*.bak.<timestamp>`;
- il kit è referenziato con percorso assoluto: se sposti la cartella, riesegui l'installer;
- non copiare fatti di progetto nel repository del kit.

---

## 13. Problemi e domande frequenti

| Sintomo | Causa e soluzione |
| --- | --- |
| OpenCode: i comandi non compaiono o una modifica non ha effetto | `opencode service restart` quando non hai sessioni attive; apri una nuova sessione |
| OpenCode: `opencode run "/resume"` non espande il comando | Limite della CLI: usa la TUI |
| Uno script con `opencode run` resta fermo | Aggiungi `< /dev/null` |
| Claude Code: `/review` apre la review integrata | Usa `/dev-brain:review`: i comandi integrati hanno la precedenza |
| Codex: lo stato non arriva | Approva l'hook `SessionStart` nella TUI; nel frattempo vale la regola di riserva |
| Codex: dopo un aggiornamento vedo la versione vecchia | Riesegui `./install.sh codex`: Codex usa una copia del plugin |
| Cursor: le regole non vengono applicate | Incolla `core/AGENTS.md` in Settings > Rules |
| Lo stato non viene iniettato | Controlla che `.dev-brain/STATE.md` sia nella radice, non vuoto, sotto i 3000 caratteri; i subagenti non lo ricevono per scelta |
| Lo stato cresce troppo | Arriva solo l'avviso: compattalo con `handoff` |
| Il reviewer chiede di eseguire un comando che scrive | Rispondi no: il reviewer è in sola lettura |
| L'installer ha spostato un mio file | Cerca `<nome>.bak.<timestamp>` e unisci il contenuto |
| Un file JSON non viene aggiornato | Contiene commenti o non è JSON valido: l'installer non lo tocca e lo segnala; aggiungi la voce a mano |
| Ho dati clinici o segreti nello stato | Rimuovili subito, valuta la rotazione delle credenziali, non committare: lo stato viene inviato al provider |

---

## 14. Limiti noti

- Le prove con modelli reali usano fixture piccole e pochi run; i risultati dipendono dal modello. Dettagli in `evals/results.md`.
- Il controllo offline verifica cosa il kit invia e permette, non la qualità delle risposte.
- La nuova architettura multi-agente non è ancora stata provata con un modello reale, né nelle TUI.
- Cursor non è stato eseguito: i suoi file sono generati secondo la documentazione e controllati solo per presenza.
- Codex: il reviewer in sola lettura è solo un'istruzione (`sandbox_mode` non applicato ai subagenti in 0.164).
- Le regole sono contesto: il modello può non seguirle. Workflow e skill riducono la variabilità, non la eliminano.
- `resume` dipende dal rispetto delle istruzioni di sola lettura.
- Codex elenca anche i workflow tra le skill (non rispetta `disable-model-invocation`): circa 1200 caratteri (~300 token) in più nel prompt di sistema.
- Una sola sessione dovrebbe aggiornare lo stato alla volta.
- Non c'è uno script di disinstallazione.

---

## 15. Checklist

- [ ] `./install.sh` eseguito senza errori
- [ ] `python3 evals/offline/check.py` stampa `ALL PASS`
- [ ] OpenCode: server riavviato; Codex: hook approvato; Cursor: regole visibili in Settings
- [ ] `start` eseguito su almeno una repository
- [ ] `AGENTS.md` sotto 60 righe, senza path assoluti né dati sensibili
- [ ] `.dev-brain/STATE.md` sotto 3000 caratteri, con evidenza reale
- [ ] I due file di progetto revisionati; eventuale commit separato, solo per tua decisione
- [ ] `resume`, `review` e `handoff` provati in una sessione reale con ogni agente che usi
- [ ] Nessun dato clinico, personale o segreto in stato, istruzioni o chat
