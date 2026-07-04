"""Service: PFC-Dateiimport.

Vorgabe: 06_excel_mockdaten_import.md, Abschnitt 8.2. Liest Dateien mit Muster
YYYYMMDD_EEX_PFC_YYYY.xlsx aus einem Verzeichnis, PFC-Mittelwert aus Zelle
D2, Generierungsdatum und Lieferjahr aus dem Dateinamen.

Die PFC-Pruefung bezieht sich im Prototyp nur auf Base Y+1 bis Y+3. Fehlt
eine Datei, entspricht der Dateiname nicht dem Muster oder ist D2 nicht
numerisch, wird ein Default-Mockwert verwendet und im Rueckgabewert
`warnings` klar als Default gekennzeichnet (Abschnitt 8.4).
"""

import datetime as dt
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import openpyxl

from src.db.default_mock_values import BASE_PFC_MEAN

_FILENAME_PATTERN = re.compile(r"^(\d{8})_EEX_PFC_(\d{4})\.xlsx$", re.IGNORECASE)


@dataclass
class PfcCheckSeed:
    product_type: str
    delivery_year: int
    pfc_mean_eur_mwh: float
    pfc_file_timestamp: dt.datetime
    is_default: bool


def read_pfc_checks_from_files(
    pfc_dir: Path, current_year: int, today: Optional[dt.date] = None
) -> Tuple[List[PfcCheckSeed], List[str]]:
    """Liest PFC-Mittelwerte fuer Base Y+1 bis Y+3 aus dem PFC-Verzeichnis.

    Gibt (seeds, warnings) zurueck. Fehlende/ungueltige Werte werden durch
    Default-Mockdaten aus `default_mock_values.BASE_PFC_MEAN` ersetzt.
    """
    today = today or dt.date.today()
    warnings: List[str] = []
    found_by_year: Dict[int, Tuple[float, dt.datetime]] = {}
    dir_exists = pfc_dir.is_dir()

    if dir_exists:
        for path in sorted(pfc_dir.glob("*.xlsx")):
            match = _FILENAME_PATTERN.match(path.name)
            if not match:
                warnings.append(
                    f"PFC-Datei '{path.name}' entspricht nicht dem Muster "
                    "YYYYMMDD_EEX_PFC_YYYY.xlsx und wird ignoriert."
                )
                continue

            date_str, year_str = match.groups()
            try:
                file_date = dt.datetime.strptime(date_str, "%Y%m%d")
            except ValueError:
                warnings.append(
                    f"PFC-Datei '{path.name}' hat ein ungueltiges Datum im "
                    "Dateinamen und wird ignoriert."
                )
                continue

            mean_value = _read_d2(path)
            if mean_value is None:
                warnings.append(
                    f"PFC-Datei '{path.name}': Zelle D2 ist leer oder nicht "
                    "numerisch und wird ignoriert."
                )
                continue

            found_by_year[int(year_str)] = (mean_value, file_date)
    else:
        warnings.append(
            f"PFC-Verzeichnis '{pfc_dir}' nicht gefunden - Default-Mockwerte werden verwendet."
        )

    seeds: List[PfcCheckSeed] = []
    for offset in (1, 2, 3):
        year = current_year + offset
        if year in found_by_year:
            mean_value, file_date = found_by_year[year]
            seeds.append(
                PfcCheckSeed(
                    product_type="Base",
                    delivery_year=year,
                    pfc_mean_eur_mwh=mean_value,
                    pfc_file_timestamp=file_date,
                    is_default=False,
                )
            )
        else:
            if dir_exists:
                warnings.append(
                    f"Keine gueltige PFC-Datei fuer Lieferjahr {year} (Y+{offset}) "
                    "gefunden - Default-Mockwert wird verwendet."
                )
            seeds.append(
                PfcCheckSeed(
                    product_type="Base",
                    delivery_year=year,
                    pfc_mean_eur_mwh=BASE_PFC_MEAN[offset],
                    pfc_file_timestamp=dt.datetime.combine(today, dt.time.min),
                    is_default=True,
                )
            )
    return seeds, warnings


def _read_d2(path: Path) -> Optional[float]:
    try:
        workbook = openpyxl.load_workbook(path, data_only=True, read_only=True)
        try:
            value = workbook.active["D2"].value
        finally:
            workbook.close()
    except Exception:
        return None
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    return None
