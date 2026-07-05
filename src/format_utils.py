"""Deutsche Zahlenformatierung fuer die UI-Anzeige.

Python und Streamlit nutzen standardmaessig das englische Zahlenformat
(z. B. 1,234.56). In der Oberflaeche soll aber durchgaengig das deutsche
Format verwendet werden: Punkt als Tausendertrennzeichen und Komma als
Dezimaltrennzeichen (z. B. 1.234,56).

Bewusst ohne das `locale`-Modul, das unter Windows (cp1252) fehleranfaellig
ist. Fuer pandas-Tabellen wird stattdessen `Styler.format(thousands=".",
decimal=",")` genutzt, fuer einzelne Werte diese Helferfunktion.
"""

from typing import Optional


def format_de(value: Optional[float], decimals: int = 2) -> str:
    """Formatiert eine Zahl im deutschen Format, z. B. 1.234,56.

    Gibt "-" zurueck, wenn ``value`` None ist (praktisch fuer optionale
    Werte wie einen noch nicht vorhandenen Marktpreis).
    """
    if value is None:
        return "-"
    # Zuerst englisches Format erzeugen (',' = Tausender, '.' = Dezimal),
    # danach die Trennzeichen ueber einen Platzhalter tauschen.
    formatted = f"{value:,.{decimals}f}"
    return formatted.replace(",", "\x00").replace(".", ",").replace("\x00", ".")
