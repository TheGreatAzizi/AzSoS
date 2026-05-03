# Publishing packages

> Language: **English** | [فارسی](../fa/PUBLISHING_PACKAGES.md)


## Recommended publishing layout

Create a branch named `IR-packages` and use this layout:

```text
packages.index.json
packages/
  first-aid.azsos
  digital-safety.azsos
```

## Build packages

Generate a publisher key once and keep the private key safe:

```powershell
python azsos.py keygen --out-dir keys
```

Pack content:

```powershell
python azsos.py pack `
  --content .\content `
  --id first-aid.fa.basic `
  --title "First Aid Basic" `
  --version 0.1.0 `
  --publisher-name "AZSOS Publisher" `
  --key keys\publisher_private.pem `
  --out packagesirst-aid.azsos
```

Verify before publishing:

```powershell
python azsos.py verify packagesirst-aid.azsos
```

## Build the registry

```powershell
python azsos.py registry build `
  --packages-dir .\packages `
  --base-url https://raw.githubusercontent.com/TheGreatAzizi/AzSoS/IR-packages/packages `
  --out packages.index.json `
  --source-name azsos-ir-packages
```

## Publish

Commit the registry and packages to the `IR-packages` branch. Users can fetch from:

```text
https://github.com/TheGreatAzizi/AzSoS/tree/IR-packages
```

## Good package practice

- Keep packages small and focused.
- Use clear titles and versions.
- Include source attribution in the content.
- Review emergency or medical content carefully before publishing.
- Never publish the private signing key.
