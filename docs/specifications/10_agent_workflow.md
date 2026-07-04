# Agent-Workflow: Claude Code implementiert, Codex reviewt

## 1. Ziel

Dieses Dokument beschreibt den empfohlenen Arbeitsablauf mit zwei Coding-Agenten:

```text
Claude Code = Umsetzung
Codex       = Review
```

Ziel ist eine strukturierte, kontrollierte Entwicklung des Streamlit-/SQLite-Prototyps.

## 2. Grundprinzip

Nicht alles auf einmal bauen.

Besser:

```text
Spezifikation lesen
   ↓
kleines Arbeitspaket mit Claude Code umsetzen
   ↓
lokal starten / Tests ausführen
   ↓
Codex Review durchführen
   ↓
Claude Code lässt Review-Fixes einfließen
   ↓
nächstes Arbeitspaket
```

## 3. Empfohlene Reihenfolge

| Phase | Claude Code | Codex |
|---:|---|---|
| 1 | Projektstruktur und leere App | Strukturreview |
| 2 | DB-Modelle und Initialisierung | DB-Review |
| 3 | Domain-Logik und Tests | Fachlogik-Review |
| 4 | Position-Seite | Positionsreview |
| 5 | Preise-Seite | Preisreview |
| 6 | Excel-/PFC-Mockdatenimport | Importreview |
| 7 | Limitorder-Seite | Limitorder-Review |
| 8 | Handelskalender-Seite | Handelskalender-Review |
| 9 | End-to-End-Polish | Finalreview |

## 4. Empfohlene Git-Arbeitsweise

Auch für einen Prototypen sollte der Stand nachvollziehbar bleiben.

Empfehlung:

```bash
git init
git add .
git commit -m "Initial specification"
```

Danach je Arbeitspaket:

```bash
git checkout -b feature/01-project-skeleton
# Claude Code implementiert
git diff
git status
# lokal testen
git add .
git commit -m "Add Streamlit project skeleton"
# Codex Review auf den Stand anwenden
```

Für kleine lokale Prototypen reicht auch ein einzelner Branch, aber nach jedem Arbeitspaket sollte ein Commit entstehen.

## 5. Claude-Code-Ablauf je Arbeitspaket

Claude Code soll nach jedem Arbeitspaket diese Zusammenfassung liefern:

```text
Geänderte Dateien:
- ...

Umgesetzt:
- ...

Ausgeführt:
- streamlit run app.py / pytest / Seed-Skript / nicht ausgeführt

Annahmen:
- ...

Offene Punkte:
- ...
```

## 6. Codex-Review-Ablauf je Arbeitspaket

Codex soll immer gegen die Spezifikation prüfen, nicht nur gegen allgemeinen Codegeschmack.

Review-Fokus:

```text
1. Fachregeln korrekt?
2. Prototyp bewusst einfach gehalten?
3. Schichten sauber getrennt?
4. Keine risiko-kritische Automatisierung eingebaut?
5. Tests für zentrale Regeln vorhanden?
```

## 7. Fix-Ablauf nach Review

Wenn Codex Findings liefert, Claude Code nicht alles neu schreiben lassen.

Besserer Prompt:

```text
Bitte behebe nur die folgenden Codex-Review-Punkte minimal-invasiv:

1. ...
2. ...
3. ...

Ändere keine fachlichen Regeln ohne Rückfrage.
Führe danach die passenden Tests aus und liste die Änderungen auf.
```

## 8. Wann Rückfrage nötig ist

Claude Code oder Codex sollen bei diesen Punkten nicht raten:

| Thema | Warum Rückfrage nötig? |
|---|---|
| uneindeutige Kauf-/Verkaufsperspektive | hohes fachliches Fehlerrisiko |
| unklare Excel-Zellbereiche | Import könnte falsche Daten übernehmen |
| abweichende Jahreslogik | Position und Preise könnten falsch gemappt werden |
| unklare Auslösebedingung Limitorder | Risiko falscher Trigger |
| fehlende PFC- oder Settlementdaten | Defaultdaten müssen klar markiert werden |

## 9. Definition of Done für den Prototyp

Der Prototyp gilt als fachlich ausreichend umgesetzt, wenn:

| Bereich | Kriterium |
|---|---|
| Start | App startet mit `streamlit run app.py` |
| DB | SQLite wird erzeugt und mit Mockdaten befüllt |
| Backup | Initiales DB-Backup existiert |
| Position | PMS-Position, untertägige Geschäfte und simulierte Position werden angezeigt |
| Limit | Limit je Jahr 1,00 MW auf Absolutwert wird geprüft |
| Preise | Marktpreise, Aufschläge, Settlementvergleich, Chat-/Mailtext funktionieren |
| PFC | PFC-Prüfung zeigt Mittelwerte und Zeitstempel |
| Limitorder | Triggerprüfung, Hervorhebung, Ausgeführt/Gelöscht funktionieren |
| Handelskalender | Fälligkeit, Erledigt-Button und Geschäftserzeugung funktionieren |
| Tests | zentrale Domain-Tests laufen |
| Sicherheit | keine automatische Handelsausführung ohne Nutzerbutton |
| UI | keine echte E-Mail, kein Reset-Button, keine unnötige Startseite |

## 10. Demo-Checkliste

Vor einer Demo sollte geprüft werden:

```text
[ ] App startet ohne Fehler
[ ] Datenbank ist befüllt
[ ] Position-Seite zeigt Y0 bis Y+4
[ ] Limitverletzung ist sichtbar, falls vorhanden
[ ] Untertägiges Geschäft kann eingefügt werden
[ ] Untertägiges Geschäft kann gelöscht werden
[ ] Preisänderung + Aufschlag kann gespeichert werden
[ ] Chattext wird korrekt erzeugt
[ ] Mailtext enthält Settlement-Differenz
[ ] PFC-Prüfung zeigt drei Jahre
[ ] Limitorder kann angelegt werden
[ ] Ausgeführte Limitorder erzeugt untertägiges Geschäft
[ ] Handelskalendereintrag kann angelegt werden
[ ] Erledigter Handelskalendereintrag erzeugt untertägiges Geschäft
[ ] pytest läuft erfolgreich oder bekannte Ausnahmen sind dokumentiert
```

## 11. Klare Arbeitsteilung

Claude Code soll bevorzugt:

```text
- Dateien anlegen
- Code schreiben
- Tests schreiben
- README aktualisieren
- Bugs beheben
```

Codex soll bevorzugt:

```text
- Code gegen Spezifikation prüfen
- Risiken erkennen
- falsche Annahmen markieren
- Testlücken benennen
- minimal notwendige Fixes empfehlen
```

Codex sollte nicht versuchen, die App nach eigenem Geschmack in eine größere Architektur umzubauen.
