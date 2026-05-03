# Security Policy

## Supported versions

AZSOS is currently alpha software. Security fixes target the latest `main` branch and the latest release tag.

## Reporting a vulnerability

Please report security issues privately first when possible.

Contact links:

- X: https://x.com/the_azzi
- Telegram: https://t.me/luluch_code
- GitHub: https://github.com/TheGreatAzizi
- Self-hosted Git: https://git.theazizi.ir/TheAzizi

## Scope

Security-sensitive areas include:

- `.azsos` package verification
- ZIP extraction and path handling
- Ed25519 signing and verification
- Search database handling
- HTML rendering and sanitization
- Local share server behavior

## Notes

A valid package signature proves that package metadata and hashed files match the included publisher key. It does not prove the publisher is trustworthy. A persistent trust-store is planned.
