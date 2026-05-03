# AZSOS

> Language: **English** | [فارسی](README_FA.md)

AZSOS is an offline-first emergency content cache for Windows. It stores, verifies, searches, updates, exports, and locally shares trusted `.azsos` packages without depending on a central server.

## Default sources

Package source:

```text
https://github.com/TheGreatAzizi/AzSoS/tree/IR-packages
```

Software update source:

```text
https://github.com/TheGreatAzizi/AzSoS/tree/UPDATE
```

## What AZSOS can do

- Import and verify `.azsos` packages.
- Search installed content offline with SQLite FTS5.
- Open packaged HTML content locally in the system browser.
- Fetch content from GitHub branches, GitHub Releases, direct `.azsos` links, local folders, or registry JSON files.
- Let users add, save, and remove content sources inside the app.
- Install multiple remote packages after verification.
- Inspect a package before installing it.
- Delete installed packages.
- Export installed packages back to `.azsos` files.
- Share installed packages over local Wi-Fi, hotspot, or LAN.
- Show QR codes for local sharing.
- Let users mark publisher fingerprints as trusted on their own device.
- Check software updates from the UPDATE branch.
- Provide an English Markdown-style Docs tab inside the desktop app.

## Documentation

- [English documentation index](docs/en/README.md)
- [Persian documentation index](docs/fa/README.md)
- [User guide](docs/en/USER_GUIDE.md)
- [Package publishing guide](docs/en/PUBLISHING_PACKAGES.md)
- [GitHub publishing guide](docs/en/GITHUB_PUBLISHING.md)
- [Update publishing guide](docs/en/UPDATES.md)
- [Format specification](docs/en/FORMAT.md)
- [Security model](docs/en/SECURITY.md)

## Social and project links

- X: https://x.com/the_azzi
- GitHub: https://github.com/TheGreatAzizi
- Self-hosted Git: https://git.theazizi.ir/TheAzizi
- Telegram: https://t.me/luluch_code

## Development setup

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run_app.py
```

## Build a Windows executable

```powershell
pip install -r requirements-dev.txt
pyinstaller --noconsole --onefile --name AZSOS run_app.py
```

Or use:

```powershell
.\scriptsuild_windows.ps1
```

## CLI examples

```powershell
python azsos.py verify sample-packages/first-aid-demo.azsos
python azsos.py install sample-packages/first-aid-demo.azsos
python azsos.py search help
python azsos.py catalog fetch "https://github.com/TheGreatAzizi/AzSoS/tree/IR-packages"
```

Build a registry JSON for publishing:

```powershell
python azsos.py registry build `
  --packages-dir .\packages `
  --base-url https://raw.githubusercontent.com/TheGreatAzizi/AzSoS/IR-packages/packages `
  --out packages.index.json `
  --source-name azsos-ir-packages
```

## Trust model

Discovery is not trust. AZSOS installs a package only after checking the package structure, `hashes.json`, SHA-256 hashes, Ed25519 signature, and optional registry SHA-256. A user can also mark a publisher fingerprint as trusted locally after checking it through a trusted channel.

## Package format

`.azsos` files are ZIP packages using the `azsos.v1` format:

```text
package.azsos
  manifest.json
  hashes.json
  signature.ed25519
  search.sqlite
  content/
```

See [Format specification](docs/en/FORMAT.md).

## License

MIT
