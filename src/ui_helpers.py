"""Gemeinsame UI-Helfer fuer die Streamlit-Seiten.

Streamlit fuehrt jede Datei unter ``pages/`` als eigenes Skript aus. Das in
``app.py`` gesetzte ``layout="wide"`` gilt dort NICHT - ohne eigenen
``set_page_config``-Aufruf rendern die Unterseiten im schmalen "centered"-
Layout. Deshalb setzt jede Seite das Wide-Layout selbst.
"""

import streamlit as st

# Button-Beschriftungen (z. B. "Ausgeführt", "Löschen") sollen nicht umbrechen.
_PAGE_CSS = """
<style>
.stButton button, .stFormSubmitButton button,
[data-testid="stButton"] button, [data-testid="stFormSubmitButton"] button {
    white-space: nowrap;
}
</style>
"""


def configure_wide_page(page_title: str) -> None:
    """Aktiviert Wide-Layout und das Seiten-CSS.

    Muss der erste Streamlit-Aufruf einer Seite sein (Vorgabe von
    ``st.set_page_config``).
    """
    st.set_page_config(page_title=page_title, layout="wide")
    st.markdown(_PAGE_CSS, unsafe_allow_html=True)
