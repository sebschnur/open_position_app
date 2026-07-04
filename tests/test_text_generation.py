"""Tests fuer Chat-/Mailtext-Generierung (Arbeitspaket 5)."""

from src.domain.text_generation import PriceTextEntry, build_chat_text, build_mail_text


def test_chat_text_contains_all_entries_without_difference():
    entries = [
        PriceTextEntry(label="Base 2027", final_price_eur_mwh=84.25),
        PriceTextEntry(label="Peak 2027", final_price_eur_mwh=96.10),
    ]
    text = build_chat_text(entries)

    assert "Base 2027: 84,25 €/MWh" in text
    assert "Peak 2027: 96,10 €/MWh" in text
    assert "Differenz" not in text
    assert "Settlement" not in text


def test_chat_text_preserves_entry_order():
    entries = [
        PriceTextEntry(label="Base 2027", final_price_eur_mwh=1.0),
        PriceTextEntry(label="Peak 2027", final_price_eur_mwh=2.0),
        PriceTextEntry(label="Base 2028", final_price_eur_mwh=3.0),
    ]
    text = build_chat_text(entries)

    assert text.index("Base 2027") < text.index("Peak 2027") < text.index("Base 2028")


def test_mail_text_includes_signed_difference():
    entries = [
        PriceTextEntry(label="Base 2027", final_price_eur_mwh=85.40, difference_eur_mwh=0.60),
        PriceTextEntry(label="Peak 2027", final_price_eur_mwh=96.75, difference_eur_mwh=-1.25),
    ]
    text = build_mail_text(entries)

    assert "Base 2027: 85,40 €/MWh (Differenz zum Settlement Vortag: +0,60 €/MWh)" in text
    assert "Peak 2027: 96,75 €/MWh (Differenz zum Settlement Vortag: -1,25 €/MWh)" in text


def test_mail_text_handles_missing_difference():
    entries = [PriceTextEntry(label="Base 2027", final_price_eur_mwh=85.40, difference_eur_mwh=None)]
    text = build_mail_text(entries)

    assert "kein Settlement-Vergleich verfügbar" in text
