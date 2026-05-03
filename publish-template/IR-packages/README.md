# AZSOS IR packages branch template

Upload the contents of this folder to the `IR-packages` branch:

```text
packages.index.json
packages/*.azsos
```

AZSOS Desktop 0.3.3 checks `packages.index.json` first, so users can fetch packages without hitting the GitHub API rate limit.

To rebuild the registry after adding new packages:

```powershell
python azsos.py registry build `
  --packages-dir .\packages `
  --base-url https://raw.githubusercontent.com/TheGreatAzizi/AzSoS/IR-packages/packages `
  --out packages.index.json `
  --source-name azsos-ir-packages
```
