"""Geteilte plausible Default-Mockwerte.

Diese Werte werden an zwei Stellen gebraucht:
- `seed_default_mock_data.py` fuer eine komplett leere Datenbank ohne Excel.
- `excel_import_service.py` / `pfc_import_service.py` als Fallback, wenn
  einzelne Excel-/PFC-Werte fehlen (siehe 06_excel_mockdaten_import.md,
  Abschnitt 8.4: "Default-Mockdaten sind erlaubt, aber sie muessen im
  Importprotokoll klar als Default gekennzeichnet werden").

Schluessel sind Jahres-Offsets (1 = Y+1 usw.), analog zu PRICE_PRODUCT_ORDER_TABLE.
"""

BASE_MARKET_PRICE = {1: 85.00, 2: 79.50, 3: 76.20}
PEAK_MARKET_PRICE = {1: 95.50, 2: 89.30, 3: 85.00}
BASE_OTC_SURCHARGE = {1: 0.40, 2: 0.50, 3: 0.60}
PEAK_OTC_SURCHARGE = {1: 0.65, 2: 0.75, 3: 0.85}
BASE_SETTLEMENT_PRICE = {1: 84.80, 2: 79.10, 3: 75.90}
PEAK_SETTLEMENT_PRICE = {1: 95.00, 2: 88.90, 3: 84.70}
BASE_PFC_MEAN = {1: 85.10, 2: 79.60, 3: 76.30}

# Y0 (aktuelles Jahr) bis Y+4: plausible Netto-Positionen in MWh.
PORTFOLIO_POSITION_BY_OFFSET = {0: 15000.0, 1: -8000.0, 2: 4000.0, 3: -2000.0, 4: 0.0}
