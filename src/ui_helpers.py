"""Gemeinsame UI-Helfer fuer die Streamlit-App.

Layout und CSS werden zentral im Einstiegsskript ``app.py`` gesetzt - direkt
bevor ``st.navigation(...).run()`` die gewaehlte Seite ausfuehrt. Weil ``app.py``
bei jedem Seitenwechsel von oben durchlaeuft, gilt beides automatisch fuer jede
Fachseite; eine einzelne Seite kann es nicht mehr vergessen (frueher musste jede
Seite ``configure_wide_page`` selbst als ersten Aufruf setzen).
"""

import streamlit as st

# Globales Seiten-CSS:
# - Button-Beschriftungen (z. B. "Ausgeführt", "Löschen") nicht umbrechen.
# - Die +/- Schrittregler der Zahlenfelder (st.number_input) ausblenden;
#   Werte werden direkt eingetippt.
_PAGE_CSS = """
<style>
.stButton button, .stFormSubmitButton button,
[data-testid="stButton"] button, [data-testid="stFormSubmitButton"] button {
    white-space: nowrap;
}
[data-testid="stNumberInputStepUp"],
[data-testid="stNumberInputStepDown"] {
    display: none;
}
</style>
"""


def apply_global_layout() -> None:
    """Aktiviert Wide-Layout und injiziert das globale Seiten-CSS.

    Muss der erste Streamlit-Aufruf der App sein (Vorgabe von
    ``st.set_page_config``) und wird ausschliesslich in ``app.py`` aufgerufen -
    NICHT je Seite. So ist sichergestellt, dass Layout und CSS auf allen Seiten
    greifen, ohne dass eine Seite den Aufruf vergessen kann.
    """
    st.set_page_config(page_title="Energiehandels-Prototyp", layout="wide")
    st.markdown(_PAGE_CSS, unsafe_allow_html=True)
