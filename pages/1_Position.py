"""Seite: Position.

Vorgabe: docs/specifications/03_streamlit_ui_konzept.md, Abschnitt 4.

Auf dieser Seite werden bewusst KEINE Begriffe "Kauf"/"Verkauf" verwendet.
Die Richtung ergibt sich ausschliesslich aus dem Vorzeichen der Menge
(siehe 01_fachliche_funktionen.md, Abschnitt 6).
"""

import datetime as dt

import altair as alt
import pandas as pd
import streamlit as st

from src.db.database import SessionLocal
from src.domain.position_logic import STATUS_LIMIT_BREACHED
from src.format_utils import format_de
from src.services.position_service import (
    add_intraday_trade,
    delete_intraday_trade,
    get_intraday_trade_rows,
    get_position_table,
)
from src.ui_helpers import configure_wide_page
from src.user_context import get_current_username

configure_wide_page("Position")

st.title("Position")

today = dt.date.today()
username = get_current_username()
year_labels = [str(today.year + offset) for offset in range(5)]
st.caption(f"Datenstand: {today.isoformat()} (Mockdaten)")
st.caption(f"Angemeldeter Benutzer: **{username}** (wird bei jedem Eintrag gespeichert)")

with SessionLocal() as session:
    position_rows = get_position_table(session, today=today)
    trade_rows = get_intraday_trade_rows(session)

# --- Offene Position je Kalenderjahr -----------------------------------

st.subheader("Offene Position je Kalenderjahr")

# Balkendiagramm ueber der Tabelle: simulierte (aktuelle) Position je Jahr in MW,
# rote gestrichelte Linien markieren das Limit (+/- 1,00 MW, da auf Absolutwert
# geprueft). Balken werden rot, wenn das Limit verletzt ist.
if position_rows:
    limit_mw = position_rows[0].limit_mw
    chart_df = pd.DataFrame(
        {
            "Kalenderjahr": [str(row.year) for row in position_rows],
            "Position MW": [row.simulated_position_mw for row in position_rows],
        }
    )
    bars = (
        alt.Chart(chart_df)
        .mark_bar()
        .encode(
            x=alt.X("Kalenderjahr:N", title="Kalenderjahr"),
            y=alt.Y("Position MW:Q", title="MW"),
            color=alt.condition(
                f"abs(datum['Position MW']) > {limit_mw}",
                alt.value("#d62728"),
                alt.value("#1f77b4"),
            ),
            tooltip=["Kalenderjahr", alt.Tooltip("Position MW:Q", format=".2f")],
        )
    )
    limit_lines = (
        alt.Chart(pd.DataFrame({"Limit MW": [limit_mw, -limit_mw]}))
        .mark_rule(color="red", strokeDash=[6, 4])
        .encode(y="Limit MW:Q")
    )
    st.altair_chart((bars + limit_lines).properties(height=280, width="container"))
    st.caption("Simulierte Position je Kalenderjahr in MW; rote Linie = Limit (±1,00 MW).")

position_df = pd.DataFrame(
    [
        {
            "Kalenderjahr": row.year,
            "PMS-Position MW": row.pms_position_mw,
            "Untertaegige Geschaefte MW": row.intraday_position_mw,
            "Simulierte Position MW": row.simulated_position_mw,
            "Limit MW": row.limit_mw,
            "Auslastung %": row.utilization_pct,
            "Status": row.status,
        }
        for row in position_rows
    ]
)


def _highlight_breach(row: pd.Series) -> list:
    if row["Status"] == STATUS_LIMIT_BREACHED:
        return ["background-color: #ffcccc"] * len(row)
    return [""] * len(row)


_MW_COLUMNS = [
    "PMS-Position MW",
    "Untertaegige Geschaefte MW",
    "Simulierte Position MW",
    "Limit MW",
]

# Deutsches Zahlenformat (1.234,56) ueber den pandas-Styler statt ueber
# column_config, das nur englische Formatierung unterstuetzt.
position_style = (
    position_df.style.apply(_highlight_breach, axis=1)
    .format(precision=2, thousands=".", decimal=",", na_rep="-", subset=_MW_COLUMNS)
    .format(precision=1, thousands=".", decimal=",", na_rep="-", subset=["Auslastung %"])
)

st.dataframe(
    position_style,
    hide_index=True,
    width="stretch",
)

# --- Neues untertaegiges Geschaeft erfassen ------------------------------

years = [today.year + offset for offset in range(5)]

with st.expander("Neues untertaegiges Geschaeft erfassen", expanded=False):
    st.caption(
        "Kein Richtungsfeld: positive Menge = Partner kauft von uns, "
        "negative Menge = Partner verkauft an uns."
    )

    with st.form("new_intraday_trade_form", clear_on_submit=True):
        trade_date = st.date_input("Datum", value=today)
        partner_alias = st.text_input("Partner-/Kunden-Alias")

        qty_cols = st.columns(5)
        quantities = [
            col.number_input(f"Menge {year} MWh", value=0.0, step=100.0, format="%.0f")
            for col, year in zip(qty_cols, years)
        ]

        submitted = st.form_submit_button("Einfuegen")

if submitted:
    if not partner_alias.strip():
        st.error("Partner-/Kunden-Alias darf nicht leer sein.")
    else:
        with SessionLocal() as session:
            errors = add_intraday_trade(
                session,
                trade_date=trade_date,
                partner_alias=partner_alias.strip(),
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
            st.success("Untertaegiges Geschaeft gespeichert. Position wurde aktualisiert.")
            st.rerun()

# --- Untertaegige Geschaefte --------------------------------------------

st.subheader("Untertaegige Geschaefte")

if not trade_rows:
    st.info("Noch keine untertaegigen Geschaefte erfasst.")
else:
    col_widths = [1, 2, 1, 1, 1, 1, 1, 2, 1, 1.5, 1]
    header_cols = st.columns(col_widths)
    for col, header in zip(
        header_cols,
        ["Datum", "Partner-Alias", *year_labels, "Interpretation", "Quelle", "Geändert von", ""],
    ):
        col.markdown(f"**{header}**")

    for trade in trade_rows:
        cols = st.columns(col_widths)
        if trade.trade_date < today:
            # Datum liegt in der Vergangenheit (gestern oder aelter).
            cols[0].markdown(f":red[**{trade.trade_date.isoformat()}**]")
        else:
            cols[0].write(trade.trade_date.isoformat())
        cols[1].write(trade.partner_alias)
        cols[2].write(format_de(trade.quantity_y0_mwh, 0))
        cols[3].write(format_de(trade.quantity_y1_mwh, 0))
        cols[4].write(format_de(trade.quantity_y2_mwh, 0))
        cols[5].write(format_de(trade.quantity_y3_mwh, 0))
        cols[6].write(format_de(trade.quantity_y4_mwh, 0))
        cols[7].write(trade.interpretation)
        cols[8].write(trade.source_type)
        cols[9].write(trade.last_modified_by)
        if cols[10].button("Loeschen", key=f"delete_trade_{trade.id}"):
            with SessionLocal() as session:
                delete_intraday_trade(session, trade.id)
            st.rerun()
