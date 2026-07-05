# Startet die Streamlit-App mit dem Python aus der lokalen .venv.
# Aufruf im Terminal:  .\start_app.ps1
# Beenden: Strg + C
# Beenden alternativ: Stop-Process -Id (Get-NetTCPConnection -LocalPort 8501 -State Listen).OwningProcess -Force

$ErrorActionPreference = "Stop"

# Ins Projektverzeichnis wechseln (dort, wo dieses Skript liegt)
Set-Location -Path $PSScriptRoot

$python = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    Write-Error "Kein Python in .venv gefunden ($python). Zuerst virtuelle Umgebung anlegen."
    exit 1
}

& $python -m streamlit run app.py
