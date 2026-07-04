# Changelog

## Ergänzung: Settlementpreise und PFC-Mockdaten

- Settlementpreise werden im Prototyp aus `Vertriebsinfos!L14:L16` gelesen.
- Diese Settlementwerte gelten nur für Base Y+1 bis Y+3 und werden in SQLite gespeichert.
- Fehlende Peak-Settlementpreise oder leere Base-Werte dürfen als realistische Default-Mockdaten erzeugt werden.
- Drei PFC-Dateien im `.xlsx`-Format werden erwartet, z. B. `20260702_EEX_PFC_2028.xlsx`.
- Der PFC-Mittelwert steht in jeder PFC-Datei in Zelle `D2`.
- Das PFC-Generierungsdatum wird aus den ersten 8 Zeichen des Dateinamens gelesen.
- Das Lieferjahr wird aus dem Jahr im Dateinamen gelesen.
- Fehlende oder unvollständige PFC-Dateien dürfen im Prototyp durch Default-Mockdaten ersetzt werden, müssen aber im Importprotokoll gekennzeichnet werden.

## Ergänzung: bestätigte Importregeln

- Handelskalender: `Kauf` bedeutet sicher `Partner kauft von uns`.
- Handelskalender: `Verkauf` bedeutet entsprechend `Partner verkauft an uns`.
- Limitorder-Mockdaten: Es wird nur der Fall `Partner kauft von uns, wenn Preis <= Limit` verwendet.
- Leere Datumsfelder bei untertägigen Geschäften werden mit dem heutigen Datum befüllt; vorhandene Datumswerte werden übernommen.



## Ergänzung: Claude-Code-Umsetzung und Codex-Review

- Rollenverteilung festgelegt: Claude Code implementiert, Codex reviewt.
- Neue Datei `07_projektstruktur_claude_code.md` ergänzt.
- Neue Datei `08_claude_code_prompts.md` mit konkreten Claude-Code-Arbeitsprompts ergänzt.
- Neue Datei `09_codex_review_prompts.md` mit Review-Prompts und Checklisten für Codex ergänzt.
- Neue Datei `10_agent_workflow.md` mit empfohlenem Implementierungs-/Review-Ablauf ergänzt.
- `README.md` und `05_umsetzungsplan_codex_claude.md` aktualisiert.
