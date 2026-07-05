# Fachliche Funktionen des Prototyps

## 1. Überblick

Die Anwendung besteht fachlich aus vier Hauptbereichen:

1. Position
2. Preise / Vertriebsinfos
3. Limitorder
4. Handelskalender

Es gibt keine separate Startseite. Auffälligkeiten werden direkt auf der jeweiligen Fachseite hervorgehoben.

```text
Streamlit-Seiten:
- Position
- Preise
- Limitorder
- Handelskalender
```

## 2. Tagesablauf im Zielprozess

Der heutige Excel-Prozess wird im Prototyp fachlich wie folgt abgebildet:

1. Anwendung öffnen.
2. Offene Position aus Mock-Datenbank anzeigen.
3. Untertägige Vertriebs- und Beschaffungsgeschäfte manuell erfassen.
4. Simulierte aktuelle Position automatisch neu berechnen.
5. Prüfen, ob das Limit von 1 MW Base je Kalenderjahr eingehalten wird.
6. PFC-/Settlement-Informationen anzeigen.
7. Live-Marktpreise und OTC-Aufschläge pflegen.
8. Chat- und Mailtext für den Vertrieb erzeugen.
9. Limitorders gegen aktuelle Marktpreise prüfen.
10. Ausgeführte Limitorders in untertägige Geschäfte überführen.
11. Handelskalendereinträge prüfen.
12. Erledigte Handelskalendereinträge in untertägige Geschäfte überführen.

## 3. Wesentliche fachliche Entscheidungen

Die Anwendung unterstützt insbesondere zwei Entscheidungen:

| Entscheidung | Unterstützende App-Funktion |
|---|---|
| Muss am Markt ein Geschäft getätigt werden, um die Position wieder in das Limit zu bringen? | Position, Limitauslastung, untertägige Geschäfte |
| Welche Marktpreise sollen an den Vertrieb kommuniziert werden? | Preise, OTC-Aufschläge, Settlement-Vergleich, Textgenerierung |

## 4. Wesentliche Ausgaben

| Ausgabe | Beschreibung |
|---|---|
| Offene Position und Limitauslastung | je Kalenderjahr in MW |
| Marktpreistext für Vertrieb | Chat-Text und längerer Mailtext |
| Untertägige Geschäfte | manuell oder aus Workflow erzeugt |
| Limitorder-Übersicht | offene, ausgelöste, ausgeführte oder gelöschte Orders |
| Handelskalender | geplante, fällige oder erledigte Aktionen |

## 5. Bereich Position

### 5.1 Ziel

Die Position-Seite zeigt je Kalenderjahr:

- Position aus Portfoliomanagementsystem
- Nettoeffekt untertägiger Geschäfte
- aktuelle simulierte Position
- Limit
- Limitauslastung
- Status/Hervorhebung

### 5.2 Berechnungslogik

```text
Aktuelle simulierte Position MW
=
Position aus Portfoliomanagementsystem MW
+
Nettoeffekt der untertägigen Geschäfte MW
```

Die Position wird nach jeder Änderung an den untertägigen Geschäften automatisch neu berechnet.

### 5.3 Anzeige je Kalenderjahr

| Spalte | Bedeutung |
|---|---|
| Kalenderjahr | aktuelles Jahr bis Y+4 |
| PMS-Position MW | Mock-Position aus Portfoliomanagementsystem |
| Untertägige Geschäfte MW | Nettoeffekt der manuell/workflowseitig erfassten Geschäfte |
| Simulierte Position MW | Summe aus PMS-Position und untertägigen Geschäften |
| Limit MW | 1,00 MW |
| Auslastung % | `abs(simulierte_position_mw) / limit_mw * 100` |
| Status | innerhalb Limit / Limit überschritten |

### 5.4 Limitlogik

Das Limit gilt je Kalenderjahr separat und auf den Absolutwert.

```text
Limit verletzt, wenn:
abs(simulierte_position_mw) > 1.0
```

1 MW Base entspricht:

| Jahrtyp | Stunden | MWh je 1 MW |
|---|---:|---:|
| normales Jahr | 8.760 | 8.760 MWh |
| Schaltjahr | 8.784 | 8.784 MWh |

Die App erkennt Schaltjahre automatisch.

## 6. Vorzeichen- und Richtungslogik

### 6.1 Grundregel

Die Anwendung verzichtet im Positionsbereich bewusst auf die Begriffe „Kauf“ und „Verkauf“. Die Richtung wird ausschließlich über das Mengenvorzeichen abgebildet.

```text
Positive Menge:
→ Partner/Kunde kauft von uns
→ unsere offene Position steigt

Negative Menge:
→ Partner/Kunde verkauft an uns
→ wir kaufen
→ unsere offene Position sinkt
```

### 6.2 Anwendung der Regel

| Bereich | Regel |
|---|---|
| Position | keine Kauf-/Verkaufsbegriffe, nur Vorzeichen |
| Untertägige Geschäfte | kein Richtungsfeld, nur Mengen mit Vorzeichen |
| Limitorder | Formulierung: „Partner kauft …“ / „Partner verkauft …“ |
| Handelskalender | Formulierung: „Partner kauft“ / „Partner verkauft“ |
| Berechnung | ausschließlich über Vorzeichenlogik |

### 6.3 UI-Sicherheit

Die UI sollte die Interpretation der Menge immer anzeigen.

Beispiel:

```text
Menge: +8.760 MWh
Interpretation: Partner kauft von uns
Positionswirkung: +1,00 MW
```

```text
Menge: -8.760 MWh
Interpretation: Partner verkauft an uns
Positionswirkung: -1,00 MW
```

## 7. Untertägige Geschäfte

### 7.1 Zweck

Untertägige Geschäfte sind manuelle Korrektur- und Ergänzungsdaten, bis sie am nächsten Tag im Portfoliomanagementsystem enthalten sind.

### 7.2 Erfassung

Untertägige Geschäfte werden über ein Formular auf der Position-Seite eingegeben.

Mindestfelder:

- Datum
- Partner-/Kunden-Alias
- Liefermenge aktuelles Jahr in MWh
- Liefermenge Y+1 in MWh
- Liefermenge Y+2 in MWh
- Liefermenge Y+3 in MWh
- Liefermenge Y+4 in MWh

Es gibt kein separates Richtungsfeld. Die Richtung ergibt sich aus dem Vorzeichen der Mengen.

### 7.3 Aktionen

- Einfügen
- Löschen

Nach jeder Änderung wird die Position automatisch neu berechnet.

## 8. Bereich Preise / Vertriebsinfos

### 8.1 Preisprodukte

Die Preise-Seite enthält genau diese Produkte in folgender Reihenfolge:

1. Base Y+1
2. Base Y+2
3. Base Y+3
4. Peak Y+1
5. Peak Y+2
6. Peak Y+3

Für Chat-Texte wird eine andere Reihenfolge verwendet:

1. Base Y+1
2. Peak Y+1
3. Base Y+2
4. Peak Y+2
5. Base Y+3
6. Peak Y+3

### 8.2 Spalten

| Spalte | Bedeutung |
|---|---|
| Produkt | Base/Peak + Lieferjahr |
| Marktpreis | aktueller Live-/Mock-Marktpreis |
| OTC-Aufschlag | gespeicherter Aufschlag je Produkt |
| Finaler Preis | Marktpreis + OTC-Aufschlag |
| Settlement Vortag | Settlementpreis aus SQLite |
| Differenz | Finaler Preis minus Settlement Vortag |

### 8.3 Berechnung

```text
Finaler Preis = Marktpreis + OTC-Aufschlag
Differenz = Finaler Preis - Settlement Vortag
```

Keine weitere Sonderlogik.

### 8.4 Bedienung

- Livepreise eintragen
- OTC-Aufschläge eintragen
- Livepreise und Aufschläge gemeinsam speichern
- Chattext erzeugen
- Mailtext erzeugen
- PFC-Prüfung anzeigen

Es gibt keine getrennte Speicheraktion für Livepreise und Aufschläge.

## 9. Settlement- und PFC-Prüfung

### 9.1 Settlementpreise

Settlementpreise werden im Prototyp aus SQLite gelesen.

Produkte:

- Base Y+1 bis Y+3
- Peak Y+1 bis Y+3

### 9.2 Preisvergleich

Der Prototyp zeigt je Produkt:

```text
Finaler Livepreis inkl. Aufschlag
versus
Settlementpreis Vortag
```

Differenz in €/MWh.

### 9.3 PFC-Prüfung

Die PFC-Aktualitätsprüfung ist im Prototyp eine Anzeige, keine harte automatische Ampellogik.

Anzuzeigen je Jahr/Produkt:

- PFC-Mittelwert
- Settlementpreis aus SQLite
- Differenz
- Zeitstempel der PFC-Datei
- Zeitstempel des Settlementpreises

## 10. Preis-Kommunikation an den Vertrieb

### 10.1 Kein echter Mailversand

Im Prototyp wird kein echter E-Mail-Versand umgesetzt.

Stattdessen erzeugt die App kopierbare Texte:

- Kurztext für Chat
- längerer Mailtext

### 10.2 Chat-Kurztext

Der Chat-Kurztext enthält alle finalen Preise, ohne Settlement-Differenzen.

Reihenfolge:

1. Base Y+1
2. Peak Y+1
3. Base Y+2
4. Peak Y+2
5. Base Y+3
6. Peak Y+3

Formulierung: neutral.

### 10.3 Mailtext

Der Mailtext enthält:

- alle finalen Preise
- zusätzlich die Differenz zum Settlement des Vortages
- neutrale Formulierung

Keine echten Empfänger.

## 11. Bereich Limitorder

### 11.1 Mindestfelder

Eine Limitorder enthält:

- Lieferjahr bzw. Mengen für aktuelles Jahr bis Y+4
- Liefermenge je Jahr in MWh
- Kunden-/Partner-Alias
- Limitpreis
- Trigger-Preis
- Auslöseart
- Status

Hinweis: Das frühere Feld „Verantwortlicher Handel/Vertrieb“ ist obsolet und
entfällt in der Eingabe. Die Nachvollziehbarkeit erfolgt über den automatisch
gespeicherten Benutzernamen (`last_modified_by`, siehe
`02_datenmodell_sqlite.md`, Grundsatz Nachvollziehbarkeit).

### 11.2 Trigger-Preis

Statt „Struktur“ wird der Begriff „Trigger-Preis“ verwendet.

Mögliche Trigger-Preise:

- Base Y+1
- Base Y+2
- Base Y+3
- Peak Y+1
- Peak Y+2
- Peak Y+3

Die Limitorder wird gegen den Marktpreis des gewählten Trigger-Preises geprüft.

### 11.3 Auslösearten

| Auslöseart | Erwartetes Mengenvorzeichen |
|---|---:|
| Partner kauft, wenn Preis > Limit | positiv |
| Partner kauft, wenn Preis < Limit | positiv |
| Partner verkauft, wenn Preis > Limit | negativ |
| Partner verkauft, wenn Preis < Limit | negativ |

Die App muss diese Vorzeichenlogik technisch erzwingen.

### 11.4 Status

- Offen
- Ausgeführt
- Gelöscht
- Abgelaufen

### 11.5 Prüfung

Die Prüfung erfolgt gegen aktuelle Marktpreise aus SQLite-Mockdaten.

Keine automatische Ausführung.

Die App markiert offene Limitorders, wenn die Auslösebedingung erfüllt ist.

### 11.6 Aktionen

- neue Limitorder speichern
- Limitorder auf „Ausgeführt“ setzen
- Limitorder auf „Gelöscht“ setzen

Beim Klick auf „Ausgeführt“ wird automatisch ein untertägiges Geschäft erzeugt.

## 12. Bereich Handelskalender

### 12.1 Mindestfelder

Ein Handelskalendereintrag enthält:

- Datum
- Kunden-/Partner-Alias
- Richtung: Partner kauft / Partner verkauft
- Mengen je Lieferjahr aktuelles Jahr bis Y+4
- Status

### 12.2 Status

- Geplant
- Fällig
- Erledigt

### 12.3 Anzeige

Die Standardansicht zeigt:

- Einträge ab heute
- zusätzlich überfällige, noch nicht erledigte Einträge
- keine erledigten Einträge

### 12.4 Fälligkeitslogik

```text
Fällig, wenn:
Datum <= heute
und Status != Erledigt
```

### 12.5 Aktionen

- neuen Handelskalendereintrag per Formular anlegen
- Eintrag auf „Erledigt“ setzen

Beim Klick auf „Erledigt“ wird automatisch ein untertägiges Geschäft erzeugt und der Handelskalendereintrag auf erledigt gesetzt.
