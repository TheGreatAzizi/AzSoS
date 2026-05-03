# Content sources and distribution

AZSOS packages are normal files with the `.azsos` extension. Users can get them through the built-in content source fetcher, GitHub Releases, a mirror, USB drive, LAN share, hotspot, Telegram, email, or another AZSOS device running Local share.

Default built-in source:

```text
https://github.com/TheGreatAzizi/AzSoS/tree/IR-packages
```

## Recommended first release model

Use a simple, boring distribution model first:

1. Maintainers publish curated `.azsos` files in the `IR-packages` branch and/or as GitHub Release assets.
2. Users open AZSOS Desktop and click **Fetch** in the **Content source / online catalog** panel.
3. Users select a package and click **Install selected**. AZSOS downloads and verifies it before installation.
4. The release page or package description should include each package name, version, SHA-256 checksum, publisher fingerprint, language, and short description.
5. During an outage, a user with the package starts Local share; nearby users download the same `.azsos` file from the LAN/hotspot page.

This avoids a central server requirement and keeps the MVP easy to audit.

## Package registry for later

A future app can read a signed registry file named `packages.index.json`. Keep the registry separate from package verification: the registry helps users discover packages, but each `.azsos` file still verifies itself with hashes and Ed25519 signature.

Example:

```json
{
  "format": "azsos.index.v1",
  "updated_at": "2026-05-03T00:00:00Z",
  "packages": [
    {
      "id": "first-aid.fa.demo",
      "title": "First Aid Demo",
      "version": "0.1.0",
      "language": "fa",
      "download_url": "https://github.com/TheGreatAzizi/AzSoS/releases/download/v0.2.0/first-aid-demo.azsos",
      "sha256": "replace-with-release-checksum",
      "publisher_name": "AZSOS Demo Publisher",
      "publisher_fingerprint": "replace-with-fingerprint",
      "size_bytes": 0,
      "tags": ["first-aid", "offline", "demo"]
    }
  ]
}
```

## Where content should come from

AZSOS should not scrape random medical or legal advice. Prefer:

- Public-domain or openly licensed emergency-preparedness material.
- Content written by known local publishers who sign their packages.
- Official source documents that allow redistribution, with attribution preserved.
- User-created personal/local lists, such as emergency contacts, addresses, and checklists.
- Offline datasets with clear license terms, such as OpenStreetMap-based local POI lists with attribution.

For medical, legal, and safety content, keep source names, review dates, disclaimers, and version history inside each package.

## Trust rules

- A valid package signature proves the package was signed by the embedded publisher key.
- A valid signature does not prove the publisher is trustworthy.
- Show the fingerprint to users and let them compare it with a fingerprint published on a known channel.
- Do not silently update packages from a registry until AZSOS has a persistent trust store.

## Offline distribution flows

### Flow A: In-app fetch

1. User opens AZSOS Desktop.
2. User keeps the default source or pastes another GitHub/registry URL.
3. User clicks **Fetch**.
4. User selects a remote `.azsos` package and clicks **Install selected**.
5. AZSOS downloads and verifies the package.

### Flow B: Direct download

1. User opens the release page.
2. User downloads `something.azsos`.
3. User clicks **Import .azsos** in AZSOS.
4. AZSOS verifies the package.

### Flow C: Local share

1. Device A imports a trusted package.
2. Device A clicks **Start** in Local share.
3. Device B connects to the same Wi-Fi/hotspot and opens the AZSOS URL or scans the QR.
4. Device B downloads the `.azsos` file and imports it.

### Flow D: Sneakernet

1. Copy `.azsos` files to USB, memory card, or phone storage.
2. Move the file to the offline machine.
3. Import and verify in AZSOS.

### Flow E: Build your own

```powershell
python azsos.py keygen --out-dir keys
python azsos.py pack --content my-content --id my-pack.fa --title "My Pack" --version 0.1.0 --publisher-name "My Publisher" --key keys/publisher_private.pem --out my-pack.azsos
python azsos.py verify my-pack.azsos
```
