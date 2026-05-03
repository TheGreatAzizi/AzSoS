# Security model

> Language: **English** | [فارسی](../fa/SECURITY.md)


## Core idea

AZSOS separates **discovery** from **trust**.

A source may tell AZSOS that a package exists. Trust only starts after cryptographic verification.

## Verification checks

When installing a package, AZSOS checks:

1. The archive can be opened.
2. Required files exist.
3. No path escapes the install directory.
4. `manifest.json` uses `azsos.v1`.
5. Every listed file matches `hashes.json`.
6. The Ed25519 signature is valid.
7. Optional registry SHA-256 matches the downloaded file.

## Publisher trust

AZSOS shows the publisher name and fingerprint. The user can mark a fingerprint as trusted locally.

This does not create a global trust authority. It only means: “I trust this publisher on this device.”

## Threats AZSOS tries to reduce

- Modified packages
- Broken or incomplete downloads
- ZIP path traversal
- Confusing package sources with trusted publishers
- Silent replacement of package files

## Out of scope

AZSOS is not a VPN, messenger, antivirus, or anonymity tool. It does not hide network traffic and does not guarantee that a package source is safe.

## Reporting security issues

Please report security issues privately first when possible. Include steps to reproduce, affected version, and expected impact.
