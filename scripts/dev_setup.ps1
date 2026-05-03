$ErrorActionPreference = "Stop"
py -m venv .venv
. .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
Write-Host "Development environment ready. Run: pytest"
