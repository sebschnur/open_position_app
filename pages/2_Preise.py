"""Seite: Preise / Vertriebsinfos.

Vorgabe: docs/specifications/03_streamlit_ui_konzept.md, Abschnitt 5.

Marktpreis und OTC-Aufschlag werden ueber ein Formular gepflegt und
gemeinsam gespeichert (kein getrennter Speichern-Button). Chat- und
Mailtext werden ueber je einen eigenen Button erzeugt - kein echter
Mailversand, nur kopierbarer Text.
"""

import datetime as dt

import pandas as pd
import streamlit as st

from src.config import PRICE_PRODUCT_ORDER_TABLE
from src.db.database import SessionLocal
from src.services.price_service import (
    get_chat_text,
    get_mail_text,
    get_pfc_check_rows,
    get_price_table,
    save_prices_and_surcharges,
)

st.title("Preise / Vertriebsinfos")

today = dt.date.today()
current_year = today.year


def _offset_from_label(label: str) -> int:
    return int(label.replace("Y+", ""))


# --- Preise und Aufschlaege (Formular) ----------------------------------

st.subheader("Preise und Aufschlaege")
st.caption(
    "Marktpreis und OTC-Aufschlag werden gemeinsam gespeichert - "
    "es gibt keinen getrennten Speichern-Button."
)

with SessionLocal() as session:
    price_rows = get_price_table(session, today=today)
price_rows_by_key = {(row.product_type, row.delivery_year): row for row in price_rows}

with st.form("prices_and_surcharges_form"):
    header_cols = st.columns([2, 2, 2])
    header_cols[0].markdown("**Produkt**")
    header_cols[1].markdown("**Marktpreis EUR/MWh**")
    header_cols[2].markdown("**OTC-Aufschlag EUR/MWh**")

    input_keys = []
    for product_type, year_label in PRICE_PRODUCT_ORDER_TABLE:
        delivery_year = current_year + _offset_from_label(year_label)
        row = price_rows_by_key[(product_type, delivery_year)]
        cols = st.columns([2, 2, 2])
        cols[0].write(row.label)
        cols[1].number_input(
            f"Marktpreis {row.label}",
            value=row.market_price_eur_mwh,
            step=0.01,
            format="%.2f",
            label_visibility="collapsed",
            key=f"market_price_{product_type}_{delivery_year}",
        )
        cols[2].number_input(
            f"OTC-Aufschlag {row.label}",
            value=row.otc_surcharge_eur_mwh,
            step=0.01,
            format="%.2f",
            label_visibility="collapsed",
            key=f"surcharge_{product_type}_{delivery_year}",
        )
        input_keys.append((product_type, delivery_year))

    submitted = st.form_submit_button("Preise und Aufschlaege speichern")

if submitted:
    entries = [
        {
            "product_type": product_type,
            "delivery_year": delivery_year,
            "market_price_eur_mwh": st.session_state[f"market_price_{product_type}_{delivery_year}"],
            "otc_surcharge_eur_mwh": st.session_state[f"surcharge_{product_type}_{delivery_year}"],
        }
        for product_type, delivery_year in input_keys
    ]
    with SessionLocal() as session:
        save_prices_and_surcharges(session, entries)
    st.success("Preise und Aufschlaege gespeichert.")
    st.rerun()

# --- Preisvergleich Settlement -------------------------------------------

st.subheader("Preisvergleich Settlement")

with SessionLocal() as session:
    price_rows = get_price_table(session, today=today)

comparison_df = pd.DataFrame(
    [
        {
            "Produkt": row.label,
            "Marktpreis": row.market_price_eur_mwh,
            "OTC-Aufschlag": row.otc_surcharge_eur_mwh,
            "Finaler Preis": row.final_price_eur_mwh,
            "Settlement Vortag": row.settlement_price_eur_mwh,
            "Differenz": row.difference_eur_mwh,
        }
        for row in price_rows
    ]
)

st.dataframe(
    comparison_df,
    hide_index=True,
    width="stretch",
    column_config={
        col: st.column_config.NumberColumn(format="%.2f")
        for col in ["Marktpreis", "OTC-Aufschlag", "Finaler Preis", "Settlement Vortag", "Differenz"]
    },
)

# --- Chat-Kurztext --------------------------------------------------------

st.subheader("Chat-Kurztext")

with SessionLocal() as session:
    if "chat_text_area" not in st.session_state:
        st.session_state["chat_text_area"] = get_chat_text(session, today=today)
    if st.button("Chattext erzeugen"):
        st.session_state["chat_text_area"] = get_chat_text(session, today=today)

st.code(st.session_state["chat_text_area"], language=None)

# --- Mailtext --------------------------------------------------------------

st.subheader("Mailtext")

with SessionLocal() as session:
    if "mail_text_area" not in st.session_state:
        st.session_state["mail_text_area"] = get_mail_text(session, today=today)
    if st.button("Mailtext erzeugen"):
        st.session_state["mail_text_area"] = get_mail_text(session, today=today)

st.code(st.session_state["mail_text_area"], language=None)

# --- PFC-Pruefung ----------------------------------------------------------

st.subheader("PFC-Pruefung")

with st.expander("PFC-Pruefung anzeigen"):
    with SessionLocal() as session:
        pfc_rows = get_pfc_check_rows(session, today=today)

    if not pfc_rows:
        st.info("Keine PFC-Daten vorhanden.")
    else:
        pfc_df = pd.DataFrame(
            [
                {
                    "Produkt": row.label,
                    "PFC-Mittelwert": row.pfc_mean_eur_mwh,
                    "Settlementpreis": row.settlement_price_eur_mwh,
                    "Differenz": row.difference_eur_mwh,
                    "Zeitstempel PFC-Datei": row.pfc_file_timestamp.isoformat(sep=" "),
                    "Zeitstempel Settlement": (
                        row.settlement_timestamp.isoformat(sep=" ") if row.settlement_timestamp else "-"
                    ),
                }
                for row in pfc_rows
            ]
        )
        st.dataframe(
            pfc_df,
            hide_index=True,
            width="stretch",
            column_config={
                "PFC-Mittelwert": st.column_config.NumberColumn(format="%.2f"),
                "Settlementpreis": st.column_config.NumberColumn(format="%.2f"),
                "Differenz": st.column_config.NumberColumn(format="%.2f"),
            },
        )
        st.caption("Keine harte automatische Ampellogik - reine Anzeige zur fachlichen Pruefung.")
