# Streamlit UI-Konzept

## 1. Grundprinzip

Die Anwendung besteht aus vier separaten Streamlit-Seiten:

1. Position
2. Preise
3. Limitorder
4. Handelskalender

Es gibt keine zusätzliche Startseite.

Auffälligkeiten werden direkt auf der jeweiligen Fachseite hervorgehoben.

## 2. Bedienprinzip

Die App verwendet bewusst einfache UI-Elemente:

- Tabellen zur Anzeige
- kleine Formulare zur Eingabe
- klare Buttons für Aktionen
- kopierbare Textfelder für Preisnachrichten
- Highlighting statt komplexer Ampellogik

Keine komplexe Tabellenbearbeitung als Hauptprinzip.

```text
Besser:
Formular + Button + klare Aktion

Nicht nötig:
komplexes Excel-ähnliches Inline-Editing
```

## 3. Navigation

Empfohlene Streamlit-Struktur:

```text
app.py
pages/
  1_Position.py
  2_Preise.py
  3_Limitorder.py
  4_Handelskalender.py
```

## 4. Seite „Position“

### 4.1 Ziel

Die Seite zeigt:

- offene Position je Kalenderjahr in MW
- Limitauslastung je Kalenderjahr
- separaten Effekt untertägiger Geschäfte
- Tabelle der untertägigen Geschäfte
- Formular zur Erfassung neuer untertägiger Geschäfte

### 4.2 Layout-Vorschlag

```text
# Position

[Infobox: aktueller Datenstand]

## Offene Position je Kalenderjahr
[Tabelle]

## Untertägige Geschäfte
[Tabelle mit Löschen-Buttons]

## Neues untertägiges Geschäft erfassen
[Formular]
[Button: Einfügen]
```

### 4.3 Positionstabelle

Spalten:

- Kalenderjahr
- PMS-Position MW
- Untertägige Geschäfte MW
- Simulierte Position MW
- Limit MW
- Auslastung %
- Status

Highlighting:

- `abs(simulierte_position_mw) <= 1.0`: normal
- `abs(simulierte_position_mw) > 1.0`: hervorheben

### 4.4 Untertägige Geschäfte Tabelle

Spalten:

- Datum
- Partner-Alias
- Menge Y0 MWh
- Menge Y1 MWh
- Menge Y2 MWh
- Menge Y3 MWh
- Menge Y4 MWh
- Interpretation / Positionswirkung
- Quelle
- Button „Löschen“

### 4.5 Formular „Neues untertägiges Geschäft“

Felder:

- Datum
- Partner-Alias
- Menge Y0 MWh
- Menge Y1 MWh
- Menge Y2 MWh
- Menge Y3 MWh
- Menge Y4 MWh

Kein Richtungsfeld.

Die UI zeigt automatisch eine Interpretation an:

```text
Positive Menge: Partner kauft von uns
Negative Menge: Partner verkauft an uns
```

Button:

- `Einfügen`

Nach dem Einfügen:

- Datensatz speichern
- Position neu berechnen
- Tabelle aktualisieren

## 5. Seite „Preise“

### 5.1 Ziel

Die Seite dient zur Pflege von Marktpreisen und OTC-Aufschlägen sowie zur Erzeugung von Chat- und Mailtexten.

### 5.2 Layout-Vorschlag

```text
# Preise / Vertriebsinfos

## Preise und Aufschläge
[Formular/Tabelle für 6 Produkte]
[Button: Preise und Aufschläge speichern]

## Preisvergleich Settlement
[Tabelle]

## Chat-Kurztext
[Textfeld kopierbar]
[Button: Chattext erzeugen]

## Mailtext
[Textfeld kopierbar]
[Button: Mailtext erzeugen]

## PFC-Prüfung
[Button oder Expander: PFC-Prüfung anzeigen]
[Tabelle]
```

### 5.3 Preisprodukte

Anzeige-Reihenfolge in der Pflegetabelle:

1. Base Y+1
2. Base Y+2
3. Base Y+3
4. Peak Y+1
5. Peak Y+2
6. Peak Y+3

Spalten:

- Produkt
- Marktpreis
- OTC-Aufschlag
- Finaler Preis
- Settlement Vortag
- Differenz

### 5.4 Speicherlogik

Livepreise und OTC-Aufschläge werden gemeinsam gespeichert.

Es gibt keinen getrennten Speichern-Button.

Button:

- `Preise und Aufschläge speichern`

### 5.5 Chattext

Der Chattext enthält alle finalen Preise ohne Settlement-Differenz.

Reihenfolge:

1. Base Y+1
2. Peak Y+1
3. Base Y+2
4. Peak Y+2
5. Base Y+3
6. Peak Y+3

Formulierung neutral.

Beispiel:

```text
Aktuelle Indikationen Vertrieb:

Base 2027: 84,25 €/MWh
Peak 2027: 96,10 €/MWh
Base 2028: 79,40 €/MWh
Peak 2028: 91,75 €/MWh
Base 2029: 76,80 €/MWh
Peak 2029: 88,60 €/MWh
```

### 5.6 Mailtext

Der Mailtext enthält:

- alle finalen Preise
- zusätzlich je Produkt Differenz zum Settlement Vortag
- neutrale Formulierung

Keine echten Empfänger, kein Versand.

### 5.7 PFC-Prüfung

Die PFC-Prüfung kann als Expander oder Dialog dargestellt werden. Die PFC-Prüfung im Prototyp bezieht sich auf Base Y+1 bis Y+3, weil die PFC-Mockdateien je Jahr einen Mittelwert liefern.

Spalten:

- Produkt
- Lieferjahr
- PFC-Mittelwert
- Settlementpreis
- Differenz
- Zeitstempel PFC-Datei
- Zeitstempel Settlementpreis

Keine harte automatische Entscheidung.

## 6. Seite „Limitorder“

### 6.1 Ziel

Die Seite zeigt offene Limitorders, prüft sie gegen aktuelle Marktpreise und ermöglicht Statusaktionen.

### 6.2 Layout-Vorschlag

```text
# Limitorder

## Neue Limitorder anlegen
[Formular]
[Button: Limitorder speichern]

## Offene Limitorders
[Tabelle]
[Buttons: Ausgeführt / Gelöscht]

## Ausgelöste Limitorders
[Hervorhebung innerhalb der Tabelle]
```

### 6.3 Formularfelder

- Kunden-/Partner-Alias
- Mengen Y0 bis Y+4 in MWh
- Trigger-Preis: Base/Peak + Lieferjahr
- Auslöseart
- Limitpreis
- Verantwortlicher Handel
- Verantwortlicher Vertrieb
- optional gültig bis

### 6.4 Auslösearten

- Partner kauft, wenn Preis > Limit
- Partner kauft, wenn Preis < Limit
- Partner verkauft, wenn Preis > Limit
- Partner verkauft, wenn Preis < Limit

### 6.5 Validierung

Die App erzwingt:

- Partner kauft → befüllte Mengen müssen positiv sein
- Partner verkauft → befüllte Mengen müssen negativ sein
- mindestens ein Mengenfeld muss ungleich 0 sein

### 6.6 Prüfung gegen Marktpreise

Eine Limitorder ist ausgelöst, wenn die Bedingung gegen den aktuellen Marktpreis des Trigger-Preises erfüllt ist.

Beispiele:

```text
Partner kauft, wenn Preis < Limit:
aktueller Marktpreis < Limitpreis
```

```text
Partner verkauft, wenn Preis > Limit:
aktueller Marktpreis > Limitpreis
```

### 6.7 Aktionen

Button `Ausgeführt`:

- erzeugt ein untertägiges Geschäft
- Datum = heute
- Partner-Alias = Alias der Limitorder
- Mengen = Mengen der Limitorder
- Quelle = `limit_order`
- setzt Limitorder-Status auf `ausgeführt`

Button `Gelöscht`:

- setzt Limitorder-Status auf `gelöscht`

## 7. Seite „Handelskalender“

### 7.1 Ziel

Die Seite zeigt geplante und fällige Handelskalendereinträge und ermöglicht deren Erledigung.

### 7.2 Layout-Vorschlag

```text
# Handelskalender

## Neuen Kalendereintrag anlegen
[Formular]
[Button: Eintrag speichern]

## Fällige und geplante Einträge
[Tabelle]
[Button: Erledigt]
```

### 7.3 Anzeige

Die Standardansicht zeigt:

- Einträge ab heute
- zusätzlich überfällige, nicht erledigte Einträge
- keine erledigten Einträge

### 7.4 Fälligkeitslogik

```text
Fällig, wenn:
Datum <= heute
und Status != erledigt
```

Fällige und überfällige Einträge werden hervorgehoben.

### 7.5 Formularfelder

- Datum
- Partner-Alias
- Richtung: Partner kauft / Partner verkauft
- Mengen Y0 bis Y+4 in MWh

### 7.6 Validierung

- Partner kauft → befüllte Mengen müssen positiv sein
- Partner verkauft → befüllte Mengen müssen negativ sein
- mindestens ein Mengenfeld muss ungleich 0 sein

### 7.7 Aktion „Erledigt“

Beim Klick auf `Erledigt`:

- wird ein untertägiges Geschäft erzeugt
- Datum = heutiges Datum
- Partner-Alias wird übernommen
- Mengen werden übernommen
- Quelle = `trading_calendar`
- Handelskalendereintrag wird auf `erledigt` gesetzt
- Position wird automatisch neu berechnet

Die Datumsregel ist fachlich bestätigt: Für das automatisch erzeugte untertägige Geschäft wird das heutige Datum verwendet.
