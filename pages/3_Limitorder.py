"""Seite: Limitorder.

Vorgabe: docs/specifications/03_streamlit_ui_konzept.md, Abschnitt 6.

Die Ausloeseart legt nur die Vergleichsrichtung gegen den Marktpreis fest
(siehe limit_order_logic.py). Das erwartete Mengenvorzeichen wird davon
unabhaengig ueber die Ausloeseart hergeleitet und beim Speichern validiert
(siehe validation.py).
"""

import datetime as dt

import streamlit as st

from src.config import PRICE_PRODUCT_ORDER_TABLE
from src.db.database import SessionLocal
from src.domain.limit_order_logic import TRIGGER_CONDITION_LABELS
from src.format_utils import format_de
from src.services.limit_order_service import (
    add_limit_order,
    get_open_limit_order_rows,
    mark_deleted,
    mark_executed,
)
from src.ui_helpers import configure_wide_page
from src.user_context import get_current_username

configure_wide_page("Limitorder")

st.title("Limitorder")

today = dt.date.today()
current_year = today.year
username = get_current_username()
year_labels = [str(current_year + offset) for offset in range(5)]

st.caption(f"Angemeldeter Benutzer: **{username}** (wird bei jedem Eintrag gespeichert)")


def _offset_from_label(label: str) -> int:
    return int(label.replace("Y+", ""))


_TRIGGER_OPTIONS = [
    (product_type, current_year + _offset_from_label(year_label))
    for product_type, year_label in PRICE_PRODUCT_ORDER_TABLE
]
_TRIGGER_LABELS = [f"{product_type} {year}" for product_type, year in _TRIGGER_OPTIONS]
_TRIGGER_LABEL_TO_KEY = dict(zip(_TRIGGER_LABELS, _TRIGGER_OPTIONS))

_CONDITION_LABELS = list(TRIGGER_CONDITION_LABELS.values())
_CONDITION_LABEL_TO_KEY = {label: key for key, label in TRIGGER_CONDITION_LABELS.items()}

# --- Neue Limitorder anlegen ----------------------------------------------

years = [current_year + offset for offset in range(5)]

with st.expander("Neue Limitorder anlegen", expanded=False):
    st.caption(
        "Partner kauft: alle befuellten Mengen muessen positiv sein. "
        "Partner verkauft: alle befuellten Mengen muessen negativ sein."
    )

    with st.form("new_limit_order_form", clear_on_submit=True):
        partner_alias = st.text_input("Partner-/Kunden-Alias")

        qty_cols = st.columns(5)
        quantities = [
            col.number_input(f"Menge {year} MWh", value=0.0, step=100.0, format="%.0f")
            for col, year in zip(qty_cols, years)
        ]

        select_cols = st.columns(2)
        trigger_label = select_cols[0].selectbox("Trigger-Preis", _TRIGGER_LABELS)
        condition_label = select_cols[1].selectbox("Auslöseart", _CONDITION_LABELS)

        limit_price = st.number_input("Limitpreis €/MWh", value=0.0, step=0.01, format="%.2f")

        valid_until = st.date_input("Gültig bis (optional)", value=None)

        submitted = st.form_submit_button("Limitorder speichern")

if submitted:
    if not partner_alias.strip():
        st.error("Partner-/Kunden-Alias darf nicht leer sein.")
    else:
        trigger_product_type, trigger_delivery_year = _TRIGGER_LABEL_TO_KEY[trigger_label]
        trigger_condition = _CONDITION_LABEL_TO_KEY[condition_label]
        with SessionLocal() as session:
            errors = add_limit_order(
                session,
                partner_alias=partner_alias.strip(),
                quantity_y0_mwh=quantities[0],
                quantity_y1_mwh=quantities[1],
                quantity_y2_mwh=quantities[2],
                quantity_y3_mwh=quantities[3],
                quantity_y4_mwh=quantities[4],
                trigger_product_type=trigger_product_type,
                trigger_delivery_year=trigger_delivery_year,
                trigger_condition=trigger_condition,
                limit_price_eur_mwh=limit_price,
                username=username,
                valid_until=valid_until,
            )
        if errors:
            for error in errors:
                st.error(error)
        else:
            st.success("Limitorder gespeichert.")
            st.rerun()

# --- Offene Limitorders -----------------------------------------------------

st.subheader("Offene Limitorders")
st.caption("Ausgelöste Orders sind rot hervorgehoben. Es gibt keine automatische Ausführung.")

with SessionLocal() as session:
    order_rows = get_open_limit_order_rows(session)

if not order_rows:
    st.info("Keine offenen Limitorders vorhanden.")
else:
    # Auslöseart-Spalte 20% schmaler (3 -> 2.4), dafuer neue Spalte "Gültig bis".
    col_widths = [2, 1, 1, 1, 1, 1, 2, 2.4, 1, 1, 2, 2, 2, 2, 2]
    header_cols = st.columns(col_widths)
    for col, header in zip(
        header_cols,
        [
            "Partner-Alias", *year_labels,
            "Trigger", "Auslöseart", "Marktpreis", "Limitpreis", "Gültig bis",
            "Ausgelöst?", "Geändert von", "", "",
        ],
    ):
        col.markdown(f"**{header}**")

    for order in order_rows:
        cols = st.columns(col_widths)
        cols[0].write(order.partner_alias)
        cols[1].write(format_de(order.quantity_y0_mwh, 0))
        cols[2].write(format_de(order.quantity_y1_mwh, 0))
        cols[3].write(format_de(order.quantity_y2_mwh, 0))
        cols[4].write(format_de(order.quantity_y3_mwh, 0))
        cols[5].write(format_de(order.quantity_y4_mwh, 0))
        cols[6].write(order.trigger_label)
        cols[7].write(order.trigger_condition_label)
        cols[8].write(format_de(order.current_market_price_eur_mwh, 2))
        cols[9].write(format_de(order.limit_price_eur_mwh, 2))
        if order.valid_until and order.valid_until < today:
            # Gueltigkeitsdatum liegt in der Vergangenheit (gestern oder aelter).
            cols[10].markdown(f":red[**{order.valid_until.isoformat()}**]")
        else:
            cols[10].write(order.valid_until.isoformat() if order.valid_until else "-")
        if order.is_triggered:
            cols[11].markdown(":red[**Ja**]")
        else:
            cols[11].write("Nein")
        cols[12].write(order.last_modified_by)
        if cols[13].button("Ausgeführt", key=f"execute_order_{order.id}"):
            with SessionLocal() as session:
                mark_executed(session, order.id, username=username)
            st.success("Untertägiges Geschäft erzeugt, Limitorder ausgeführt.")
            st.rerun()
        if cols[14].button("Gelöscht", key=f"delete_order_{order.id}"):
            with SessionLocal() as session:
                mark_deleted(session, order.id, username=username)
            st.rerun()
