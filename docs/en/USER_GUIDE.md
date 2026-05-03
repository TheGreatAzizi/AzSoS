# User guide

> Language: **English** | [فارسی](../fa/USER_GUIDE.md)


## What AZSOS is for

AZSOS helps users keep important content available when the internet is slow, filtered, unstable, or fully unavailable. The user downloads a package once, AZSOS verifies it, then the content remains usable offline.

## Main tabs

### Installed

Use this tab to manage content already on your computer.

Actions:

- **Import `.azsos`**: add a package from disk.
- **Open package**: open the package entry page in the browser.
- **Search selected**: search inside one package.
- **Search all**: search across installed packages.
- **Export package**: save an installed package as a `.azsos` file.
- **Delete package**: remove the selected package from your local library.
- **Trust publisher**: mark the package publisher fingerprint as trusted on this device.

### Get content

Use this tab to find packages from online or local sources.

Supported sources:

- GitHub branch/tree URLs
- GitHub Releases
- direct `.azsos` links
- local folders
- `packages.index.json` registry files

Recommended flow:

1. Keep the default source selected.
2. Click **Fetch selected**.
3. Inspect a package if needed.
4. Select one or more packages.
5. Click **Install selected**.

### Share

Use this tab to share installed packages over a local network. This is useful when only one device has the packages and other devices are nearby.

Flow:

1. Connect devices to the same Wi-Fi, hotspot, or LAN.
2. Click **Start** in the Share tab.
3. Copy the local URL or show the QR code.
4. Other devices open the URL and download packages.

### Docs

The Docs tab explains AZSOS directly inside the app. It is English-only and uses Markdown-style rendering.

## Where files are stored

AZSOS stores user data under:

```text
~/AZSOS/
```

Important folders:

```text
~/AZSOS/library/    installed packages
~/AZSOS/incoming/   temporary downloads
~/AZSOS/updates/    downloaded software updates
~/AZSOS/config.json content source settings
```

## Safe usage tips

- Prefer packages from known publishers.
- Check the publisher fingerprint through a trusted channel before trusting it.
- Do not treat discovery as trust.
- Keep exported packages in a safe place if you want to share them later.
