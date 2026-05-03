# Package Authoring Guide

## 1. Prepare content

Create a folder with Markdown or HTML files:

```text
my-pack/
  index.md
  burns.md
  bleeding.md
```

AZSOS converts Markdown files to sanitized HTML during packing.

## 2. Generate a publisher key

```powershell
python azsos.py keygen --out-dir keys
```

Do not commit `keys/publisher_private.pem`.

## 3. Pack

```powershell
python azsos.py pack `
  --content my-pack `
  --id my-pack.fa `
  --title "My AZSOS Pack" `
  --version 0.1.0 `
  --publisher-name "My Publisher" `
  --key keys/publisher_private.pem `
  --out build/packages/my-pack.azsos
```

## 4. Verify

```powershell
python azsos.py verify build/packages/my-pack.azsos
```

## 5. Test import and search

```powershell
python azsos.py install build/packages/my-pack.azsos
python azsos.py search burns
```
