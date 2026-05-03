# AZSOS content discovery

AZSOS Desktop can fetch `.azsos` packages from multiple content sources.

Default source:

```text
https://github.com/TheGreatAzizi/AzSoS/tree/IR-packages
```

Supported sources:

1. GitHub branch/tree URL
2. GitHub repository URL, using Release assets
3. Direct `.azsos` download URL
4. Local folder containing `.azsos` files
5. `packages.index.json` registry URL or local file

Examples:

```text
https://github.com/TheGreatAzizi/AzSoS/tree/IR-packages
https://github.com/TheGreatAzizi/AzSoS/releases
https://example.com/first-aid.azsos
C:\Users\you\AZSOS\packs
https://example.com/packages.index.json
```

## Recommended public publishing flow

For a simple release, upload `.azsos` files to the `IR-packages` branch or to GitHub Releases.

For a better catalog, publish a registry JSON:

```powershell
python azsos.py registry build `
  --packages-dir .\packages `
  --base-url https://raw.githubusercontent.com/TheGreatAzizi/AzSoS/IR-packages `
  --out packages.index.json `
  --source-name azsos-ir-packages
```

Then users can paste the `packages.index.json` URL into AZSOS Desktop and fetch packages with metadata, sizes, fingerprints, and SHA-256 checksums.

## Trust model

Discovery is not trust. A package is installed only after AZSOS verifies:

- `.azsos` structure
- hashes in `hashes.json`
- Ed25519 signature
- optional registry SHA-256

Users can mark a publisher fingerprint as trusted on their own device after verifying it through a trusted channel.

## GitHub rate-limit resistant discovery

AZSOS 0.3.3 tries discovery in this order for GitHub tree sources:

1. `packages.index.json` from the branch, using `raw.githubusercontent.com`
2. GitHub HTML tree scanning, without the GitHub API
3. GitHub API tree scan, only as a fallback
4. GitHub Releases, best-effort only

For public publishing, prefer a `packages.index.json` file in the branch root. This avoids GitHub API rate limits and gives users better metadata. If you still need API-based discovery, set `AZSOS_GITHUB_TOKEN` or `GITHUB_TOKEN` before running the app.
