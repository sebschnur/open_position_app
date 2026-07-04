# Excel-Mockdaten-Import: Zellbereiche und Mapping

Dieses Dokument ergänzt die Spezifikation um das konkrete Mapping der Excel-Mockdaten in die SQLite-Datenbank.

Ziel ist nicht, die Excel-Datei dauerhaft als produktive Datenquelle zu behandeln. Die Excel-Datei dient im Prototyp nur als initiale Mockdatenquelle. Die fachliche Anwendung arbeitet danach gegen SQLite über SQLAlchemy.

```text
Excel-Mockdatei
   ↓
Seed-Skript liest definierte Zellbereiche
   ↓
SQLite wird initial befüllt
   ↓
Streamlit-App arbeitet gegen SQLite
```

## 1. Grundsatz

## 1.1 Fachlich bestätigte Importregeln

Diese Regeln sind für den Excel-Mockdatenimport verbindlich:

| Thema | Regel |
|---|---|
| Handelskalender `Kauf` | bedeutet `Partner kauft von uns` und erfordert positive Mengen |
| Handelskalender `Verkauf` | bedeutet `Partner verkauft an uns` und erfordert negative Mengen |
| Limitorder-Mockdaten | es wird nur der Fall `Partner kauft von uns, wenn Preis <= Limit` verwendet |
| Limitorder `Kauf-Limit` | wird als `Partner kauft, wenn Preis <= Limit` importiert |
| Limitorder `Verkauf-Limit` | im aktuellen Mock-Import nicht relevant; bei Befüllung klar melden oder ignorieren |
| Leeres Datum bei untertägigen Geschäften | automatisch heutiges Datum setzen |
| Befülltes Datum | vorhandenes Datum übernehmen |

- Die SQLite-Datenbank wird vor dem Start mit Mockdaten befüllt.
- Falls die Datenbank bereits Daten enthält, soll sie nicht automatisch überschrieben werden.
- Nach erfolgreicher Initialisierung wird eine Backup-Datei des initialen Stands angelegt.
- Die App selbst erhält keinen Reset-Button.
- Die Excel-Bereiche werden nur für den Initialimport verwendet.

Empfohlene Dateien:

```text
data/
  app.db
  app_initial_backup.db
scripts/
  seed_from_excel.py
```

## 2. Vom Nutzer benannte Zellbereiche

| Fachbereich | Excel-Blatt | Zellbereich |
|---|---|---|
| Position aus Portfoliomanagementsystem | `Position Frontjahre` | `A7:H8` |
| Untertägige Geschäfte | `Position Frontjahre` | `A9:H10` |
| Preise und Aufschläge Base | `Vertriebsinfos` | `B14:C17` |
| Preise und Aufschläge Peak | `Vertriebsinfos` | `G14:H17` |
| Handelskalender | `Handelskalender` | `A3:M6` |
| Limitorder | `Limitorder` | `A5:G6` |
| Settlementpreise Base | `Vertriebsinfos` | `L14:L16` |
| PFC-Mittelwerte | separate `.xlsx`-Dateien | Dateiname `YYYYMMDD_EEX_PFC_YYYY.xlsx`, Mittelwert in `D2` |

## 3. Gelesene Struktur in der aktuellen Datei

Die aktuelle hochgeladene Datei ist technisch lesbar. Die benannten Bereiche enthalten folgende Strukturen.

### 3.1 Position aus Portfoliomanagementsystem

Kontextbereich: `Position Frontjahre!A6:H8`

| Spalte | Bedeutung |
|---|---|
| A | Datum |
| B | Bezeichnung |
| C | alte Excel-Richtung `K` / `V` |
| D:H | Lieferjahre, aktuell 2026 bis 2030 |

Aktuell gelesene Beispielwerte:

| Datum | Bezeichnung | Richtung Excel | 2026 | 2027 | 2028 | 2029 | 2030 |
|---|---|---:|---:|---:|---:|---:|---:|
| 2026-07-02 01:15 | Portfolio A/B | K | 1129293.891 | 594936 | 309196.8 | 105120 | 17520 |
| 2026-07-02 01:15 | Portfolio A/B | V | 1117774.067584 | 600611.32558 | 308922.326794 | 112043.92786 | 17520 |

Empfohlenes Mapping:

```text
K-Zeile = negative Positionswirkung
V-Zeile = positive Positionswirkung

portfolio_position_mwh je Jahr = Summe(V-Mengen) - Summe(K-Mengen)
```

Beispiel aus den aktuellen Daten:

| Lieferjahr | Netto-Position MWh | Hinweis |
|---:|---:|---|
| 2026 | -11.519,82 | Long / negative Position |
| 2027 | 5.675,33 | positive offene Position |
| 2028 | -274,47 | Long / negative Position |
| 2029 | 6.923,93 | positive offene Position |
| 2030 | 0,00 | ausgeglichen |

In SQLite wird nur die Netto-Position je Jahr gespeichert, nicht zwingend die alte Excel-K/V-Struktur.

Zieltabelle:

```text
portfolio_positions
```

## 4. Untertägige Geschäfte

Kontextbereich: `Position Frontjahre!A6:H10`

| Spalte | Bedeutung |
|---|---|
| A | Datum |
| B | Partner-/Kunden-Alias |
| C | alte Excel-Richtung `K` / `V` |
| D:H | Mengen pro Lieferjahr |

Aktuell gelesene Beispielwerte:

| Datum | Partner | Richtung Excel | 2026 | 2027 | 2028 | 2029 | 2030 |
|---|---|---:|---:|---:|---:|---:|---:|
| leer | Malermeister A | V | leer | 5000 | leer | 3000 | leer |
| leer | Vattenfall | K | leer | 8760 | leer | 8760 | leer |

Empfohlenes Mapping in die neue Vorzeichenlogik:

```text
V in alter Excel-Datei = positive Menge
K in alter Excel-Datei = negative Menge
```

Neue App-Logik:

```text
Positive Menge  = Partner kauft von uns
Negative Menge  = Partner verkauft an uns
```

Beispiel-Mapping:

| Partner | Lieferjahr | Excel-Richtung | Excel-Menge MWh | SQLite-Menge MWh |
|---|---:|---:|---:|---:|
| Malermeister A | 2027 | V | 5000 | +5000 |
| Malermeister A | 2029 | V | 3000 | +3000 |
| Vattenfall | 2027 | K | 8760 | -8760 |
| Vattenfall | 2029 | K | 8760 | -8760 |

Wenn das Datum leer ist, setzt das Importskript im Prototyp automatisch das aktuelle Datum. Wenn ein Datum vorhanden ist, wird dieses Datum unverändert übernommen.

Zieltabelle:

```text
intraday_trades
```

## 5. Preise und OTC-Aufschläge

### 5.1 Base

Kontextbereich: `Vertriebsinfos!A13:C17`

| Spalte | Bedeutung |
|---|---|
| A | Jahr |
| B | Base-Marktpreis / EEX |
| C | OTC-Aufschlag |

Aktuell gelesene Beispielwerte:

| Jahr | Base-Marktpreis | OTC-Aufschlag |
|---:|---:|---:|
| 2027 | 93.19 | 0.40 |
| 2028 | 81.27 | 0.50 |
| 2029 | 75.50 | 0.60 |
| 2030 | 71.63 | leer |

### 5.2 Peak

Kontextbereich: `Vertriebsinfos!F13:H17`

| Spalte | Bedeutung |
|---|---|
| F | aktuell leer / Kontext |
| G | Peak-Marktpreis / EEX |
| H | OTC-Aufschlag |

Aktuell gelesene Beispielwerte:

| Jahr | Peak-Marktpreis | OTC-Aufschlag |
|---:|---:|---:|
| 2027 | 93.98 | 0.65 |
| 2028 | 82.34 | 0.75 |
| 2029 | 76.12 | 0.85 |

Für den Prototyp werden nur Y+1 bis Y+3 verwendet.

Bei aktuellem Jahr 2026 entspricht das:

```text
Y+1 = 2027
Y+2 = 2028
Y+3 = 2029
```

Zieltabellen:

```text
market_prices
otc_surcharges
```

Berechnung:

```text
finaler Preis = Marktpreis + OTC-Aufschlag
```

## 6. Handelskalender

Kontextbereich: `Handelskalender!A1:M6`

| Spalte | Bedeutung in der aktuellen Excel-Datei |
|---|---|
| A | Datum |
| B | Kunde |
| C | alte Richtung, z. B. `Kauf` |
| D | Produkt, z. B. `Base` oder `Peak` |
| E:G | Mengen für Lieferjahre 2027 bis 2029 |
| H:J | aktueller Preis / Formelbereich |
| K:M | Kauflimit-Bereich |

Vom Nutzer gewünschtes Zielmodell:

```text
Datum
Kunden-/Partner-Alias
Partner kauft / Partner verkauft
Mengen pro Lieferjahr Y0 bis Y+4
Status: geplant, fällig, erledigt
```

Importempfehlung:

- Für den Prototyp sind die Spalten A:G fachlich relevant.
- Spalten H:M sind im Prototyp nicht als Stammdaten des Handelskalenders nötig.
- Nicht vorhandene Jahre Y0 und Y+4 werden beim Import mit 0 befüllt.
- Die Richtung aus der Excel-Datei sollte auf die neue eindeutige Formulierung gemappt werden:
  - `Kauf` → `Partner kauft von uns` → positive Menge
  - `Verkauf` → `Partner verkauft an uns` → negative Menge

Diese Interpretation ist fachlich bestätigt. Zur Sicherheit sollen die importierten Mengen gegen die abgeleitete Richtung validiert werden.

Zieltabelle:

```text
trading_calendar
```

## 7. Limitorder

Kontextbereich: `Limitorder!A1:G6`

| Spalte | Bedeutung in der aktuellen Excel-Datei |
|---|---|
| A | Lieferzeitraum / Lieferjahr |
| B | Kunde |
| C | Menge MWh |
| D | Produkt / Trigger-Preis-Typ Base oder Peak |
| E | Kauf-Limit €/MWh |
| F | Verkauf-Limit €/MWh |
| G | Order gültig bis einschließlich |

Aktuell gelesene Beispielwerte:

| Lieferjahr | Kunde | Menge MWh | Produkt | Kauf-Limit | Verkauf-Limit | gültig bis |
|---:|---|---:|---|---:|---:|---|
| 2027 | Bau AG | 8760 | Base | 90 | leer | 2026-07-31 |
| 2028 | Malermeister A | 200 | Peak | 99 | leer | 2026-07-03 |

Vom Nutzer gewünschtes Zielmodell:

```text
Trigger-Preis:
- Base Y+1
- Base Y+2
- Base Y+3
- Peak Y+1
- Peak Y+2
- Peak Y+3

Auslöseart:
- Partner kauft, wenn Preis > Limit
- Partner kauft, wenn Preis < Limit
- Partner verkauft, wenn Preis > Limit
- Partner verkauft, wenn Preis < Limit
```

Vorzeichenregel:

```text
Positive Menge = Partner kauft von uns
Negative Menge = Partner verkauft an uns
```

Importempfehlung:

- Lieferjahr aus Spalte A wird sowohl als Lieferjahr als auch als Trigger-Lieferjahr interpretiert.
- Produkt aus Spalte D wird als Trigger-Produkttyp verwendet.
- Menge aus Spalte C wird mit Vorzeichen übernommen.
- In den Mock-Daten wird nur der Fall `Partner kauft von uns, wenn Preis <= Limit` verwendet.
- Wenn `Kauf-Limit` befüllt ist, wird daraus eine Order mit Auslöseart `Partner kauft, wenn Preis <= Limit`.
- `Verkauf-Limit` ist in den aktuellen Mock-Daten nicht relevant und soll beim Import ignoriert oder als nicht unterstützter Mock-Fall klar gemeldet werden.
- Die Menge muss für `Partner kauft` positiv sein.

Zieltabelle:

```text
limit_orders
```

## 8. Settlementpreise und PFC-Prüfung

Settlementpreise und PFC-Werte werden im Prototyp ebenfalls in SQLite gespeichert. Die App liest diese Werte später ausschließlich aus SQLite; Excel- und PFC-Dateien dienen nur der initialen Mockdatenbefüllung.

```text
Settlement-/PFC-Mockquellen
   ↓
Seed-Skript liest definierte Quellen
   ↓
SQLite-Tabellen `settlement_prices` und `pfc_checks`
   ↓
Preise-Seite / PFC-Prüfung zeigt die Werte an
```

### 8.1 Settlementpreise aus Excel

Für Settlementpreise werden im Prototyp Mockdaten aus der Excel-Datei verwendet.

| Thema | Festlegung |
|---|---|
| Excel-Blatt | `Vertriebsinfos` |
| Zellbereich | `L14:L16` |
| Produkte | nur Base |
| Jahre | Y+1 bis Y+3 |
| Ziel | Werte in SQLite-Tabelle `settlement_prices` schreiben |

Mapping:

| Excel-Zelle | Zielprodukt bei aktuellem Jahr 2026 | Allgemeines Mapping |
|---|---|---|
| `L14` | Base 2027 | Base Y+1 |
| `L15` | Base 2028 | Base Y+2 |
| `L16` | Base 2029 | Base Y+3 |

Regeln:

- Es werden nur Base-Settlementpreise aus Excel gelesen.
- Die Jahre werden dynamisch relativ zum aktuellen Jahr bestimmt.
- Falls Peak-Settlementpreise für die UI oder Mailtext-Differenz benötigt werden, erzeugt das Seed-Skript realistische Default-Mockdaten.
- Falls einzelne Base-Werte leer sind, erzeugt das Seed-Skript auch dafür realistische Default-Mockdaten und meldet dies klar im Importprotokoll.
- `settlement_date` kann im Prototyp als Vortag des Seed-Laufs gesetzt werden.
- `settlement_timestamp` kann im Prototyp als Zeitpunkt des Seed-Laufs gesetzt werden, sofern kein genauerer Zeitstempel vorliegt.

Zieltabelle:

```text
settlement_prices
```

### 8.2 PFC-Mittelwerte aus separaten PFC-Dateien

Zusätzlich werden im Projekt drei Beispiel-PFC-Dateien im `.xlsx`-Format bereitgestellt, je eine Datei für 2027, 2028 und 2029.

Beispiel-Dateiname:

```text
20260702_EEX_PFC_2028.xlsx
```

Festlegungen:

| Thema | Festlegung |
|---|---|
| Dateiformat | `.xlsx` |
| Anzahl im Prototyp | 3 Dateien |
| Jahre | 2027, 2028, 2029 beziehungsweise Y+1 bis Y+3 |
| PFC-Mittelwert | Zelle `D2` |
| Generierungsdatum | aus dem Dateinamen, erste 8 Stellen `YYYYMMDD` |
| Lieferjahr | aus dem Dateinamen, z. B. `_2028.xlsx` |
| Ziel | Werte in SQLite-Tabelle `pfc_checks` schreiben |

Mapping aus Dateiname:

```text
20260702_EEX_PFC_2028.xlsx
│        │       │
│        │       └─ Lieferjahr = 2028
│        └──────── Kontext / Quelle = EEX_PFC
└───────────────── PFC-Generierungsdatum = 2026-07-02
```

Mapping aus Dateiinhalt:

```text
D2 = PFC-Mittelwert in €/MWh
```

Regeln:

- Das Seed-Skript sucht die PFC-Dateien in einem definierten Verzeichnis, z. B. `data/pfc/`.
- Der Dateiname muss dem Muster `YYYYMMDD_EEX_PFC_YYYY.xlsx` entsprechen.
- Das Lieferjahr im Dateinamen muss zu Y+1 bis Y+3 passen.
- Der PFC-Mittelwert wird aus Zelle `D2` gelesen.
- Der Zeitstempel der PFC-Datei wird aus dem Datum im Dateinamen abgeleitet.
- Im Prototyp reicht ein Datum ohne Uhrzeit; technisch kann `00:00:00` verwendet werden.
- Falls eine PFC-Datei fehlt oder `D2` leer/nicht numerisch ist, erzeugt das Seed-Skript realistische Default-Mockdaten und meldet dies klar im Importprotokoll.
- Die PFC-Prüfung bezieht sich im Prototyp auf die Base-Jahresprodukte Y+1 bis Y+3.

Zieltabelle:

```text
pfc_checks
```

### 8.3 Anzeige in der PFC-Prüfung

Die PFC-Prüfung bleibt eine Anzeige- und Plausibilitätsprüfung, keine harte automatische Ampellogik.

Die UI zeigt je Jahr:

| Spalte | Quelle |
|---|---|
| Jahr | aus PFC-Dateiname / aktuelles Jahr + Offset |
| PFC-Mittelwert | PFC-Datei, Zelle `D2`, oder Default-Mockwert |
| Settlementpreis Base | SQLite-Tabelle `settlement_prices` |
| Differenz | PFC-Mittelwert minus Settlementpreis Base |
| Zeitstempel PFC-Datei | aus Dateiname |
| Zeitstempel Settlementpreis | aus SQLite |

### 8.4 Default-Mockdaten

Wenn Excel-Zellen oder PFC-Dateien fehlen, darf der Prototyp realistische Default-Mockdaten erzeugen.

Wichtig:

```text
Default-Mockdaten sind erlaubt,
aber sie müssen im Importprotokoll klar als Default gekennzeichnet werden.
```

Empfohlene technische Umsetzung:

- Seed-Skript erzeugt eine Liste von Importwarnungen.
- Diese Warnungen werden auf der Konsole ausgegeben.
- Optional werden sie zusätzlich in `app_metadata` gespeichert.

## 9. Technische Empfehlung für Codex / Claude Code

### 9.1 Seed-Skript

Ein eigenes Seed-Skript sollte die Excel-Datei lesen und die SQLite-Datenbank befüllen:

```bash
python scripts/seed_from_excel.py --excel path/to/mockdaten.xlsm --db data/app.db
```

Aufgaben des Skripts:

1. Excel-Datei öffnen.
2. Definierte Zellbereiche lesen.
3. Werte validieren und normalisieren.
4. Alte Excel-Richtungen in neue Vorzeichenlogik übersetzen.
5. SQLAlchemy-Modelle erzeugen.
6. SQLite-Datenbank initial befüllen.
7. Initiales Backup `app_initial_backup.db` erzeugen.
8. Seed-Metadaten in `app_metadata` speichern.

### 9.2 Empfohlene Funktionen

```python
def read_portfolio_positions_from_excel(path: str) -> list[PortfolioPositionSeed]:
    ...

def read_intraday_trades_from_excel(path: str) -> list[IntradayTradeSeed]:
    ...

def read_market_prices_and_surcharges_from_excel(path: str) -> tuple[list[MarketPriceSeed], list[SurchargeSeed]]:
    ...

def read_trading_calendar_from_excel(path: str) -> list[TradingCalendarSeed]:
    ...

def read_limit_orders_from_excel(path: str) -> list[LimitOrderSeed]:
    ...

def read_settlement_prices_from_excel(path: str) -> list[SettlementPriceSeed]:
    ...

def read_pfc_checks_from_files(pfc_dir: str) -> list[PfcCheckSeed]:
    ...

def seed_database_from_excel(excel_path: str, db_url: str, pfc_dir: str | None = None) -> None:
    ...
```

### 9.3 Wichtige Validierungen

| Validierung | Grund |
|---|---|
| Jahrsspalten müssen zum aktuellen Jahr passen | verhindert falsche Y0/Y+1-Zuordnung |
| Mengen müssen numerisch sein | verhindert Importfehler |
| positive Menge = Partner kauft | Sicherheitskonvention |
| negative Menge = Partner verkauft | Sicherheitskonvention |
| Limitorder-Vorzeichen muss zur Auslöseart passen | verhindert widersprüchliche Orders |
| leere Mengen werden als 0 importiert | einfache MVP-Logik |
| Preise werden auf 2 Nachkommastellen angezeigt | einheitliche Darstellung |
| MWh werden auf 0 Nachkommastellen angezeigt | einheitliche Darstellung |
| MW werden auf 2 Nachkommastellen angezeigt | einheitliche Darstellung |

## 10. Offene Klärpunkte aus dem Excel-Mapping

| Nr. | Klärpunkt | Status |
|---:|---|---|
| 1 | Bedeutet `Kauf` im Handelskalender sicher `Partner kauft`? | geklärt: ja, `Partner kauft von uns` |
| 2 | Bedeutet `Verkauf` im Handelskalender sicher `Partner verkauft`? | geklärt: ja, `Partner verkauft an uns` |
| 3 | Wie wird aus `Kauf-Limit` / `Verkauf-Limit` die genaue Auslösebedingung abgeleitet? | geklärt für Mock-Daten: `Kauf-Limit` = `Partner kauft, wenn Preis <= Limit`; `Verkauf-Limit` wird im Mock-Import nicht benötigt |
| 4 | Was soll passieren, wenn Datumsfelder leer sind? | geklärt: heutiges Datum setzen; vorhandene Datumswerte übernehmen |
| 5 | Woher kommen initiale Settlementpreise? | geklärt: `Vertriebsinfos!L14:L16`, nur Base Y+1 bis Y+3; fehlende Peak-/Leerwerte als Default-Mockdaten |
| 6 | Woher kommen PFC-Mittelwerte und Zeitstempel? | geklärt: drei `.xlsx`-PFC-Dateien, Mittelwert in `D2`, Datum und Jahr aus Dateiname `YYYYMMDD_EEX_PFC_YYYY.xlsx` |
| 7 | Sollen fehlende Settlement-/PFC-Werte ersetzt werden? | geklärt: ja, realistische Default-Mockdaten erzeugen und im Importprotokoll kenntlich machen |
| 8 | Sollen Formeln in Excel beim Import ignoriert und nur Werte gelesen werden? | offen / technische Empfehlung: Werte lesen, Python-Logik ist später führend |

## 11. Merksatz

```text
Die Excel-Datei liefert nur den initialen Mockdatenstand.
Die fachliche Wahrheit des Prototyps liegt danach in SQLite.
Die neue App übernimmt nicht die alte Excel-Perspektive,
sondern nutzt konsequent die sichere Vorzeichenlogik.
```
