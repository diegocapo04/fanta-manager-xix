# FantaManager XIX — Documentazione del Progetto

## Panoramica

FantaManager XIX è un'applicazione web per la gestione di una lega di fantacalcio manageriale,
sviluppata con **Streamlit** (frontend), **MySQL** (database) e **Docker** (infrastruttura).
Il sistema gestisce squadre, giocatori, contratti, mercato, calendario partite e contabilità
in modo completamente autonomo rispetto alle piattaforme esterne.

---

## Stack Tecnologico

| Componente   | Tecnologia                        |
|--------------|-----------------------------------|
| Frontend     | Streamlit 1.40.0                  |
| Database     | MySQL 8.0                         |
| ORM / DB     | SQLAlchemy 2.0 + PyMySQL          |
| Grafici      | Plotly 5.18.0                     |
| Container    | Docker + Docker Compose           |
| Auth         | SQLite locale (users.db)          |

---

## Struttura del Progetto

```
fanta-manager-xix/
├── compose.yaml
├── .env                            # Variabili d'ambiente (non committare)
├── nginx.conf                      # Config Nginx per reverse proxy (non attivo)
├── db/
│   ├── struct.sql              # Schema del database (solo struttura, senza dati)
│   └── init.sql                # Schema + dati iniziali (usato da Docker al primo avvio)
└── web/
    ├── Dockerfile
    ├── requirements.txt
    ├── utils.py                # Connessione DB, autenticazione, funzioni comuni
    ├── Home.py                 # Pagina principale Streamlit
    └── pages/
        ├── 1_Rose.py           # Visualizzazione rose delle squadre
        ├── 2_Mercato.py        # Mercato pubblico (visualizzazione)
        ├── 3_Info.py           # Dettagli club e infrastrutture
        ├── 4_Statistiche.py    # Statistiche e classifiche
        ├── 5_Admin_Mercato.py  # [ADMIN] Gestione giocatori e contratti
        ├── 6_Admin_Gestione_Squadre.py  # [ADMIN] Squadre, stadi, vivai
        ├── 7_Admin_Campionato.py        # [ADMIN] Calendario e risultati
        └── 8_Admin_Fine_Stagione.py     # [ADMIN] Chiusura stagione
```

---

## Configurazione Iniziale

### 1. Clona il repository e crea il file `.env`

```bash
git clone <repo-url> fanta-manager-xix
cd fanta-manager-xix
```

Crea il file `.env` nella root del progetto:

```env
MYSQL_ROOT_PASSWORD=rootpassword
MYSQL_DATABASE=fantamanagerxix
MYSQL_USER=fantauser
MYSQL_PASSWORD=fantapassword

DB_NAME=fantamanagerxix
DB_USER=fantauser
DB_PASSWORD=fantapassword
```

### 2. Avvia i container

```bash
docker compose up --build -d
```

L'applicazione sarà disponibile su `http://localhost:8501`.

### 3. Credenziali di accesso default

| Utente   | Password   | Ruolo |
|----------|------------|-------|
| `admin`  | `admin123` | Admin |
| `utente` | `user123`  | User  |

> ⚠️ Cambiare le password di default prima dell'uso in produzione.

---

## Schema Database

### Tabelle principali

#### `giocatori`
Contiene l'anagrafica di tutti i calciatori nel sistema.

| Colonna          | Tipo               | Note                     |
|------------------|--------------------|--------------------------|
| `ID`             | INT AUTO_INCREMENT | Chiave primaria          |
| `Nome`           | VARCHAR(50)        |                          |
| `Cognome`        | VARCHAR(50)        | Indicizzato              |
| `Ruolo`          | ENUM(P,D,C,A)      |                          |
| `ValoreMercato`  | DECIMAL(12,2)      | In unità FM              |

#### `fantasquadre`
Le squadre partecipanti alla lega.

| Colonna          | Tipo          | Note                 |
|------------------|---------------|----------------------|
| `ID`             | INT           | Chiave primaria      |
| `Nome`           | VARCHAR(50)   | Unico                |
| `CreditiResidui` | DECIMAL(10,2) | Budget attuale in FM |

#### `contratti`
Lega giocatori e squadre con i termini contrattuali.

| Colonna           | Tipo          | Note                              |
|-------------------|---------------|-----------------------------------|
| `SquadraID`       | INT FK        | → `fantasquadre`                  |
| `GiocatoreID`     | INT FK        | → `giocatori`                     |
| `StagioneFirma`   | VARCHAR(9)    | Es. `2025/2026`                   |
| `AnniDurata`      | INT           | Anni rimanenti                    |
| `Stipendio`       | DECIMAL(10,2) | Costo annuale in FM               |
| `CostoAcquisto`   | DECIMAL(10,2) | Costo pagato all'ingaggio         |
| `PrimaSquadra`    | TINYINT(1)    | 1 = prima squadra, 0 = vivaio     |
| `SettoreGiovanile`| TINYINT       | 1 = giovane di proprietà          |

#### `competizioni`
Le competizioni della lega, una per stagione.

| Colonna    | Tipo                        | Note                                      |
|------------|-----------------------------|-------------------------------------------|
| `ID`       | INT                         | Chiave primaria                           |
| `Nome`     | VARCHAR(50)                 |                                           |
| `Stagione` | VARCHAR(9)                  | Es. `2025/2026` — chiave univoca          |
| `Tipo`     | ENUM('Campionato','Coppa')  | Determina il metodo di assegnazione premi |

> `UNIQUE KEY` su `(Nome, Stagione)` — ogni competizione è unica per stagione.

#### `premi_competizioni`
Premi per fase di ogni competizione. Per il Campionato la `Fase` è la posizione in classifica (`'1'`–`'10'`); per le coppe è il turno raggiunto (`'Quarti'`, `'Semifinale'`, ecc.). I premi delle coppe sono **cumulativi**: chi vince riceve la somma di tutte le fasi.

| Colonna          | Tipo          | Note                                                               |
|------------------|---------------|--------------------------------------------------------------------|
| `ID`             | INT           | Chiave primaria                                                    |
| `CompetizioneID` | INT FK        | → `competizioni`                                                   |
| `Fase`           | VARCHAR(50)   | Posizione ('1'–'10') per Campionato; fase per Coppe                |
| `Premio`         | DECIMAL(12,2) | FM assegnati per questa singola fase                               |
| `Ordine`         | INT           | Gerarchia della fase (1 = prima fase, N = finale/vittoria)         |

Premi configurati per stagione 2025/2026:

| Competizione     | Fase       | Premio  | Cumulato |
|------------------|------------|---------|----------|
| Campionato       | 1° posto   | 35 FM   | 35 FM    |
| Campionato       | 2° posto   | 28 FM   | 28 FM    |
| Campionato       | 3° posto   | 21 FM   | 21 FM    |
| Campionato       | 4°–10°     | …       | …        |
| Champions League | Quarti     | 5 FM    | 5 FM     |
| Champions League | Semifinale | 5 FM    | 10 FM    |
| Champions League | Finale     | 5 FM    | 15 FM    |
| Champions League | Vittoria   | 15 FM   | 30 FM    |
| Europa League    | Quarti     | 2.5 FM  | 2.5 FM   |
| Europa League    | Semifinale | 2.5 FM  | 5 FM     |
| Europa League    | Finale     | 5 FM    | 10 FM    |
| Europa League    | Vittoria   | 10 FM   | 20 FM    |
| Coppa Italia     | Ottavi     | 2 FM    | 2 FM     |
| Coppa Italia     | Quarti     | 2 FM    | 4 FM     |
| Coppa Italia     | Semifinale | 4 FM    | 8 FM     |
| Coppa Italia     | Finale     | 4.5 FM  | 12.5 FM  |
| Coppa Italia     | Vittoria   | 12.5 FM | 25 FM    |

#### `partite`
Risultati e guadagni per ogni incontro.

| Colonna           | Tipo          | Note                          |
|-------------------|---------------|-------------------------------|
| `CompetizioneID`  | INT FK        | → `competizioni`              |
| `Stagione`        | VARCHAR(9)    |                               |
| `Giornata`        | INT           |                               |
| `SquadraCasaID`   | INT FK        | → `fantasquadre`              |
| `SquadraOspiteID` | INT FK        | → `fantasquadre`              |
| `GolCasa`         | INT           |                               |
| `GolOspite`       | INT           |                               |
| `Giocata`         | TINYINT(1)    | 0 = schedulata, 1 = giocata   |
| `GuadagnoCasa`    | DECIMAL(12,2) | FM guadagnati dalla casa      |
| `GuadagnoOspite`  | DECIMAL(12,2) | FM guadagnati dall'ospite     |

> `UNIQUE KEY uq_partita` su `(CompetizioneID, Stagione, Giornata, SquadraCasaID, SquadraOspiteID)`.

#### `operazioni_mercato`
Log di tutte le operazioni di mercato.

| Colonna       | Tipo                    | Note                          |
|---------------|-------------------------|-------------------------------|
| `Stagione`    | VARCHAR(9)              |                               |
| `Sessione`    | ENUM(Estiva, Invernale) |                               |
| `SquadraID`   | INT FK                  |                               |
| `GiocatoreID` | INT FK                  |                               |
| `Tipo`        | VARCHAR(100)            | Es. `Acquisto`, `Cessione`... |
| `Costo`       | DECIMAL(10,2)           | Positivo = guadagno           |
| `Note`        | TEXT                    | Formula usata o descrizione   |

#### `stadi`
Un record per squadra (relazione 1:1).

| Colonna         | Tipo          | Note                         |
|-----------------|---------------|------------------------------|
| `ID`            | INT PK        | Chiave primaria auto         |
| `SquadraID`     | INT FK        | → `fantasquadre`, unico      |
| `Livello`       | INT           | Default 1, max consigliato 5 |
| `IncassoPartita`| DECIMAL(12,2) | FM per ogni partita casalinga|
| `Costo`         | DECIMAL(12,2) | Valore asset dell'impianto   |

#### `settori_giovanili`
Slot per i giovani di proprietà.

| Colonna                | Tipo          | Note            |
|------------------------|---------------|-----------------|
| `SquadraID`            | INT FK        | → `fantasquadre`|
| `SlotMax`              | INT           | Default 5       |
| `SlotAcquistati`       | INT           | Slot attivi     |
| `CostoPerSlot`         | DECIMAL(12,2) | Default 20 FM   |
| `StipendioFissoGiovani`| DECIMAL(12,2) | Default 0.10 FM |

#### `configurazione`
Parametri globali del sistema.

| Chiave              | Valore esempio |
|---------------------|----------------|
| `stagione_corrente` | `2025/2026`    |

---

## Logica di Business

### Sistema Crediti (FM — FantaMonete)

Ogni squadra opera con un budget in **FM (FantaMonete)**. I movimenti sono:

| Evento               | Effetto sul budget              |
|----------------------|---------------------------------|
| Acquisto giocatore   | `− costo cartellino`            |
| Partita vinta        | `+ 0.50 FM`                     |
| Partita pareggiata   | `+ 0.25 FM`                     |
| Partita persa        | `+ 0.10 FM`                     |
| Gol segnato          | `+ 0.50 FM × numero gol`        |
| Partita in casa      | `+ incasso stadio`              |
| Premio competizione  | `+ premio posizione finale`     |
| Fine stagione        | `− somma stipendi annuali`      |
| Acquisto slot vivaio | `− 20.00 FM`                    |

### Tipi di Svincolo

| Tipo                   | Formula impatto budget                                   |
|------------------------|----------------------------------------------------------|
| Svincolo Ordinario     | `−(50% × valore) − (anni_rimasti × stipendio)`          |
| Svincolo Straordinario | `+(50% × valore) − (anni_rimasti × stipendio)`          |
| Addio Serie A          | `+valore − (1 anno × stipendio)`                        |
| Scadenza Contratto     | `0` — nessun impatto                                     |

### Rollover di Fine Stagione

Eseguito dalla pagina `8_Admin_Fine_Stagione.py`, in transazione atomica:

1. **Deduzione stipendi** — sottrae la somma degli stipendi attivi dal budget di ogni squadra
2. **Decremento contratti** — `AnniDurata = AnniDurata - 1` su tutti i contratti
3. **Pulizia scaduti** — elimina i contratti con `AnniDurata <= 0`
4. **Avanzamento stagione** — aggiorna `configurazione.Valore` alla stagione successiva

> L'operazione è atomica: se un qualsiasi step fallisce, MySQL esegue il rollback completo.

---

## Funzionalità per Pagina

### `Home.py`
- Dashboard principale con riepilogo generale della lega
- Classifica live delle squadre

### `1_Rose.py`
- Visualizzazione rosa per squadra (prima squadra + vivaio)
- KPI: monte ingaggi, budget residuo, investimento totale
- Grafico a torta ripartizione ingaggi per ruolo

### `2_Mercato.py`
- Vista pubblica del mercato: giocatori svincolati disponibili
- Filtrabile per ruolo

### `3_Info.py`
- Dettagli infrastrutturali di ogni club
- Livello stadio e incasso per partita casalinga
- Lista contratti in scadenza (ultimo anno)

### `4_Statistiche.py`
- Classifiche per competizione
- Statistiche gol, partite giocate, rendimento economico

### `5_Admin_Mercato.py` *(solo admin)*

Cinque tab operativi:

| Tab                  | Funzione                                                       |
|----------------------|----------------------------------------------------------------|
| 👤 Gestione Giocatori | Visualizza, crea, modifica, elimina giocatori dal DB          |
| ➕ Acquisto           | Ingaggio di uno svincolato con definizione stipendio e durata |
| 👋 Svincolo           | 4 tipi di svincolo con calcolo automatico impatto budget      |
| 🔄 Scambio            | Trasferimento tra club con gestione stipendio e costo         |
| 📝 Rinnovo            | Aggiornamento stipendio e anni rimanenti di contratto         |

### `6_Admin_Gestione_Squadre.py` *(solo admin)*
- Modifica livello stadio, incasso per partita e valore asset
- Acquisto slot settore giovanile (scala automaticamente il budget)
- Rettifica manuale del budget (per penalizzazioni o bonus)

### `7_Admin_Campionato.py` *(solo admin)*
- **Importa da Excel**: carica il file Fantacalcio, rileva automaticamente
  il formato (campionato lineare o coppa con gironi), importa solo
  le giornate non ancora presenti nel DB (delta update)
- **Inserimento manuale**: aggiunta singola partita con calcolo automatico guadagni
- **Storico**: visualizzazione di tutte le partite giocate con filtro per competizione

### `8_Admin_Fine_Stagione.py` *(solo admin)*
- Anteprima contratti in scadenza e stipendi da detrarre
- **Step 1 — Assegnazione Premi** (un tab per ogni competizione):
  - *Campionato*: calcola automaticamente la classifica e assegna i premi per posizione
  - *Coppe (Champions, Europa, Coppa Italia)*: l'admin seleziona la fase massima raggiunta per ogni squadra; il sistema calcola e assegna i premi cumulativi
- **Step 2 — Rollover**: chiusura stagione (irreversibile)

---

## Aggiornamento Stagione Manuale (emergenza)

Se il rollover automatico fallisce, è possibile aggiornare la stagione direttamente:

```sql
UPDATE configurazione SET Valore = '2026/2027' WHERE Chiave = 'stagione_corrente';
```

---

## Note di Sviluppo

- **Autenticazione**: gestita tramite SQLite locale (`users.db`) separato dal DB di gioco.
  Le password sono hashate con SHA-256. La sessione scade dopo 30 minuti di inattività.
- **Transazioni**: tutte le operazioni multi-step (acquisto, svincolo, rollover) usano
  `run_transaction_batch()` che garantisce atomicità tramite `engine.begin()` di SQLAlchemy.
- **Cache connessione**: il pool di connessione MySQL è cachato con `@st.cache_resource`
  per non ricreare la connessione ad ogni ricaricamento della pagina.
- **INSERT IGNORE**: usato sulle partite per prevenire duplicati grazie alla
  `UNIQUE KEY uq_partita` definita nello schema.
- **Competizioni per stagione**: la colonna `Stagione` in `competizioni` permette
  di avere edizioni diverse della stessa competizione in anni diversi mantenendo lo storico.
