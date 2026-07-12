# Projektschritt 11: Persistenz auf PostgreSQL umstellen (SQLite bleibt für Tests)

> Status: **geplant** — auszuführen in einer eigenen Session im Projektpfad
> `open_position_app/`. Grundlage: Stack-Analyse-Hausstandard
> (`stack-analyse/docs/synthese.md`, §4/§5) und die offene Frage „Prod-DB-Backend"
> (§6.5). Dieser Schritt bringt den Prototyp näher an eine deploybare Version.

## Ziel

Die **laufende App** persistiert auf **PostgreSQL** (reproduzierbar via Container),
Schemaänderungen laufen über **Alembic** statt über die bisherige PRAGMA-Leichtmigration.
Die **Test-Suite bleibt auf In-Memory-SQLite** (schnell, isoliert, 100 % Domain-Coverage).

## Nicht-Ziele

- Keine fachliche Änderung an Position/Preise/Limitorder/Handelskalender.
- **Keine** Authentifizierung / Mehrbenutzer-Identität (eigener, späterer Schritt — siehe
  offene Frage in `IMPLEMENTIERUNG.md`).
- **Kein** MS SQL Server. Der Hausprimär-Speicher ist zwar MSSQL (Postgres ist im Haus
  Sekundär-Backend), aber welches Backend diese App produktiv bekommt, ist eine **offene
  Betriebsfrage**. Solange wir strikt über SQLAlchemy Core/ORM gehen (kein roher Dialekt-SQL),
  bleibt ein späterer Wechsel Postgres→MSSQL klein.

## Voraussetzungen

- Container-Laufzeit lokal (Docker **oder** podman — podman ist bereits installiert und kann
  `podman compose`).
- Neue Dependencies (exakt pinnen, in `requirements.txt`): **`psycopg[binary]`** (Treiber, v3),
  **`alembic`**.
- Bestehende lokale PostgreSQL-Installation ist nutzbar; empfohlen wird jedoch ein
  **Postgres-Container** (wegwerfbar, reproduzierbar, näher am Deployment).

## Betroffene Stellen im Code (aus der Ist-Analyse)

| Datei | Ist-Zustand | Änderung |
|---|---|---|
| `src/config.py:20` | `DB_URL = f"sqlite:///{DB_PATH}"` fest verdrahtet | DB_URL **env-getrieben**: `os.getenv("DB_URL", <sqlite-default>)`. Default bleibt SQLite (lokal/Tests laufen unverändert). |
| `src/db/database.py:21` | `connect_args={"check_same_thread": False}` (SQLite-spezifisch) | connect_args **nur bei SQLite** setzen (auf URL-Schema prüfen); für Postgres `pool_pre_ping=True`. |
| `src/db/init_db.py` | `PRAGMA table_info(...)`, `ALTER TABLE ... DROP COLUMN`, `DB_PATH.exists()` — alles SQLite-spezifisch | Durch **Alembic** ersetzen. „db_existed"-Erkennung backend-agnostisch über `inspect(engine).has_table(...)` statt Dateiexistenz. |
| `tests/*_service.py` | eigene `create_engine("sqlite:///:memory:")` je Test | **unverändert lassen** — die Tests bauen ihre eigene Engine und hängen nicht an der App-DB_URL. |

## Arbeitspakete

### AP1 — Konfiguration entkoppeln
- `DB_URL` aus Umgebungsvariable lesen, SQLite als Default behalten.
- Einheitliches Namensschema wählen (empfohlen: eine `DB_URL`, alternativ
  `DB_HOST/DB_PORT/DB_NAME/DB_USER/DB_PASSWORD` zusammensetzen — Hausschema `DB_*`).
- `.env` in `.gitignore` (prüfen) und **`.env.example`** mit Variablennamen (ohne echte Werte)
  anlegen. **Keine echten Credentials/Hostnamen einchecken** (Hausregel).

### AP2 — Engine backend-fähig machen
- `connect_args` konditional (nur SQLite). Für Postgres `create_engine(url, pool_pre_ping=True)`.
- Kurz prüfen, dass die Streamlit-Wiederverwendung der Engine (`@st.cache_resource`) mit
  Postgres-Pool sauber funktioniert.

### AP3 — Alembic einführen
- `alembic init alembic`; `env.py` an `Base.metadata` (aus `src.db.database`) und an die
  `DB_URL` koppeln.
- Erste Revision per Autogenerate = **aktuelles Schema** (9 Fachtabellen inkl.
  `last_modified_by`). Danach entfällt die PRAGMA-Leichtmigration in `init_db.py`.
- `init_db.py` so umbauen, dass Schemapflege über `alembic upgrade head` läuft (die
  `create_all`-Nutzung im Prototyp kann für die reine Test-DB bleiben).

### AP4 — Datentypen für Postgres härten
- SQLite ist typ-lax, Postgres streng. Prüfen:
  - **Preise/Beträge:** `Numeric(…, 2)` statt Float, wo fachlich exakt gerechnet wird.
  - **Mengen (MWh):** bewusst Integer/Numeric wählen.
  - **Zeitstempel:** aktuell **naives UTC**. Hausregel wäre **UTC-aware** (`timestamptz`).
    Als **eigene Entscheidung** markieren; wenn umgestellt, konsistent in Modell + Lese-/
    Schreibpfad (siehe `ts-utc`-Skill / Synthese-Zeitzonenregel).

### AP5 — Container: Postgres lokal reproduzierbar
- `docker-compose.yml` mit Service `db` (Image **gepinnt**, z. B. `postgres:16`),
  Named Volume, `POSTGRES_*`-Env aus `.env`, `healthcheck` (`pg_isready`), Port-Mapping.
- (App-Service optional in diesem Schritt; sonst im Deployment-Schritt.)
- Läuft mit `docker compose up` **oder** `podman compose up`.

### AP6 — Datenübernahme SQLite → Postgres
- Da **reiner Mockdaten-Prototyp**: einfachster, sauberster Weg ist **Neu-Seed** gegen
  Postgres (`scripts/init_db.py` → `alembic upgrade head`, dann
  `scripts/seed_default_mock_data.py` bzw. `seed_from_excel.py`).
- Nur falls echte Bestandsdaten nötig: einmaliges Kopieren via pandas
  (`read_sql` je Tabelle → `to_sql`) in Abhängigkeitsreihenfolge. Für den Prototyp
  **nicht** erforderlich.

## Akzeptanzkriterien

- [ ] `docker compose up` (oder `podman compose up`) startet Postgres mit Healthcheck grün.
- [ ] `alembic upgrade head` erzeugt das vollständige Schema in Postgres.
- [ ] Seed füllt Postgres; die App startet gegen Postgres und alle vier Seiten rendern.
- [ ] `pytest`: alle Tests weiter grün — **auf In-Memory-SQLite** (keine Postgres-Abhängigkeit
      der Unit-Tests).
- [ ] Im Nicht-Test-Pfad kein SQLite-spezifischer Code mehr (kein `PRAGMA`, keine
      `check_same_thread`-Annahme, keine Datei-Existenz-Logik als Backend-Signal).
- [ ] `.env.example` vorhanden; **keine** echten Credentials/Hostnamen im Repo.
- [ ] Neue Deps exakt gepinnt in `requirements.txt`.

## Verweise

- Hausstandard: `stack-analyse/docs/synthese.md` §4 (DB-Zugriff/Migrationen), §5 (Checkliste),
  §6.5 (offene Frage Prod-DB-Backend & Zeitzonensemantik).
- Bestehende Einschränkungen/Notiz: `docs/IMPLEMENTIERUNG.md` (Abschnitt „Bekannte
  Einschränkungen" und „Offene fachliche Fragen": Migrationspfad SQLite→PostgreSQL vorbereitet).
- Qualitäts-Gates (parallel eingerichtet): `pyproject.toml`, `.pre-commit-config.yaml`,
  `requirements-dev.txt`.
