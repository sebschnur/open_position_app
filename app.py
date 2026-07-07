"""Einstiegspunkt der Streamlit-App (Energiehandels-Prototyp).

Die App nutzt die ``st.navigation``/``st.Page``-Navigation: Dieses Skript ist der
einzige Einstiegspunkt und laeuft bei jedem Seitenwechsel von oben durch. Layout
und globales CSS werden hier genau einmal ueber ``apply_global_layout()`` gesetzt
- damit gelten sie automatisch fuer jede Fachseite, ohne dass eine Seite den
Aufruf selbst setzen (und vergessen) koennte.

Die vier Fachseiten liegen als eigenstaendige Skripte unter ``views/``. Es gibt
eine schlichte Uebersichts-Startseite; Auffaelligkeiten werden direkt auf der
jeweiligen Fachseite hervorgehoben (siehe docs/specifications/01_fachliche_funktionen.md).

Beim Start wird sichergestellt, dass die SQLite-Datenbank existiert und mit
Mockdaten befuellt ist (siehe docs/specifications/04_workflows_automatisierungen.md,
Abschnitt 2).
"""

import streamlit as st

from src.services.initialization_service import ensure_database_ready
from src.ui_helpers import apply_global_layout

# Muss der erste Streamlit-Aufruf sein (set_page_config) und gilt fuer alle Seiten.
apply_global_layout()


@st.cache_resource
def _init_database_once() -> str:
    return ensure_database_ready()


db_status = _init_database_once()


def _uebersicht() -> None:
    """Schlichte Startseite ohne Fachinhalt."""
    st.title("Energiehandels-Prototyp")
    st.info(
        "Waehle links eine Fachseite: **Position**, **Preise**, **Limitorder** "
        "oder **Handelskalender**.\n\n"
        "Hinweis: Dies ist ein Prototyp mit Mockdaten. Die Fachlogik wird "
        "schrittweise gemaess Spezifikation implementiert."
    )
    st.caption(f"Datenbankstatus: {db_status}")


_pages = [
    st.Page(_uebersicht, title="Übersicht", default=True),
    st.Page("views/position.py", title="Position"),
    st.Page("views/preise.py", title="Preise"),
    st.Page("views/limitorder.py", title="Limitorder"),
    st.Page("views/handelskalender.py", title="Handelskalender"),
]

st.navigation(_pages).run()
