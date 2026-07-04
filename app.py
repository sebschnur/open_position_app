"""Einstiegspunkt der Streamlit-App (Energiehandels-Prototyp).

Es gibt bewusst keine separate Startseite mit Fachinhalt. Die vier Fachseiten
liegen unter ``pages/`` und werden von Streamlit automatisch in der Navigation
angezeigt. Auffaelligkeiten werden direkt auf der jeweiligen Fachseite
hervorgehoben (siehe docs/specifications/01_fachliche_funktionen.md).
"""

import streamlit as st

st.set_page_config(page_title="Energiehandels-Prototyp", layout="wide")

st.title("Energiehandels-Prototyp")
st.info(
    "Waehle links eine Fachseite: **Position**, **Preise**, **Limitorder** "
    "oder **Handelskalender**.\n\n"
    "Hinweis: Dies ist ein Prototyp mit Mockdaten. Die Fachlogik wird "
    "schrittweise gemaess Spezifikation implementiert."
)
