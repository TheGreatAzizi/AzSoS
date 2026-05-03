# In-app manual

> Language: **English** | [فارسی](../fa/IN_APP_MANUAL.md)


This is the GitHub copy of the English in-app manual. The Docs tab inside AZSOS Desktop uses the English version.

## Quick start

### The 60-second flow

1. **Open `Get content`.**
2. Click **Fetch selected** to scan the default AZSOS package source.
3. Select one or more packages and click **Install selected**.
4. Open **Installed**, choose a package, then click **Open package**.
5. Use **Search selected** or **Search all** to find text offline.
6. To share without internet, open **Share** and click **Start**.

> [!TIP]
> If somebody gives you a `.azsos` file on USB, Telegram, LAN, or Bluetooth, you do not need the internet. Use **Installed → Import .azsos**.

### What you get after installation

- A local copy of the content under `~/AZSOS/library/`
- Offline search when the package includes `search.sqlite`
- Verification status, publisher information, and package metadata
- Export and local sharing options

## What AZSOS does

### One sentence

**AZSOS is an offline-first emergency content cache for trusted `.azsos` packages.**

It helps users download important content while the internet works, keep it locally, verify it, search it, and share it on a local network when the internet is unavailable or unreliable.

### AZSOS is useful for

- First-aid and emergency guides
- Digital safety guides
- Family preparedness checklists
- Offline business continuity kits
- Local contact lists and maps
- Curated education packs
- Any small, source-aware content that should survive outages

### AZSOS is not

- A VPN
- A messenger
- A browser replacement
- A central cloud service

> [!NOTE]
> The main design rule is simple: **download once, verify once, use and share offline many times.**

## What a .azsos file is

### Package format

A `.azsos` file is a controlled ZIP-based package with a strict internal structure.

```text
first-aid.azsos
  manifest.json
  hashes.json
  signature.ed25519
  search.sqlite
  content/
    index.html
    pages/
    assets/
```

### Important files

- **`manifest.json`** — package title, version, language, publisher, entry page, and format version.
- **`hashes.json`** — SHA-256 hashes for package files.
- **`signature.ed25519`** — publisher signature over the manifest and hashes.
- **`search.sqlite`** — optional offline search index.
- **`content/`** — the files the user reads.

> [!WARNING]
> AZSOS rejects unsafe ZIP paths such as `../evil.txt`. A package must not be able to overwrite files outside the AZSOS library.

## Installed tab

### Purpose

The **Installed** tab manages packages that are already on this computer.

### Main actions

- **Import .azsos** — choose a local `.azsos` file, verify it, and install it.
- **Verify file** — check a package without installing it.
- **Open package** — open the selected package's entry page in the default browser.
- **Export selected** — export an installed package back to a `.azsos` file.
- **Delete package** — remove the selected package from the AZSOS library.
- **Trust publisher** — mark the selected publisher fingerprint as trusted on this device.
- **Refresh** — reload the installed package list.
- **Open library folder** — open `~/AZSOS/library/`.

> [!IMPORTANT]
> **Delete package** removes the installed copy from AZSOS. It does not delete the original file you imported from another folder.

## Offline search

### How search works

AZSOS searches the local package index. No server is contacted.

### Buttons

- **Search selected** — search only inside the selected package.
- **Search all** — search across all installed packages.
- **Open result** — open the selected result.

### Search tips

- Start with short keywords: `water`, `burn`, `help`, `تماس`.
- For Persian content, try both normal spaces and half-spaces when needed.
- If there are no results, the package may not include `search.sqlite`.

> [!TIP]
> Package authors should build a search index during packing. Search quality depends on the package, not only the app.

## Get content tab

### Default source

AZSOS ships with this default content source:

```text
https://github.com/TheGreatAzizi/AzSoS/tree/IR-packages
```

### What the tab does

The **Get content** tab discovers packages from GitHub branches, releases, direct URLs, local folders, and registry files.

### Common flow

1. Keep the default source or add a new one.
2. Click **Fetch selected**.
3. Select one or more remote packages.
4. Optional: click **Inspect selected**.
5. Click **Install selected**.

### Buttons

- **Fetch selected** — scan only the selected source.
- **Fetch all** — scan every saved source.
- **Open source** — open the current source URL or folder.
- **Reset default** — restore the default AZSOS IR package source.
- **Save current** — save edits to the selected source.
- **Add as new** — save the current name and URL as a new source.
- **Remove** — remove the selected source.
- **Install selected** — download, verify, and install selected packages.
- **Inspect selected** — preview manifest, publisher, fingerprint, and SHA-256.
- **Copy download URL** — copy the package URL.

> [!TIP]
> Prefer a `packages.index.json` registry for public sources. It is faster and avoids GitHub rate limits.

## Content sources and registries

### Supported source types

AZSOS can fetch packages from:

- **GitHub branch/tree**
- **GitHub Releases**
- **Direct `.azsos` URL**
- **Local folder**
- **`packages.index.json` registry**

### Recommended registry layout

```text
IR-packages/
  packages.index.json
  packages/
    first-aid.azsos
    digital-safety.azsos
    offline-business-kit.azsos
```

### Minimal `packages.index.json`

```json
{
  "format": "azsos.registry.v1",
  "source_name": "azsos-ir-packages",
  "packages": [
    {
      "name": "first-aid.azsos",
      "title": "First Aid",
      "version": "0.1.0",
      "download_url": "https://raw.githubusercontent.com/TheGreatAzizi/AzSoS/IR-packages/packages/first-aid.azsos",
      "sha256": "..."
    }
  ]
}
```

> [!NOTE]
> The registry helps users discover files. Trust still comes from package verification, signatures, hashes, and publisher fingerprints.

## Getting content before and during outages

### Before an outage

- Fetch packages from the default AZSOS source.
- Install useful packs in advance.
- Export important packs to USB or external drives.
- Keep a trusted publisher fingerprint list.

### During weak connectivity

- Try **Fetch selected** once.
- If GitHub is slow or rate-limited, use a direct `.azsos` link or a registry mirror.
- Ask someone who already has the package to use **Share**.

### During a full outage

- Use **Share** over Wi-Fi, hotspot, or LAN.
- Use **Export selected** and move files with USB, external drives, Bluetooth, or cables.
- Import local files using **Installed → Import .azsos**.

> [!IMPORTANT]
> AZSOS is designed for graceful degradation: internet source → mirror → local network → physical file transfer.

## Share tab

### What Share does

The **Share** tab runs a small local HTTP server so other devices on the same network can download your installed packages.

### Flow

1. Connect this computer to Wi-Fi, hotspot, or LAN.
2. Open **Share**.
3. Click **Start**.
4. Copy the shown URL or display the QR code.
5. Other devices open the URL in a browser.
6. They download `.azsos` files and verify them locally.

### Endpoints

```text
/              simple web page
/packages.json package list
/packages/...  package download
/health        connectivity test
```

> [!WARNING]
> Click **Stop** when you are done, especially on public or shared networks.

## Creating .azsos packages with the CLI

### Create a publisher key

```powershell
python azsos.py keygen --out-dir keys
```

### Build a package

```powershell
python azsos.py pack ^
  --content examples/first-aid/content ^
  --id first-aid.fa ^
  --title "First Aid" ^
  --version 0.1.0 ^
  --publisher-name "AZSOS Publisher" ^
  --key keys/publisher_private.pem ^
  --out dist/first-aid.azsos
```

### Verify and install

```powershell
python azsos.py verify dist/first-aid.azsos
python azsos.py install dist/first-aid.azsos
python azsos.py search water
python azsos.py serve
```

> [!WARNING]
> Never commit your publisher private key to a public repository. Publish only the public key or fingerprint.

## Building packages.index.json

### Why registries matter

A registry makes discovery faster, clearer, and more reliable.

### Build a registry

```powershell
python azsos.py registry build ^
  --packages-dir ./packages ^
  --base-url https://raw.githubusercontent.com/TheGreatAzizi/AzSoS/IR-packages/packages ^
  --out packages.index.json ^
  --source-name azsos-ir-packages
```

### Publish to GitHub

```text
https://github.com/TheGreatAzizi/AzSoS/tree/IR-packages
```

### Benefits

- Faster fetch
- Less GitHub API usage
- Lower chance of `HTTP Error 403: rate limit exceeded`
- Prelisted SHA-256 hashes
- Cleaner titles, versions, and publisher metadata

## Software updates

### Update source

The **Check updates** button checks:

```text
https://github.com/TheGreatAzizi/AzSoS/tree/UPDATE
```

### Supported update files

- `update.index.json`
- `.exe`
- `.msi`
- `.zip`
- GitHub Releases as a fallback

### Behavior

1. AZSOS finds update candidates.
2. The user selects one.
3. The file is downloaded to `~/AZSOS/updates/`.
4. AZSOS does **not** run installers automatically.

> [!IMPORTANT]
> Manual execution is intentional. Silently running downloaded installers is not safe.

## Security and trust

### Verification layers

AZSOS checks multiple layers before installation:

1. **ZIP safety** — rejects dangerous paths such as `../evil.txt`.
2. **Hashes** — verifies files against `hashes.json`.
3. **Signature** — verifies the Ed25519 signature.
4. **Fingerprint** — identifies publishers by public-key fingerprint.
5. **Local trust** — lets users mark known fingerprints as trusted.

### Status meanings

- **Valid package** — structure, hashes, and signature are correct.
- **Unknown publisher** — package is valid, but the fingerprint is not trusted on this device.
- **Trusted publisher** — fingerprint was previously trusted by the user.
- **Invalid package** — file is broken, incomplete, tampered with, or unsafe.

> [!WARNING]
> Trust a publisher only after checking the fingerprint through an official website, official channel, trusted contact, or in-person verification.

## Common errors

### No `.azsos` packages found

The selected source did not contain discoverable packages. Check the branch, file paths, and `packages.index.json`.

### `HTTP Error 403: rate limit exceeded`

GitHub limited unauthenticated requests.

Best fixes:

- Publish `packages.index.json`.
- Use a raw registry URL.
- Set a GitHub token temporarily.

```powershell
$env:AZSOS_GITHUB_TOKEN="ghp_xxx"
python run_app.py
```

### `Not found / 404`

The repository, branch, path, or filename is wrong.

### Invalid package

The package is incomplete, corrupted, tampered with, or incompatible with the current AZSOS format.

### Local Share does not open

Devices must be on the same network. Windows Firewall may ask you to allow Python or AZSOS.

## Important folders

### User data

AZSOS stores local data under the user's home folder.

```text
~/AZSOS/library/    installed packages
~/AZSOS/config.json settings and content sources
~/AZSOS/updates/    downloaded software updates
```

### Reset local installation

1. Export any important packages first.
2. Close AZSOS.
3. Delete `~/AZSOS`.
4. Start AZSOS again.

> [!CAUTION]
> Deleting `~/AZSOS` removes installed packages, trusted publishers, saved sources, and downloaded updates.

## Publisher checklist

### Content quality

Good packages are small, clear, source-aware, and easy to verify.

- Keep text readable offline.
- Compress images.
- Cite sources inside the content.
- Add review dates for emergency or medical information.
- Use stable package IDs, for example `first-aid.fa.basic`.
- Protect the publisher private key.
- Publish the fingerprint on official channels.
- Generate `packages.index.json`.

### Pre-release checklist

- [ ] `.azsos` file was created
- [ ] `verify` succeeds
- [ ] `install` succeeds
- [ ] Search works
- [ ] **Open package** opens the correct page
- [ ] Content includes sources and review dates where needed
- [ ] Registry was generated
- [ ] Raw download links are correct

## Useful CLI commands

```powershell
python azsos.py --help
python azsos.py keygen --out-dir keys
python azsos.py verify my-pack.azsos
python azsos.py install my-pack.azsos
python azsos.py delete <package-id-or-installed-path>
python azsos.py search help
python azsos.py catalog fetch
python azsos.py catalog inspect <url-or-index>
python azsos.py catalog install <url-or-index>
python azsos.py registry build --packages-dir ./packages --base-url <raw-base-url> --out packages.index.json
```

> [!TIP]
> Use the GUI for normal users and the CLI for publishers, testing, automation, and registry generation.

## Project links

### Main links

- **Main repository:** https://github.com/TheGreatAzizi/AzSoS
- **Content packages branch:** https://github.com/TheGreatAzizi/AzSoS/tree/IR-packages
- **Software update branch:** https://github.com/TheGreatAzizi/AzSoS/tree/UPDATE

### Author and community

- **X / Twitter:** https://x.com/the_azzi
- **GitHub profile:** https://github.com/TheGreatAzizi
- **Self-hosted Git:** https://git.theazizi.ir/TheAzizi
- **Telegram:** https://t.me/luluch_code
