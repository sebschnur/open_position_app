"""Ermittelt den aktuellen Benutzernamen fuer die Nachvollziehbarkeit.

Grundsatz: Bei jedem manuellen Eintrag und jeder per Button ausgeloesten
Aktion wird der aktuelle Benutzername in der Spalte ``last_modified_by``
gespeichert. So ist jederzeit nachvollziehbar, wer einen Eintrag zuletzt
geaendert hat. Der Name wird automatisch aus dem angemeldeten
Betriebssystem-Benutzer ermittelt (kein separates Login im Prototyp).
"""

import getpass

# Fallback, falls der Betriebssystem-Benutzer nicht ermittelbar ist.
SYSTEM_USERNAME = "system"


def get_current_username() -> str:
    """Liefert den aktuellen Betriebssystem-Benutzernamen (Fallback: 'system')."""
    try:
        username = getpass.getuser()
    except Exception:
        return SYSTEM_USERNAME
    username = (username or "").strip()
    return username or SYSTEM_USERNAME
