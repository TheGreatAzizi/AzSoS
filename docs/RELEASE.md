# Release Guide

## Manual release checklist

1. Update `azsos_core/__init__.py` version.
2. Update `pyproject.toml` version.
3. Update `CHANGELOG.md`.
4. Run tests:

```powershell
pip install -r requirements-dev.txt
pytest
```

5. Build Windows executable:

```powershell
.\scripts\build_windows.ps1
```

6. Create a tag:

```bash
git tag v0.2.0
git push origin v0.2.0
```

The GitHub Actions workflow can build and upload a Windows artifact for tagged releases.
