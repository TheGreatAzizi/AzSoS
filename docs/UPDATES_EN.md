# Software Updates

AZSOS Desktop checks software updates from:

```text
https://github.com/TheGreatAzizi/AzSoS/tree/UPDATE
```

Recommended UPDATE branch layout:

```text
UPDATE/
  update.index.json
  AZSOS-v0.3.4-windows.zip
```

AZSOS looks for:

- `update.index.json`
- `.exe`
- `.msi`
- `.zip`
- GitHub Releases as a fallback

Downloaded update files are saved to:

```text
~/AZSOS/updates/
```

AZSOS does not run downloaded installers automatically. The user must run the installer or open the archive manually.
