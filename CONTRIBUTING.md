# Contributing to AZSOS

Thank you for helping improve AZSOS.

## Good first contributions

- Improve package authoring docs
- Add tests for `.azsos` verification edge cases
- Improve Persian text normalization
- Improve Windows packaging scripts
- Add sample emergency content packages
- Improve UI wording and accessibility

## Development setup

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
pytest
python run_app.py
```

## Pull request checklist

- Keep the app usable offline.
- Do not add telemetry or network calls without an explicit opt-in design.
- Do not commit private signing keys.
- Add or update tests for package-format changes.
- Update docs when CLI behavior or format behavior changes.

## Security-sensitive changes

Changes to verification, extraction, signatures, or package rendering should be reviewed carefully. Prefer small pull requests with tests.
