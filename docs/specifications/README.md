# Spezifikationspaket: Excel zu Python + Streamlit + SQLite

Dieses Paket enthält die erste strukturierte Spezifikation für einen Prototypen zur Ablösung einer Excel-/VBA-Datei durch Python, Streamlit und SQLite.

## Dateien

| Datei | Zweck |
|---|---|
| `00_projektauftrag.md` | Ziel, Scope, Tech-Stack, Nicht-Ziele, Mock-Datenstrategie |
| `01_fachliche_funktionen.md` | Fachliche Funktionen, Seiten, Regeln, Vorzeichenlogik |
| `02_datenmodell_sqlite.md` | SQLite-/SQLAlchemy-Datenmodell und Validierungsregeln |
| `03_streamlit_ui_konzept.md` | UI-Konzept für die vier Streamlit-Seiten |
| `04_workflows_automatisierungen.md` | Workflows und unterstützende Automatisierungen |
| `05_umsetzungsplan_codex_claude.md` | Arbeitspakete und Prompts für Codex/Claude Code |
| `06_excel_mockdaten_import.md` | Zellbereiche und Mapping für den initialen Excel-Mockdatenimport |
| `07_projektstruktur_claude_code.md` | Zielstruktur und technische Leitplanken für Claude Code |
| `08_claude_code_prompts.md` | Konkrete Implementierungsprompts für Claude Code |
| `09_codex_review_prompts.md` | Review-Prompts und Checklisten für Codex |
| `10_agent_workflow.md` | Empfohlener Arbeitsablauf Claude Code → Codex Review → Fixes |
| `CHANGELOG.md` | Kurze Änderungshistorie der Spezifikation |

## Nächster Schritt

Die Spezifikation enthält nun ein Excel-Mockdaten-Mapping einschließlich der bestätigten Regeln für Handelskalender, Limitorder-Mockdaten, leere Datumsfelder, Settlementpreise und PFC-Prüfung.

Für Settlementpreise werden Base-Werte aus `Vertriebsinfos!L14:L16` gelesen. Für die PFC-Prüfung werden drei `.xlsx`-Dateien mit Dateimuster `YYYYMMDD_EEX_PFC_YYYY.xlsx` erwartet; der Mittelwert steht jeweils in `D2`. Fehlende Settlement-/PFC-Werte dürfen im Prototyp als realistische Default-Mockdaten erzeugt werden, müssen aber im Importprotokoll klar gekennzeichnet werden.

Damit kann Claude Code mit der Projektstruktur, Datenbankinitialisierung und dem Excel-Mockdatenimport beginnen. Codex wird anschließend als Review-Agent eingesetzt. Die detaillierten Prompts stehen in `08_claude_code_prompts.md` und `09_codex_review_prompts.md`.
