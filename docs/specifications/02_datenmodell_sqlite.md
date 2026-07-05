# Datenmodell SQLite / SQLAlchemy für den Prototyp

## 1. Grundsatz

SQLite ist im Prototyp die zentrale Mock-Datenschicht. Alle fachlichen Funktionen greifen über SQLAlchemy auf die Datenbank zu.

Ziel ist eine einfache, robuste Struktur, die später prinzipiell auf PostgreSQL migriert werden kann.

### Grundsatz Nachvollziehbarkeit

Jeder manuelle Eintrag ist nachvollziehbar: Tabellen mit manuellen Einträgen
führen die Spalte `last_modified_by`, in der der aktuelle Benutzername
gespeichert wird. Der Name wird automatisch aus dem angemeldeten
Betriebssystem-Benutzer ermittelt (`src/user_context.py`, kein separates
Login im Prototyp). Wird über einen Button eine Aktion ausgeführt
(z. B. „Ausgeführt“, „Gelöscht“, „Erledigt“), ersetzt der Benutzername des
ausführenden Users den bisherigen Wert – auch in den dabei erzeugten
Folgeeinträgen (untertägige Geschäfte). Betroffen sind: `intraday_trades`,
`market_prices`, `otc_surcharges`, `limit_orders`, `trading_calendar`.

Die Spalte wird in bestehenden Datenbanken über eine leichte Migration in
`init_db()` nachträglich ergänzt (`ALTER TABLE ... ADD COLUMN`, Default
`system` für Altbestand); `create_all()` kann fehlende Spalten nicht nachziehen.

## 2. Technische Vorgaben

- Datenbank: SQLite
- Zugriff: SQLAlchemy ORM oder SQLAlchemy Core
- Migrationen im Prototyp optional; Struktur kann zunächst über `create_all()` erzeugt werden
- spätere Erweiterung um Alembic möglich

## 3. Jahreslogik

Die Anwendung bestimmt das aktuelle Jahr automatisch.

Für Mengen werden feste Spalten für Y0 bis Y+4 genutzt.

```text
quantity_y0_mwh = aktuelles Jahr
quantity_y1_mwh = Folgejahr
quantity_y2_mwh = Y+2
quantity_y3_mwh = Y+3
quantity_y4_mwh = Y+4
```

Nicht relevante Jahre dürfen 0 sein.

Mengen werden immer in MWh gespeichert. MW werden berechnet, nicht gespeichert.

## 4. Tabellenübersicht

| Tabelle | Zweck |
|---|---|
| `portfolio_positions` | Mock-Position aus Portfoliomanagementsystem |
| `intraday_trades` | untertägige Geschäfte |
| `market_prices` | aktuelle Marktpreise je Produkt |
| `otc_surcharges` | OTC-Aufschläge je Produkt |
| `settlement_prices` | Settlementpreise des Vortages |
| `pfc_checks` | PFC-Mittelwerte und Zeitstempel |
| `limit_orders` | Limitorders |
| `trading_calendar` | Handelskalendereinträge |
| `app_metadata` | technische Metadaten, z. B. Initialisierung |

## 5. Tabelle `portfolio_positions`

Speichert die Position aus dem Portfoliomanagementsystem als Mock-Daten.

| Feld | Typ | Beschreibung |
|---|---|---|
| `id` | Integer PK | technische ID |
| `as_of_date` | Date | Datenstand |
| `year` | Integer | Lieferjahr |
| `position_mwh` | Numeric | Position in MWh |
| `source` | String | z. B. `mock_excel`, `manual_seed` |
| `created_at` | DateTime | Erzeugungszeitpunkt |
| `updated_at` | DateTime | Änderungszeitpunkt |

Hinweis: Die Anzeige in MW erfolgt über Berechnung:

```text
position_mw = position_mwh / hours_in_year(year)
```

## 6. Tabelle `intraday_trades`

Speichert untertägige Geschäfte.

| Feld | Typ | Beschreibung |
|---|---|---|
| `id` | Integer PK | technische ID |
| `trade_date` | Date | Datum des Geschäfts |
| `partner_alias` | String | Kunden-/Handelspartner-Alias |
| `quantity_y0_mwh` | Numeric | Menge aktuelles Jahr |
| `quantity_y1_mwh` | Numeric | Menge Y+1 |
| `quantity_y2_mwh` | Numeric | Menge Y+2 |
| `quantity_y3_mwh` | Numeric | Menge Y+3 |
| `quantity_y4_mwh` | Numeric | Menge Y+4 |
| `source_type` | String | `manual`, `limit_order`, `trading_calendar` |
| `source_id` | Integer nullable | ID des Ursprungseintrags |
| `last_modified_by` | String | Benutzer der letzten Änderung (Nachvollziehbarkeit) |
| `created_at` | DateTime | Erzeugungszeitpunkt |

Es gibt kein Richtungsfeld. Die Richtung ergibt sich aus dem Vorzeichen der Mengen.

## 7. Tabelle `market_prices`

Speichert aktuelle Marktpreise aus Mock-Daten oder manueller Eingabe.

| Feld | Typ | Beschreibung |
|---|---|---|
| `id` | Integer PK | technische ID |
| `product_type` | String | `Base` oder `Peak` |
| `delivery_year` | Integer | Lieferjahr |
| `price_eur_mwh` | Numeric | Marktpreis |
| `price_timestamp` | DateTime | Zeitstempel des Preises |
| `last_modified_by` | String | Benutzer der letzten Änderung (Nachvollziehbarkeit) |
| `created_at` | DateTime | Erzeugungszeitpunkt |
| `updated_at` | DateTime | Änderungszeitpunkt |

Eindeutigkeit empfohlen:

```text
unique(product_type, delivery_year)
```

## 8. Tabelle `otc_surcharges`

Speichert OTC-Aufschläge je Handelsprodukt.

| Feld | Typ | Beschreibung |
|---|---|---|
| `id` | Integer PK | technische ID |
| `product_type` | String | `Base` oder `Peak` |
| `delivery_year` | Integer | Lieferjahr |
| `surcharge_eur_mwh` | Numeric | OTC-Aufschlag |
| `last_modified_by` | String | Benutzer der letzten Änderung (Nachvollziehbarkeit) |
| `created_at` | DateTime | Erzeugungszeitpunkt |
| `updated_at` | DateTime | Änderungszeitpunkt |

Eindeutigkeit empfohlen:

```text
unique(product_type, delivery_year)
```

## 9. Tabelle `settlement_prices`

Speichert Settlementpreise des Vortages.

| Feld | Typ | Beschreibung |
|---|---|---|
| `id` | Integer PK | technische ID |
| `product_type` | String | `Base` oder `Peak` |
| `delivery_year` | Integer | Lieferjahr |
| `settlement_date` | Date | Settlement-Datum |
| `settlement_price_eur_mwh` | Numeric | Settlementpreis |
| `settlement_timestamp` | DateTime | Zeitstempel |
| `created_at` | DateTime | Erzeugungszeitpunkt |
| `updated_at` | DateTime | Änderungszeitpunkt |

## 10. Tabelle `pfc_checks`

Speichert PFC-Mittelwerte und Zeitstempel für die Anzeige.

| Feld | Typ | Beschreibung |
|---|---|---|
| `id` | Integer PK | technische ID |
| `product_type` | String | `Base` oder `Peak` |
| `delivery_year` | Integer | Lieferjahr |
| `pfc_mean_eur_mwh` | Numeric | PFC-Mittelwert |
| `pfc_file_timestamp` | DateTime | Zeitstempel der PFC-Datei |
| `created_at` | DateTime | Erzeugungszeitpunkt |
| `updated_at` | DateTime | Änderungszeitpunkt |

## 11. Tabelle `limit_orders`

Speichert Limitorders.

| Feld | Typ | Beschreibung |
|---|---|---|
| `id` | Integer PK | technische ID |
| `partner_alias` | String | Kunden-/Partner-Alias |
| `quantity_y0_mwh` | Numeric | Menge aktuelles Jahr |
| `quantity_y1_mwh` | Numeric | Menge Y+1 |
| `quantity_y2_mwh` | Numeric | Menge Y+2 |
| `quantity_y3_mwh` | Numeric | Menge Y+3 |
| `quantity_y4_mwh` | Numeric | Menge Y+4 |
| `trigger_product_type` | String | `Base` oder `Peak` |
| `trigger_delivery_year` | Integer | Lieferjahr des Trigger-Preises |
| `trigger_condition` | String | siehe unten |
| `limit_price_eur_mwh` | Numeric | Limitpreis |
| `responsible_trading` | String nullable | **obsolet**, siehe Hinweis; für Altbestand/Import erhalten |
| `responsible_sales` | String nullable | **obsolet**, siehe Hinweis; für Altbestand/Import erhalten |
| `valid_until` | Date nullable | optionales Gültigkeitsdatum |
| `status` | String | `offen`, `ausgeführt`, `gelöscht`, `abgelaufen` |
| `last_modified_by` | String | Benutzer der letzten Änderung (Nachvollziehbarkeit) |
| `created_at` | DateTime | Erzeugungszeitpunkt |
| `updated_at` | DateTime | Änderungszeitpunkt |

Hinweis: Das frühere Pflichtfeld „Verantwortlicher“ (`responsible_trading` /
`responsible_sales`) ist obsolet – die Nachvollziehbarkeit erfolgt jetzt
ausschließlich über `last_modified_by`. Die UI fragt es nicht mehr ab. Die
Spalten sind nun optional (nullable); der interaktive Anlage-Pfad befüllt sie
aus Kompatibilität mit bestehenden `NOT NULL`-Datenbanken mit dem aktuellen
Benutzernamen, der Excel-Import mit Default-Platzhaltern.

### 11.1 Erlaubte `trigger_condition`-Werte

Empfohlene technische Werte:

| Technischer Wert | UI-Text | Erwartetes Vorzeichen |
|---|---|---:|
| `partner_buys_price_gt_limit` | Partner kauft, wenn Preis > Limit | positiv |
| `partner_buys_price_lt_limit` | Partner kauft, wenn Preis < Limit | positiv |
| `partner_sells_price_gt_limit` | Partner verkauft, wenn Preis > Limit | negativ |
| `partner_sells_price_lt_limit` | Partner verkauft, wenn Preis < Limit | negativ |

Die App muss validieren, dass die eingegebenen Mengen zum Trigger-Text passen.

## 12. Tabelle `trading_calendar`

Speichert geplante Handelskalendereinträge.

| Feld | Typ | Beschreibung |
|---|---|---|
| `id` | Integer PK | technische ID |
| `due_date` | Date | Fälligkeitsdatum |
| `partner_alias` | String | Kunden-/Partner-Alias |
| `direction` | String | `partner_buys` oder `partner_sells` |
| `quantity_y0_mwh` | Numeric | Menge aktuelles Jahr |
| `quantity_y1_mwh` | Numeric | Menge Y+1 |
| `quantity_y2_mwh` | Numeric | Menge Y+2 |
| `quantity_y3_mwh` | Numeric | Menge Y+3 |
| `quantity_y4_mwh` | Numeric | Menge Y+4 |
| `status` | String | `geplant`, `fällig`, `erledigt` |
| `last_modified_by` | String | Benutzer der letzten Änderung (Nachvollziehbarkeit) |
| `created_at` | DateTime | Erzeugungszeitpunkt |
| `updated_at` | DateTime | Änderungszeitpunkt |

### 12.1 Vorzeichenvalidierung

| Direction | UI-Text | Erwartetes Vorzeichen |
|---|---|---:|
| `partner_buys` | Partner kauft | positiv |
| `partner_sells` | Partner verkauft | negativ |

## 13. Tabelle `app_metadata`

Speichert technische Metadaten.

| Feld | Typ | Beschreibung |
|---|---|---|
| `key` | String PK | Schlüssel |
| `value` | String | Wert |
| `updated_at` | DateTime | Änderungszeitpunkt |

Beispiele:

| Key | Wert |
|---|---|
| `db_initialized` | `true` |
| `initial_seed_source` | `excel_mock_file` |
| `initial_backup_created_at` | Zeitstempel |

## 14. Hilfsfunktionen

### 14.1 Schaltjahrprüfung

```python
def is_leap_year(year: int) -> bool:
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
```

### 14.2 Stunden je Jahr

```python
def hours_in_year(year: int) -> int:
    return 8784 if is_leap_year(year) else 8760
```

### 14.3 MWh zu MW

```python
def mwh_to_mw(quantity_mwh: float, year: int) -> float:
    return quantity_mwh / hours_in_year(year)
```

### 14.4 Positionswirkung interpretieren

```python
def interpret_quantity(quantity_mwh: float) -> str:
    if quantity_mwh > 0:
        return "Partner kauft von uns"
    if quantity_mwh < 0:
        return "Partner verkauft an uns"
    return "Keine Menge"
```

## 15. Validierungsregeln

| Regel | Beschreibung |
|---|---|
| Menge darf nicht ausschließlich 0 sein | Mindestens ein Lieferjahr muss eine Menge ungleich 0 haben |
| Partner kauft | alle befüllten Mengen müssen positiv sein |
| Partner verkauft | alle befüllten Mengen müssen negativ sein |
| Limitorder Trigger-Text und Vorzeichen müssen passen | keine widersprüchlichen Angaben |
| Handelskalender Richtung und Vorzeichen müssen passen | keine widersprüchlichen Angaben |
| Preise | numerisch, auf 2 Nachkommastellen anzeigen |
| MWh | auf 0 Nachkommastellen anzeigen |
| MW | auf 2 Nachkommastellen anzeigen |
