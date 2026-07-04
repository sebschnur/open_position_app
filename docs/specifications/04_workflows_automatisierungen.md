# Workflows und Automatisierungen

## 1. Grundsatz

Der Prototyp automatisiert keine risiko-kritischen Handelsentscheidungen.

Er automatisiert nur unterstützende Arbeitsschritte:

- Berechnungen
- Statusprüfungen
- Hervorhebungen
- Texterzeugung
- Überführung erledigter/geprüfter Einträge in untertägige Geschäfte

Die finale fachliche Entscheidung bleibt beim Nutzer.

## 2. Workflow: App-Start und Datenbankinitialisierung

### 2.1 Ziel

Beim Start soll eine funktionsfähige SQLite-Datenbank mit Mock-Daten vorhanden sein.

### 2.2 Ablauf

```text
App startet
  ↓
Prüfen, ob data/app.db existiert
  ↓
Prüfen, ob Tabellen vorhanden und befüllt sind
  ↓
Falls ja:
  App verwendet vorhandene DB
  ↓
Falls nein:
  DB-Schema erzeugen
  Mock-Daten laden
  initiales Backup erzeugen
```

### 2.3 Mock-Datenquelle

Im Ziel sollen Mock-Daten aus einer bereinigten Excel-Datei gelesen werden.

Die konkrete Feldzuordnung wird später spezifiziert.

## 3. Workflow: Position anzeigen

### 3.1 Ziel

Die App zeigt die aktuelle simulierte Position je Kalenderjahr.

### 3.2 Ablauf

```text
PMS-Mock-Positionen aus DB lesen
  ↓
Untertägige Geschäfte aus DB lesen
  ↓
MWh je Jahr in MW umrechnen
  ↓
PMS-Position MW + untertägige MW = simulierte Position MW
  ↓
Limitprüfung je Jahr durchführen
  ↓
Tabelle anzeigen und Limitverletzungen hervorheben
```

### 3.3 Limitprüfung

```text
limit_mw = 1.0
is_breached = abs(simulated_position_mw) > limit_mw
utilization_pct = abs(simulated_position_mw) / limit_mw * 100
```

## 4. Workflow: Untertägiges Geschäft manuell einfügen

### 4.1 Ablauf

```text
Nutzer erfasst Datum, Partner-Alias und Mengen Y0 bis Y+4
  ↓
App prüft, dass mindestens eine Menge ungleich 0 ist
  ↓
App speichert untertägiges Geschäft
  ↓
Position wird automatisch neu berechnet
```

### 4.2 Besonderheit

Es gibt kein Richtungsfeld. Die Richtung ergibt sich aus dem Vorzeichen.

## 5. Workflow: Untertägiges Geschäft löschen

### 5.1 Ablauf

```text
Nutzer klickt bei untertägigem Geschäft auf „Löschen“
  ↓
Datensatz wird gelöscht
  ↓
Position wird automatisch neu berechnet
```

Hinweis: Da keine Historisierung gefordert ist, ist physisches Löschen im Prototyp akzeptabel.

## 6. Workflow: Preise und Aufschläge speichern

### 6.1 Ablauf

```text
Nutzer gibt Marktpreise und OTC-Aufschläge für 6 Produkte ein
  ↓
Nutzer klickt „Preise und Aufschläge speichern“
  ↓
App validiert numerische Eingaben
  ↓
App speichert Marktpreise und Aufschläge gemeinsam
  ↓
Finale Preise werden neu berechnet
  ↓
Settlement-Differenzen werden aktualisiert angezeigt
```

### 6.2 Produkte

- Base Y+1
- Base Y+2
- Base Y+3
- Peak Y+1
- Peak Y+2
- Peak Y+3

## 7. Workflow: Chattext erzeugen

### 7.1 Ablauf

```text
Aktuelle Marktpreise und OTC-Aufschläge aus DB lesen
  ↓
Finale Preise berechnen
  ↓
Produkte in Chat-Reihenfolge sortieren
  ↓
neutralen Text erzeugen
  ↓
kopierbares Textfeld anzeigen
```

### 7.2 Chat-Reihenfolge

1. Base Y+1
2. Peak Y+1
3. Base Y+2
4. Peak Y+2
5. Base Y+3
6. Peak Y+3

## 8. Workflow: Mailtext erzeugen

### 8.1 Ablauf

```text
Aktuelle Marktpreise und OTC-Aufschläge aus DB lesen
  ↓
Settlementpreise des Vortages aus DB lesen
  ↓
Finale Preise berechnen
  ↓
Differenzen berechnen
  ↓
neutralen Mailtext erzeugen
  ↓
kopierbares Textfeld anzeigen
```

Kein echter E-Mail-Versand.

## 9. Workflow: PFC-Prüfung anzeigen

### 9.1 Ablauf

```text
PFC-Mittelwerte aus DB lesen
  ↓
Settlementpreise aus DB lesen
  ↓
Zeitstempel lesen
  ↓
Vergleichstabelle anzeigen
```

### 9.2 Kein harter Entscheidungsautomat

Die App zeigt Daten. Der Nutzer entscheidet fachlich, ob die PFC aktuell/plausibel ist.

## 10. Workflow: Limitorder prüfen

### 10.1 Ablauf

```text
Offene Limitorders aus DB lesen
  ↓
Aktuelle Marktpreise aus DB lesen
  ↓
Je Limitorder den passenden Trigger-Preis bestimmen
  ↓
Bedingung gegen Limitpreis prüfen
  ↓
Ausgelöste Orders hervorheben
```

### 10.2 Bedingungen

| Auslöseart | Bedingung |
|---|---|
| Partner kauft, wenn Preis > Limit | Marktpreis > Limitpreis |
| Partner kauft, wenn Preis < Limit | Marktpreis < Limitpreis |
| Partner verkauft, wenn Preis > Limit | Marktpreis > Limitpreis |
| Partner verkauft, wenn Preis < Limit | Marktpreis < Limitpreis |

Für die aktuellen Excel-Mockdaten ist nur der Fall `Partner kauft, wenn Preis <= Limit` relevant. Das Seed-Skript soll `Kauf-Limit` daher als `Marktpreis <= Limitpreis` interpretieren.

Die Richtung ändert nicht die Preisvergleichslogik, sondern die erwartete Mengenrichtung.

## 11. Workflow: Limitorder ausführen

### 11.1 Ablauf

```text
Nutzer prüft ausgelöste Limitorder
  ↓
Nutzer klickt „Ausgeführt“
  ↓
App erzeugt untertägiges Geschäft
  ↓
App setzt Limitorder auf Status „ausgeführt“
  ↓
Position wird neu berechnet
```

### 11.2 Erzeugtes untertägiges Geschäft

| Feld | Wert |
|---|---|
| Datum | heutiges Datum |
| Partner-Alias | Partner-Alias der Limitorder |
| Mengen | Mengen der Limitorder |
| Quelle | `limit_order` |
| Source-ID | ID der Limitorder |

## 12. Workflow: Limitorder löschen

### 12.1 Ablauf

```text
Nutzer klickt „Gelöscht“
  ↓
Status der Limitorder wird auf „gelöscht“ gesetzt
  ↓
Order verschwindet aus der Standardansicht offener Orders
```

## 13. Workflow: Handelskalender anzeigen

### 13.1 Ablauf

```text
Handelskalendereinträge aus DB lesen
  ↓
Einträge filtern:
  - Datum >= heute
  - oder Datum < heute und Status != erledigt
  ↓
Fällige Einträge bestimmen:
  Datum <= heute und Status != erledigt
  ↓
Tabelle anzeigen
  ↓
Fällige/überfällige Einträge hervorheben
```

## 14. Workflow: Handelskalendereintrag anlegen

### 14.1 Ablauf

```text
Nutzer erfasst Datum, Partner-Alias, Richtung und Mengen
  ↓
App validiert Vorzeichen gegen Richtung
  ↓
App speichert Handelskalendereintrag mit Status „geplant“
```

### 14.2 Validierung

| Richtung | Erwartetes Vorzeichen |
|---|---:|
| Partner kauft | positiv |
| Partner verkauft | negativ |

## 15. Workflow: Handelskalendereintrag erledigen

### 15.1 Ablauf

```text
Nutzer prüft fälligen Handelskalendereintrag
  ↓
Nutzer klickt „Erledigt“
  ↓
App erzeugt untertägiges Geschäft
  ↓
App setzt Handelskalendereintrag auf „erledigt“
  ↓
Position wird neu berechnet
```

### 15.2 Erzeugtes untertägiges Geschäft

| Feld | Wert |
|---|---|
| Datum | heutiges Datum |
| Partner-Alias | Partner-Alias des Kalendereintrags |
| Mengen | Mengen des Kalendereintrags |
| Quelle | `trading_calendar` |
| Source-ID | ID des Kalendereintrags |

## 16. Offene fachliche Klärpunkte für später

| Punkt | Status |
|---|---|
| genaue Excel-Felder für Mock-Datenimport | später zu klären |
| konkrete Mock-Kunden/-Partner | später aus bereinigter Excel-Datei lesen |
| Mailtext-Formulierung final | später fachlich verfeinern |
| PFC-Prüfung: Base/Peak/Jahreslogik exakt | später anhand Excel und Mock-Daten prüfen |
| Status „abgelaufen“ bei Limitorders automatisch oder manuell | später klären |
| Datum des erzeugten Geschäfts aus Handelskalender: heutiges Datum oder Fälligkeitsdatum | geklärt: heutiges Datum verwenden |
