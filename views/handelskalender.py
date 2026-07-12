"""Seite: Handelskalender.

Vorgabe: docs/specifications/03_streamlit_ui_konzept.md, Abschnitt 7.

Die Standardansicht zeigt alle nicht erledigten Eintraege (auch ueberfaellige),
faellige/ueberfaellige Eintraege werden rot hervorgehoben. Es gibt keine
Sperre - "Erledigt" ist fuer jeden sichtbaren Eintrag klickbar (siehe
trading_calendar_service.py).
"""

import datetime as dt

import streamlit as st

from src.db.database import SessionLocal
from src.domain.trading_calendar_logic import DIRECTION_LABELS, STATUS_DUE
from src.format_utils import format_de
from src.services.trading_calendar_service import (
    add_calendar_entry,
    get_visible_calendar_rows,
    mark_deleted,
    mark_done,
)
from src.user_context import get_current_username

st.title("Handelskalender")

today = dt.date.today()
username = get_current_username()
year_labels = [str(today.year + offset) for offset in range(5)]

st.caption(
    f"Angemeldeter Benutzer: **{username}** (wird bei jedem Eintrag gespeichert)"
)

_DIRECTION_LABEL_TO_KEY = {label: key for key, label in DIRECTION_LABELS.items()}

# --- Neuen Kalendereintrag anlegen ------------------------------------------

years = [today.year + offset for offset in range(5)]

with st.expander("Neuen Kalendereintrag anlegen", expanded=False):
    st.caption(
        "Partner kauft: alle befuellten Mengen muessen positiv sein. "
        "Partner verkauft: alle befuellten Mengen muessen negativ sein."
    )

    with st.form("new_calendar_entry_form", clear_on_submit=True):
        top_cols = st.columns(2)
        due_date = top_cols[0].date_input("Datum", value=today)
        partner_alias = top_cols[1].text_input("Partner-/Kunden-Alias")

        direction_label = st.selectbox("Richtung", list(_DIRECTION_LABEL_TO_KEY.keys()))

        qty_cols = st.columns(5)
        quantities = [
            col.number_input(f"Menge {year} MWh", value=0.0, step=100.0, format="%.0f")
            for col, year in zip(qty_cols, years, strict=False)
        ]

        submitted = st.form_submit_button("Eintrag speichern")

if submitted:
    if not partner_alias.strip():
        st.error("Partner-/Kunden-Alias darf nicht leer sein.")
    else:
        direction = _DIRECTION_LABEL_TO_KEY[direction_label]
        with SessionLocal() as session:
            errors = add_calendar_entry(
                session,
                due_date=due_date,
                partner_alias=partner_alias.strip(),
                direction=direction,
                quantity_y0_mwh=quantities[0],
                quantity_y1_mwh=quantities[1],
                quantity_y2_mwh=quantities[2],
                quantity_y3_mwh=quantities[3],
                quantity_y4_mwh=quantities[4],
                username=username,
            )
        if errors:
            for error in errors:
                st.error(error)
        else:
            st.success("Kalendereintrag gespeichert.")
            st.rerun()

# --- Faellige und geplante Eintraege ----------------------------------------

st.subheader("Fällige und geplante Einträge")
st.caption(
    "Fällige/überfällige Einträge sind rot hervorgehoben. Erledigte Einträge werden ausgeblendet."
)

with SessionLocal() as session:
    calendar_rows = get_visible_calendar_rows(session, today=today)

if not calendar_rows:
    st.info("Keine offenen Kalendereinträge vorhanden.")
else:
    col_widths = [1, 2, 2, 1, 1, 1, 1, 1, 1, 1.5, 2, 2]
    header_cols = st.columns(col_widths)
    for col, header in zip(
        header_cols,
        [
            "Datum",
            "Partner-Alias",
            "Richtung",
            *year_labels,
            "Status",
            "Geändert von",
            "",
            "",
        ],
        strict=False,
    ):
        col.markdown(f"**{header}**")

    for row in calendar_rows:
        cols = st.columns(col_widths)
        cols[0].write(row.due_date.isoformat())
        cols[1].write(row.partner_alias)
        cols[2].write(row.direction_label)
        cols[3].write(format_de(row.quantity_y0_mwh, 0))
        cols[4].write(format_de(row.quantity_y1_mwh, 0))
        cols[5].write(format_de(row.quantity_y2_mwh, 0))
        cols[6].write(format_de(row.quantity_y3_mwh, 0))
        cols[7].write(format_de(row.quantity_y4_mwh, 0))
        if row.display_status == STATUS_DUE:
            cols[8].markdown(f":red[**{row.display_status}**]")
        else:
            cols[8].write(row.display_status)
        cols[9].write(row.last_modified_by)
        if cols[10].button("Ausgeführt", key=f"complete_entry_{row.id}"):
            with SessionLocal() as session:
                mark_done(session, row.id, username=username)
            st.success("Untertägiges Geschäft erzeugt, Eintrag ausgeführt.")
            st.rerun()
        if cols[11].button("Löschen", key=f"delete_entry_{row.id}"):
            with SessionLocal() as session:
                mark_deleted(session, row.id, username=username)
            st.rerun()
