# Publishing AZSOS Packages

## Recommended branch layout

Use the `IR-packages` branch for content packages:

```text
IR-packages/
  packages.index.json
  packages/
    first-aid.azsos
    digital-safety.azsos
```

## Build packages

```powershell
python azsos.py keygen --out-dir keys
python azsos.py pack --content ./content --id my.pack.fa --title "My Pack" --version 0.1.0 --publisher-name "My Publisher" --key keys/publisher_private.pem --out packages/my-pack.azsos
python azsos.py verify packages/my-pack.azsos
```

Keep the private key secret. Do not commit it.

## Build packages.index.json

```powershell
python azsos.py registry build `
  --packages-dir .\packages `
  --base-url https://raw.githubusercontent.com/TheGreatAzizi/AzSoS/IR-packages/packages `
  --out packages.index.json `
  --source-name azsos-ir-packages
```

## Publish

Push `packages.index.json` and the `packages/` folder to:

```text
https://github.com/TheGreatAzizi/AzSoS/tree/IR-packages
```

AZSOS Desktop can then fetch this source without relying heavily on the GitHub API.
