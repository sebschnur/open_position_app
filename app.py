"""Einstiegspunkt der Streamlit-App (Energiehandels-Prototyp).

Es gibt bewusst keine separate Startseite mit Fachinhalt. Die vier Fachseiten
liegen unter ``pages/`` und werden von Streamlit automatisch in der Navigation
angezeigt. Auffaelligkeiten werden direkt auf der jeweiligen Fachseite
hervorgehoben (siehe docs/specifications/01_fachliche_funktionen.md).

Beim Start wird sichergestellt, dass die SQLite-Datenbank existiert und mit
Mockdaten befuellt ist (siehe docs/specifications/04_workflows_automatisierungen.md,
Abschnitt 2).
"""

import streamlit as st

from src.services.initialization_service import ensure_database_ready

st.set_page_config(page_title="Energiehandels-Prototyp", layout="wide")


@st.cache_resource
def _init_database_once() -> str:
    return ensure_database_ready()


db_status = _init_database_once()

st.title("Energiehandels-Prototyp")
st.info(
    "Waehle links eine Fachseite: **Position**, **Preise**, **Limitorder** "
    "oder **Handelskalender**.\n\n"
    "Hinweis: Dies ist ein Prototyp mit Mockdaten. Die Fachlogik wird "
    "schrittweise gemaess Spezifikation implementiert."
)
st.caption(f"Datenbankstatus: {db_status}")
