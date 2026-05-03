# Release checklist

> Language: **English** | [فارسی](../fa/RELEASE.md)


## Before releasing

- Update `azsos_core.__version__`.
- Update `pyproject.toml`.
- Update `CHANGELOG.md`.
- Run tests.
- Verify the sample package.
- Build the Windows executable.
- Upload release files to the UPDATE branch or GitHub Releases.

## Test commands

```powershell
pytest
python azsos.py verify sample-packages/first-aid-demo.azsos
python run_app.py
```

## After releasing

- Check that **Check updates** finds the new version.
- Check that **Fetch selected** finds packages from `IR-packages`.
- Keep old release files if users may need rollback.
