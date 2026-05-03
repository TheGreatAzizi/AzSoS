# Software updates

> Language: **English** | [فارسی](../fa/UPDATES.md)


## Default update source

```text
https://github.com/TheGreatAzizi/AzSoS/tree/UPDATE
```

## Update branch layout

Recommended layout:

```text
update.index.json
AZSOS-0.3.6-windows.exe
AZSOS-0.3.6-windows.zip
```

## update.index.json

Example:

```json
{
  "format": "azsos.update.v1",
  "version": "0.3.6",
  "files": [
    {
      "name": "AZSOS-0.3.6-windows.exe",
      "url": "AZSOS-0.3.6-windows.exe",
      "sha256": "..."
    }
  ]
}
```

## App behavior

The app downloads update files to:

```text
~/AZSOS/updates/
```

It does not auto-run downloaded installers. The user chooses when to run them.
