"""In-app English documentation for AZSOS Desktop."""
from __future__ import annotations

DOC_TOPICS: list[tuple[str, str]] = [
    (
        "Quick start",
        """
AZSOS is built to help people download important content before an outage, keep it on their computer, search it offline, and share it locally when the internet is unavailable or unreliable.

Fast path:

1. Open the Get content tab.
2. Click Fetch selected to scan the default AZSOS package source.
3. Select one or more remote packages and click Install selected.
4. Open the Installed tab and select an installed package.
5. Use Open package to read it, or Search selected / Search all to find text offline.
6. To share packages without internet, open the Share tab and click Start.

If you already have a .azsos file, use Installed -> Import .azsos. No internet connection is required for local imports.
""".strip(),
    ),
    (
        "What AZSOS does",
        """
AZSOS is an offline-first emergency content cache. It stores content in signed .azsos packages so users can verify, search, read, export, and share important information without depending on a central server.

Main goals:

- Download content while internet is available.
- Keep that content usable when internet access is cut off or unstable.
- Verify package integrity before installation.
- Search installed content locally.
- Share packages over Wi-Fi, hotspot, LAN, USB drives, Telegram, Git, or any other file-transfer path.
- Let publishers distribute curated, signed packages.

AZSOS is not a VPN and not a messenger. It is a trusted offline cache for knowledge and emergency content.
""".strip(),
    ),
    (
        "What a .azsos file is",
        """
A .azsos file is a controlled ZIP-based package with a strict internal structure.

Typical layout:

first-aid.azsos
  manifest.json
  hashes.json
  signature.ed25519
  search.sqlite
  content/
    index.html
    pages/
    assets/

Important files:

manifest.json
  Package metadata: title, version, language, publisher, start page, and format version.

hashes.json
  SHA-256 hashes for files inside the package. AZSOS uses this to detect corruption or tampering.

signature.ed25519
  The publisher's Ed25519 signature over the manifest and hashes.

search.sqlite
  Optional offline search index.

content/
  The actual content the user reads.

During installation, AZSOS rejects dangerous ZIP paths such as ../evil.txt so a package cannot overwrite files outside the AZSOS library.
""".strip(),
    ),
    (
        "Installed tab",
        """
The Installed tab manages packages that are already installed on this computer.

Buttons:

Import .azsos
  Select a local .azsos file. AZSOS verifies and installs it.

Verify file
  Check whether a file is valid without installing it.

Open package
  Open the selected package's start page in the default browser.

Export selected
  Export an installed package back to a .azsos file so you can send it to someone else.

Delete package
  Remove the selected package from the AZSOS library. This does not delete the original file outside the library.

Trust publisher
  Mark the selected package publisher's fingerprint as trusted on this device.

Refresh
  Reload the installed package list.

Open library folder
  Open the folder where AZSOS stores installed packages.
""".strip(),
    ),
    (
        "Offline search",
        """
You can search installed packages from the Installed tab.

Search selected
  Search only inside the selected package.

Search all
  Search across all installed packages.

Open result
  Open the selected search result.

Search tips:

- Try short keywords first.
- For Persian text, try both normal spaces and half-spaces when needed.
- Search quality depends on the package's search.sqlite index. If a publisher did not include an index, results may be incomplete.
""".strip(),
    ),
    (
        "Get content tab",
        """
The Get content tab discovers and installs remote or local packages.

Default package source:

https://github.com/TheGreatAzizi/AzSoS/tree/IR-packages

Buttons:

Fetch selected
  Scan only the currently selected source.

Fetch all
  Scan every saved source.

Open source
  Open the current source URL or folder.

Reset default
  Restore the default AZSOS IR packages source.

Save current
  Save changes to the current source name and URL.

Add as new
  Add the current name and URL as a new content source.

Remove
  Remove the selected source.

Install selected
  Download, verify, and install selected remote packages.

Inspect selected
  Download a package temporarily and show its manifest, publisher, fingerprint, and SHA-256 before installation.

Copy download URL
  Copy the selected package download URL.
""".strip(),
    ),
    (
        "Content sources and registries",
        """
AZSOS understands several source types:

1. GitHub branch/tree
   Example:
   https://github.com/TheGreatAzizi/AzSoS/tree/IR-packages

2. GitHub Releases
   If a repository has release assets ending in .azsos, AZSOS can discover them.

3. Direct .azsos URL
   Example:
   https://example.com/packs/first-aid.azsos

4. Local folder
   Example:
   C:\\AZSOS-Packs

5. packages.index.json
   The recommended publishing method. It is faster, more stable, and avoids GitHub API rate limits.

Minimal packages.index.json example:

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

For GitHub branches, place packages.index.json next to your packages folder whenever possible.
""".strip(),
    ),
    (
        "Getting content during normal access and outages",
        """
During normal internet access:

- Publishers upload .azsos packages to GitHub branches, GitHub Releases, direct file hosting, or a self-hosted Git mirror.
- Users open Get content, fetch the source, and install packages.
- Installed packages remain available offline.

During an outage or weak connectivity:

- A user who already has packages can open Share and start the local server.
- Other devices join the same Wi-Fi/hotspot/LAN and download packages from the local URL.
- If there is no network, use Export selected and copy the .azsos file through USB, external drives, Bluetooth, cables, or any other file-transfer method.

Design rule: download once, verify once, use and share offline many times.
""".strip(),
    ),
    (
        "Share tab",
        """
The Share tab publishes installed packages on the local network.

Start
  Starts a small HTTP server on this computer.

Stop
  Stops the local server.

Copy URL
  Copies the local share URL.

QR
  Generates a QR code for the share URL so phones can open it quickly.

How to use it:

1. Connect this computer to Wi-Fi, hotspot, or LAN.
2. In AZSOS, open Share and click Start.
3. Send the shown URL or display the QR code.
4. Other devices must be on the same network.
5. They open the URL in a browser and download .azsos files.

Security tip: click Stop when you are done, especially on public networks.
""".strip(),
    ),
    (
        "Creating .azsos packages with the CLI",
        """
AZSOS includes a command-line tool for publishers and content authors.

Create a publisher key:

python azsos.py keygen --out-dir keys

Build a package:

python azsos.py pack ^
  --content examples/first-aid/content ^
  --id first-aid.fa ^
  --title "First Aid" ^
  --version 0.1.0 ^
  --publisher-name "AZSOS Publisher" ^
  --key keys/publisher_private.pem ^
  --out dist/first-aid.azsos

Verify a package:

python azsos.py verify dist/first-aid.azsos

Install from the CLI:

python azsos.py install dist/first-aid.azsos

Search from the CLI:

python azsos.py search water

Start local sharing from the CLI:

python azsos.py serve

Never commit your publisher private key to a public repository. Publish only the public key or fingerprint.
""".strip(),
    ),
    (
        "Building packages.index.json",
        """
A registry file makes package discovery faster and more reliable.

Recommended IR-packages branch layout:

IR-packages/
  packages.index.json
  packages/
    first-aid.azsos
    digital-safety.azsos
    offline-business-kit.azsos

Build a registry with the CLI:

python azsos.py registry build ^
  --packages-dir ./packages ^
  --base-url https://raw.githubusercontent.com/TheGreatAzizi/AzSoS/IR-packages/packages ^
  --out packages.index.json ^
  --source-name azsos-ir-packages

Then push these files to:

https://github.com/TheGreatAzizi/AzSoS/tree/IR-packages

Benefits:

- Fetch is faster.
- AZSOS needs the GitHub API less often.
- SHA-256 values are listed in advance.
- Titles, versions, and publisher names can display more clearly.
""".strip(),
    ),
    (
        "Software updates",
        """
The app has a Check updates button in the header.

Default update source:

https://github.com/TheGreatAzizi/AzSoS/tree/UPDATE

AZSOS looks for:

- update.index.json
- .exe files
- .msi files
- .zip files
- GitHub Releases as a fallback

Behavior:

1. AZSOS finds update candidates.
2. The user selects one.
3. The file is downloaded to:

~/AZSOS/updates/

4. AZSOS does not run installers automatically. The user opens the installer or archive manually.

This is safer than silently executing downloaded files.
""".strip(),
    ),
    (
        "Security and trust",
        """
AZSOS checks several layers before installation:

1. ZIP structure
   Dangerous paths such as ../evil.txt are rejected.

2. Hashes
   Every packaged file is checked against hashes.json.

3. Ed25519 signature
   The manifest and hashes must match the publisher signature.

4. Publisher fingerprint
   Publishers are identified by fingerprints, not only display names.

5. Trust publisher
   After verifying a fingerprint through a trusted channel, users can mark that publisher as trusted on their device.

Status meanings:

Valid package
  The file is structurally valid and the signature is correct.

Unknown publisher
  The file is valid, but the publisher has not been trusted on this device.

Trusted publisher
  This publisher fingerprint was previously trusted on this device.

Invalid package
  The file is broken, incomplete, tampered with, or unsafe.

Important rule: trust a publisher only after checking the fingerprint through an official site, official channel, trusted contact, or in-person verification.
""".strip(),
    ),
    (
        "Common errors",
        """
No .azsos packages found
  The selected source did not contain any discoverable .azsos package. Check the branch, file paths, and packages.index.json.

HTTP Error 403: rate limit exceeded
  GitHub limited unauthenticated requests. Best fix: publish packages.index.json. Temporary fix: set a GitHub token.

PowerShell example:

$env:AZSOS_GITHUB_TOKEN="ghp_xxx"
python run_app.py

Not found / 404
  The repository, branch, path, or filename is wrong.

Invalid package
  The file is incomplete, corrupted, tampered with, or incompatible with the current AZSOS format.

Missing entry
  manifest.json points to a start page that does not exist inside the package.

Search returns no results
  The package may not include search.sqlite, or the search term is too specific.

Local Share does not open
  Devices must be on the same network. Windows Firewall may require an Allow action.
""".strip(),
    ),
    (
        "Important folders",
        """
AZSOS stores user data under the user's home folder.

Package library:
~/AZSOS/library/

Settings and content sources:
~/AZSOS/config.json

Downloaded updates:
~/AZSOS/updates/

Temporary downloads may be stored in the system temp folder.

To open the library from the app:

Installed -> Open library folder

To reset the local AZSOS installation, close the app and delete ~/AZSOS. Export important packages first.
""".strip(),
    ),
    (
        "Publisher checklist",
        """
Good packages are small, clear, source-aware, and easy to verify.

Recommendations:

- Keep content short and readable offline.
- Compress images.
- Cite sources inside the content.
- Add review dates for emergency or medical information.
- Use clear versions: 0.1.0, 0.2.0, 1.0.0.
- Keep package IDs stable, for example first-aid.fa.basic.
- Protect the publisher private key.
- Publish the public fingerprint on official channels.
- Generate packages.index.json.
- Test verify, install, search, and open before publishing.

Pre-release checklist:

[ ] .azsos file was created
[ ] verify succeeds
[ ] install succeeds
[ ] search works
[ ] Open package opens the correct start page
[ ] content includes sources and dates where needed
[ ] registry was generated
[ ] raw download links in the registry are correct
""".strip(),
    ),
    (
        "Useful CLI commands",
        """
Show help:

python azsos.py --help

Create a key:

python azsos.py keygen --out-dir keys

Build a package:

python azsos.py pack --content ./content --id my.pack.fa --title "Title" --version 0.1.0 --publisher-name "Publisher" --key keys/publisher_private.pem --out my-pack.azsos

Verify a package:

python azsos.py verify my-pack.azsos

Install a package:

python azsos.py install my-pack.azsos

Delete an installed package:

python azsos.py delete <package-id-or-installed-path>

Search:

python azsos.py search help

Fetch a catalog:

python azsos.py catalog fetch

Inspect a remote package:

python azsos.py catalog inspect <url-or-index>

Install from a catalog:

python azsos.py catalog install <url-or-index>

Build a registry:

python azsos.py registry build --packages-dir ./packages --base-url <raw-base-url> --out packages.index.json
""".strip(),
    ),
    (
        "Project links",
        """
Main repository:
https://github.com/TheGreatAzizi/AzSoS

Content packages branch:
https://github.com/TheGreatAzizi/AzSoS/tree/IR-packages

Software update branch:
https://github.com/TheGreatAzizi/AzSoS/tree/UPDATE

X / Twitter:
https://x.com/the_azzi

GitHub profile:
https://github.com/TheGreatAzizi

Self-hosted Git:
https://git.theazizi.ir/TheAzizi

Telegram:
https://t.me/luluch_code
""".strip(),
    ),
]


def manual_as_markdown() -> str:
    parts = ["# AZSOS Desktop Manual", ""]
    for title, body in DOC_TOPICS:
        parts.append(f"## {title}")
        parts.append("")
        parts.append(body)
        parts.append("")
    return "\n".join(parts).strip() + "\n"
