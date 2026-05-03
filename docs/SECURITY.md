# AZSOS Security Notes

AZSOS is designed around local-first distribution. The security goal is to detect tampering and avoid unsafe package extraction.

## What is verified

- ZIP structure is readable
- Required files exist
- Package format equals `azsos.v1`
- Hashed files exist
- SHA-256 digest of every hashed file matches `hashes.json`
- Ed25519 signature over manifest and hashes is valid
- Unsafe ZIP paths are rejected

## What is not solved yet

- There is no persistent trusted-publisher store yet.
- A valid signature does not mean the publisher is trusted.
- The current desktop app opens content in the default browser.
- The embedded restricted viewer is not implemented yet.

## Content rules for package authors

- Keep packages usable offline.
- Avoid remote images, scripts, and external dependencies.
- Include source and review metadata for high-impact content.
- Do not ship medical or legal advice without a source and disclaimer.
- Keep package size small enough for local transfer.

## Private keys

Never commit real publisher private keys. Generate new keys locally and keep them offline when possible.
