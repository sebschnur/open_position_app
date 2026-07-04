"""Text-Generierung fuer Chat- und Mailtext (Preise-Seite).

Vorgabe: docs/specifications/01_fachliche_funktionen.md (Abschnitt 10),
03_streamlit_ui_konzept.md (Abschnitt 5.5/5.6). Reine Funktionen, kein
echter Mailversand - nur kopierbarer Text, neutrale Formulierung.
"""

from dataclasses import dataclass
from typing import List, Optional

CHAT_HEADER = "Aktuelle Indikationen Vertrieb:"
MAIL_HEADER = "Aktuelle Preisindikationen für den Vertrieb:"


@dataclass
class PriceTextEntry:
    label: str
    final_price_eur_mwh: float
    difference_eur_mwh: Optional[float] = None


def _format_eur_mwh(value: float) -> str:
    """Deutsches Zahlenformat mit Komma, z. B. 84,25 €/MWh."""
    return f"{value:.2f}".replace(".", ",") + " €/MWh"


def _format_signed_eur_mwh(value: float) -> str:
    sign = "+" if value >= 0 else ""
    return f"{sign}{_format_eur_mwh(value)}"


def build_chat_text(entries: List[PriceTextEntry]) -> str:
    """Chat-Kurztext: nur finale Preise, keine Settlement-Differenz."""
    lines = [CHAT_HEADER, ""]
    for entry in entries:
        lines.append(f"{entry.label}: {_format_eur_mwh(entry.final_price_eur_mwh)}")
    return "\n".join(lines)


def build_mail_text(entries: List[PriceTextEntry]) -> str:
    """Mailtext: finale Preise plus Differenz zum Settlement des Vortages."""
    lines = [MAIL_HEADER, ""]
    for entry in entries:
        line = f"{entry.label}: {_format_eur_mwh(entry.final_price_eur_mwh)}"
        if entry.difference_eur_mwh is not None:
            line += f" (Differenz zum Settlement Vortag: {_format_signed_eur_mwh(entry.difference_eur_mwh)})"
        else:
            line += " (kein Settlement-Vergleich verfügbar)"
        lines.append(line)
    return "\n".join(lines)
