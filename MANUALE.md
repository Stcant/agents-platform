# dev-brain — Manuale d'uso

> Manuale utente in italiano; il resto del kit è in inglese. Versione 2026-11-23, plugin 2.4.0, provato su Claude Code 2.1.325 e OpenCode 2.3.2. Indipendente dal provider del modello.

## Avvio rapido

```bash
claude plugin marketplace add Stcant/agents-platform
claude plugin install dev-brain@dev-brain
```

Poi, nella radice di ogni repository, una volta sola:

```text
/dev-brain:start
```

Da lì: `resume` a inizio sessione → lavoro → `review` → `handoff` a fine lavoro. Le regole di qualità valgono anche senza nessun workflow.

---

## 1. Cos'è

Un plugin per Claude Code, con un adattatore per OpenCode (sezione 12). Fa tre cose:

1. **Regole globali** in ogni sessione: soluzione più semplice e completa, idiomi del progetto, una sola fonte per ogni regola di business, errori mai nascosti, niente commit senza la tua decisione, controlli riportati come PASS / FAIL / NOT RUN.
2. **Continuità**: lo stato del progetto (`.dev-brain/STATE.md`) arriva in ogni sessione, anche dopo `/clear` e dopo la compattazione.
3. **Workflow e reviewer**: procedure ripetibili per adottare una repo, riprendere, chiudere, analizzare l'impatto, capire un flusso e fare review in sola lettura.

Non decide quando committare, non sostituisce test né la tua revisione, e non garantisce che il modello segua le regole: le regole sono contesto. Imposti davvero dallo strumento sono tre vincoli: nessun commit senza di te, il reviewer in sola lettura e il budget dello stato.

---

## 2. Installazione

Prerequisiti: Claude Code (o OpenCode, sezione 12), `python3`, `git`.

```bash
claude plugin marketplace add Stcant/agents-platform
claude plugin install dev-brain@dev-brain
```

- **Aggiornamento:** `claude plugin marketplace update dev-brain`.
- **Sviluppo locale:** `claude plugin marketplace add /percorso/agents-platform`. Il plugin viene letto sul posto: le modifiche valgono dalla sessione successiva.
- **Disinstallazione:** `claude plugin uninstall dev-brain@dev-brain`. I file nelle repository restano.
- **OpenCode:** installazione, aggiornamento e rimozione sono nella sezione 12.

Il plugin non tocca `CLAUDE.md` né le tue impostazioni: regole e stato arrivano da un hook `SessionStart`.

**Verifica:** `python3 evals/offline/check.py` dalla cartella del kit deve stampare `ALL PASS` (sezione 9).

---

## 3. Primo passo in ogni repository: `/dev-brain:start`

Crea o aggiorna due file:

```text
<repo>/
├── AGENTS.md            comandi, strumenti e trappole del progetto, meno di 40 righe (Claude Code lo legge da solo)
└── .dev-brain/
    └── STATE.md         obiettivo, fatto, blocchi, prossime azioni, meno di 3000 caratteri
```

Cosa fa:

- legge codice, configurazione, README e comandi reali;
- integra un `AGENTS.md` esistente preservandone le istruzioni;
- riconcilia uno stato esistente invece di sovrascriverlo;
- usa i file del vecchio kit (`harness/`, `NOW.md`, `RULES.md`) come fonte e te li elenca da eliminare;
- scrive l'`AGENTS.md` come bozza: solo comandi, strumenti e trappole, senza scopo, elenco dello stack o panoramica dell'architettura (gli studi li trovano costosi e inutili);
- elenca le righe di un `AGENTS.md` esistente che ripetono ciò che il codice già mostra, come candidate da eliminare (non le cancella);
- se vede nomi come `.env` o `input/`, stampa le regole `deny` da aggiungere tu alle impostazioni di permesso, senza aprire quei percorsi e senza modificare impostazioni;
- se trova un controllo veloce (typecheck, lint, un test rapido), stampa la riga di Stop hook da aggiungere tu alle impostazioni del progetto, perché un turno non possa finire finché il controllo non passa;
- riporta fatti, incognite e problemi.

Non tocca codice, dipendenze o git, e non installa nulla. Non apre directory con dati personali, clinici o segreti (`input/`, `output/`, `.env`).

Dopo: rileggi i due file, elimina le righe che il codice mostra già, correggi ciò che non è vero, e committali tu se vuoi versionarli. Esempio reale: in hph i 21 KB di `harness/` sono diventati 4,4 KB (PR #10 su hph).

---

## 4. I workflow

Si invocano con `/dev-brain:<nome>`. Il testo dopo il nome è l'argomento. Non costano contesto finché non li usi (`disable-model-invocation`).

| Workflow | Quando | Scrive |
| --- | --- | --- |
| `start` | Prima adozione | `AGENTS.md`, stato |
| `resume` | Inizio sessione: riconcilia lo stato con git e codice, riporta obiettivo, ultimo risultato verificato, blocchi, una prossima azione | No |
| `handoff` | Fine lavoro: riscrive lo stato con evidenza fresca (massimo 5 “Done”, 3 “Next”, meno di 3000 caratteri) | Stato |
| `impact <modifica>` | Prima di toccare codice condiviso: consumatori, contratti, test, incognite (OBSERVED / INFERRED / UNKNOWN) | No |
| `learn <area>` | Capire un flusso o uno stack: catena reale di file e simboli, ordine di lettura | No |
| `review [scope]` | Prima di committare: delega al reviewer tutte le modifiche non committate | No |

**Pianificazione:** usa il **plan mode** nativo (Shift+Tab). È in sola lettura per costruzione, cosa che un workflow scritto come prompt non può garantire. Per questo il workflow `plan` è stato rimosso.

**`resume`** esegue un controllo registrato solo se è veloce e in sola lettura. Riporta come `NOT RUN` ciò che installa, scarica o compila (`npm install`, `uv sync`, `cargo test`…).

**`review`** passa al reviewer solo nomi e conteggi dei file: il diff lo legge lui con git. Prima il diff si pagava tre volte. Su un diff di 5,9 KB il messaggio è sceso da 7005 a 1101 caratteri. Se lo stato contiene un obiettivo con criteri di accettazione, glieli passa come requisiti da verificare; il reviewer controlla anche che nessun test sia stato cancellato, saltato o indebolito per far passare la modifica.

---

## 5. Nessun commit senza di te

La regola globale vieta commit, push, cambi di branch e comandi git distruttivi senza una tua decisione esplicita. Un hook `PreToolUse` la **impone**: prima di ogni comando Bash controlla se contiene uno di questi e, se sì, Claude Code ti chiede conferma.

- `git commit` (anche `--amend`), `push`, `merge`, `rebase`, `cherry-pick`, `revert`, `am`;
- `checkout`, `switch`;
- `reset` che sposta il branch (`--hard`, `--soft`, `HEAD~1`…);
- `clean -f`, `branch -d/-D/-m/-f`, `stash drop/pop/clear`, `tag -d/-f`.

Vale anche dentro comandi concatenati (`git add -A && git commit …`), con opzioni globali (`git -C dir commit`), e anche se nelle tue impostazioni hai permesso git: la richiesta arriva comunque. I comandi in sola lettura (`status`, `diff`, `log`, `show`, `stash`, `reset <file>`) passano senza chiedere.

Se rispondi sì, il commit avviene: la decisione resta tua, ed è il punto. Su OpenCode la richiesta compare nel TUI (la richiesta interattiva non è stata provata) e `opencode run` rifiuta (sezione 12).

---

## 6. Il reviewer

Subagente `dev-brain:reviewer`, in sola lettura **imposta**. Può usare Read, Grep, Glob e `git diff/log/show/status`; ogni comando che crea, modifica o cancella file chiede la tua approvazione. Rispondi no.

Riporta difetti di correttezza, sicurezza, integrità dei dati o requisiti, separati dai problemi concreti di manutenibilità. Per ogni finding: `file:line`, trigger o scenario, impatto, correzione minima, confidenza. Niente preferenze cosmetiche. Non esegue test o build: li riporta come `NOT RUN`.

---

## 7. Le skill

Il modello le carica quando servono; puoi anche chiederle per nome.

| Skill | Quando | Metodo |
| --- | --- | --- |
| `debugging` | Bug, test che fallisce | Riprodurre, localizzare, ipotizzare, testare, correggere la causa, verificare |
| `engineering-risk` | Auth, input, segreti, dati persistiti, migrazioni, concorrenza, prestazioni | Solo il riferimento pertinente: sicurezza, dati, prestazioni |
| `review-feedback` | Commenti di review | Classifica: SUPPORTED, UNSUPPORTED, NEEDS CONTEXT, OUT OF SCOPE |

---

## 8. Lo stato

Formato di `.dev-brain/STATE.md`:

```markdown
# State — <progetto>
Updated: <data>

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

Arriva in ogni sessione insieme alle regole: all'avvio, al resume, dopo `/clear`, dopo la compattazione. Sopra i 3000 caratteri arriva solo un avviso che chiede di compattarlo con `handoff`. Non viene troncato, perché il taglio eliminerebbe proprio “Next”. In una repo senza stato arriva una riga che suggerisce `start`.

Regole: evidenza reale con comando, righe vecchie sostituite (non è un diario), né branch, né commit corrente, né “non committato” (git li ha, e lo stato di solito viene committato insieme al lavoro: quelle righe diventano false), nessun dato sensibile (viene inviato al provider), una sola sessione alla volta fa `handoff`. Per disattivarlo in una repo, rinomina il file.

---

## 9. Manutenzione del kit

```text
.claude-plugin/marketplace.json   elenca il plugin
core/                             il plugin: AGENTS.md, skills/, agents/, hooks/, bin/
evals/                            scenari, fixture, risultati, controllo offline
```

Per modificare il kit:

1. Una modifica piccola, motivata da un fallimento osservato.
2. Scenari prima e dopo (`evals/scenarios/`), più `python3 evals/offline/check.py`.
3. Tienila solo se migliora qualcosa o toglie un costo reale.
4. Alza `version` in `core/.claude-plugin/plugin.json` e registra la decisione in `evals/results.md`.

Il **controllo offline** installa il plugin in una home temporanea e sostituisce il modello con un server locale finto che registra ogni richiesta. In circa 15 secondi, senza token, verifica:

- regole e stato nella sessione;
- avviso per lo stato troppo lungo;
- workflow che si espandono e restano fuori dall'elenco delle skill;
- reviewer che legge il diff ma non scrive;
- commit e push che chiedono conferma anche con git permesso nelle impostazioni.

Se trova `opencode` nel PATH (o nella variabile `OPENCODE`, che in quel caso lo rende obbligatorio) ripete su di esso gli stessi controlli attraverso l'adattatore, più uno: regole e stato non devono arrivare al subagente.

Non valuta la qualità delle risposte. Su GitHub Actions gira a ogni pull request sulle versioni fissate (Claude Code 2.1.325, OpenCode 2.3.2); a ogni push su `main`, ogni lunedì e su richiesta gira anche sulle ultime versioni, per accorgersi presto di un cambiamento.

`core/AGENTS.md` e le skill restano in formati standard. OpenCode si supporta con un adattatore (`adapters/opencode/index.ts`, sezione 12) che non copia nessuna regola; un altro agente richiede un altro adattatore, non una riscrittura.

---

## 10. Problemi frequenti

| Sintomo | Soluzione |
| --- | --- |
| `/review` apre la review integrata (alias di `/code-review`, che cerca bug e può applicare correzioni) | Usa `/dev-brain:review`: i comandi integrati hanno la precedenza; la nostra è in sola lettura imposta e riporta anche problemi di manutenibilità |
| Lo stato non arriva | File nella radice, non vuoto, sotto 3000 caratteri; `python3` disponibile; nuova sessione |
| Dopo un aggiornamento vedo la versione vecchia | `claude plugin marketplace update dev-brain` e nuova sessione |
| Il reviewer chiede di eseguire un comando che scrive | Rispondi no |
| Claude Code chiede conferma per un `git commit` | È il guard di dev-brain: conferma solo se hai deciso tu di committare |
| Ho dati sensibili nello stato | Rimuovili subito; non committare |
| OpenCode: regole e stato non arrivano | Controlla che `plugins` contenga il percorso assoluto di `adapters/opencode`, che `python3` sia installato e che `opencode debug agents` elenchi `reviewer` |
| OpenCode rifiuta un `git commit` in `opencode run` | È voluto: `run` non può chiedere conferma; esegui il commit tu o usa il TUI |

---

## 11. Limiti noti

- L'effetto delle regole sulla qualità del codice **non è misurato** con un modello reale: le prove esistenti sono poche e sintetiche (`evals/results.md`). È il prossimo lavoro da fare.
- Il controllo offline verifica cosa il kit invia e permette, non le risposte.
- Il reviewer chiede approvazione per le scritture: se approvi, scrive.
- Le regole costano circa 1200 token per sessione; se rendano non è ancora dimostrato.
- OpenCode è provato solo con il modello finto e con `opencode run`; il TUI non è stato eseguito (sezione 12).

---

## 12. OpenCode

OpenCode non ha un marketplace di plugin: un solo file, `adapters/opencode/index.ts`, lo collega allo stesso `core/`. Lancia gli script `dev-brain-context` e `dev-brain-guard` del plugin e costruisce il reviewer da `core/agents/reviewer.md`: nessuna regola è copiata. Provato con il programma reale contro il modello finto, non con un modello vero.

**Installazione**

```bash
git clone https://github.com/Stcant/agents-platform /percorso/agents-platform
```

Poi in `~/.config/opencode/opencode.json` (o nell'`opencode.json` di un progetto), con percorso assoluto:

```json
{ "plugins": ["/percorso/agents-platform/adapters/opencode"] }
```

- **Verifica:** `opencode debug agents` deve elencare `reviewer`.
- **Aggiornamento:** `git -C /percorso/agents-platform pull`, poi riavvia OpenCode; se `opencode service status` mostra un server in background attivo, riavvia anche quello con `opencode service restart` (qui ogni nuovo `opencode run` rileggeva i file modificati, ma un server rimasto acceso a lungo NON è stato provato).
- **Rimozione:** togli la voce da `plugins`.

| | Claude Code | OpenCode |
| --- | --- | --- |
| Regole e stato | ogni sessione | solo sessione principale, non i subagenti |
| Workflow | `/dev-brain:start` | `@start` nel prompt, oppure chiedi di caricare la skill `start` (la skill si carica per id: provato; la forma `@` segue la documentazione di OpenCode e NON è provata, serve il TUI) |
| Costo di contesto dei workflow | nullo | nullo: non compaiono nell'elenco delle skill |
| Commit, push, cambio di branch | chiede conferma | chiede conferma (la richiesta interattiva NON è stata provata); `opencode run` non può chiedere e rifiuta; `opencode run --auto` approva |
| Reviewer | sola lettura, legge il diff con git | sola lettura, legge il diff con git; redirezioni e `--output` sono negati per nome perché il filtro dei comandi di OpenCode non le interpreta |

**`--auto` annulla la guardia.** `opencode run --auto` approva ogni richiesta, comprese quelle di dev-brain: usalo solo dove accetti commit e push senza controllo.

Versioni provate: OpenCode 2.3.2 (qui e in CI) e 2.4.0 (in CI, l'ultima al momento della scrittura), con la loro API plugin V2; OpenCode 1.x NON è stato provato. I nomi dei workflow in questo manuale sono quelli di Claude Code (`/dev-brain:<nome>`): su OpenCode usa il nome nudo (`@start`).
