$ErrorActionPreference = "Stop"

if (-not (Test-Path ".venv")) {
  py -m venv .venv
}

. .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements-dev.txt

if (Test-Path "dist-exe") {
  Remove-Item -Recurse -Force "dist-exe"
}

pyinstaller --noconsole --onefile --name AZSOS --distpath dist-exe run_app.py
Write-Host "Built dist-exe/AZSOS.exe"
