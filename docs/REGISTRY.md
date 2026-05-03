# Package registry draft

AZSOS does not need a registry to work. A registry is only a discovery layer for users who have internet access before an outage.

## File name

```text
packages.index.json
```

## Format

```json
{
  "format": "azsos.index.v1",
  "updated_at": "2026-05-03T00:00:00Z",
  "packages": []
}
```

Each package item should contain:

```json
{
  "id": "first-aid.fa.demo",
  "title": "First Aid Demo",
  "version": "0.1.0",
  "language": "fa",
  "download_url": "https://example.invalid/first-aid-demo.azsos",
  "sha256": "hex-sha256-of-the-azsos-file",
  "publisher_name": "AZSOS Demo Publisher",
  "publisher_fingerprint": "ABCD 1234 ...",
  "size_bytes": 12345,
  "tags": ["first-aid"]
}
```

## Security

The registry can be signed in a later release, but package verification must never depend only on the registry. The `.azsos` package must remain self-verifying.

## User experience

Desktop flow:

1. User pastes a registry URL in the **Content source / online catalog** field.
2. User clicks **Fetch**.
3. AZSOS downloads the index.
4. User picks a package and clicks **Install selected**.
5. AZSOS downloads the file.
6. AZSOS verifies the package signature and SHA-256 before installing.
