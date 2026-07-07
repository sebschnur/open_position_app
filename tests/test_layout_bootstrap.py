"""Sichert die zentrale Layout-/CSS-Bootstrap-Architektur ab.

Layout (``st.set_page_config``) und globales CSS werden ausschliesslich in
``app.py`` ueber ``apply_global_layout()`` gesetzt und via ``st.navigation`` auf
alle Seiten angewandt. Eine einzelne Fachseite darf das NICHT selbst tun -
sonst koennte sie es (wie frueher) vergessen oder es gaebe einen doppelten
``set_page_config``-Aufruf. Diese Tests erzwingen die Invariante statisch, ohne
Streamlit-Runtime oder Datenbank.
"""

from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
VIEW_FILES = sorted((PROJECT_ROOT / "views").glob("*.py"))


def test_views_exist():
    assert {f.name for f in VIEW_FILES} == {
        "position.py",
        "preise.py",
        "limitorder.py",
        "handelskalender.py",
    }


def test_app_py_bootstraps_layout_and_navigation():
    app_src = (PROJECT_ROOT / "app.py").read_text(encoding="utf-8")
    assert "apply_global_layout()" in app_src
    assert "st.navigation(" in app_src


@pytest.mark.parametrize("view_file", VIEW_FILES, ids=lambda p: p.name)
def test_views_do_not_configure_layout_themselves(view_file: Path):
    src = view_file.read_text(encoding="utf-8")
    # Keine Seite setzt Layout/Page-Config selbst - das passiert zentral in app.py.
    assert "set_page_config" not in src
    assert "configure_wide_page" not in src
    assert "apply_global_layout" not in src
