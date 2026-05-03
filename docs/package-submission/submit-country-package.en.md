# Submit a country package to AZSOS

> Language: [English](submit-country-package.en.md) | [فارسی](submit-country-package.fa.md) | [العربية](submit-country-package.ar.md) | [Türkçe](submit-country-package.tr.md)

This guide is for people who want to create an `.azsos` package for their country and submit it to the AZSOS repository so it can be added to the public catalog after review.

## 1. What is a country package?

A country package is a signed `.azsos` file that contains offline, searchable, useful information for people in a specific country or region. The package can be downloaded before an outage, copied by USB, shared over LAN/hotspot, or installed from the AZSOS catalog.

Good examples:

- emergency phone numbers and public service contacts
- basic first-aid pages
- family preparedness checklists
- local offline guides for small businesses
- digital safety basics
- maps or local resource lists, when the data license allows redistribution

Avoid:

- private personal data
- private keys or signing keys
- copyrighted books, articles, or paid content without permission
- medical advice without clear sources and disclaimers
- anything that would put users at unnecessary risk

## 2. Repository target

Open your pull request against the AZSOS content repository/branch used for packages:

```text
https://github.com/TheGreatAzizi/AzSoS/tree/IR-packages
```

If the maintainer creates a country-specific branch later, use the branch mentioned in the latest repository instructions.

## 3. Recommended folder layout

Use a country code folder so packages stay organized:

```text
packages/
  IR/
    first-aid-basic-fa.azsos
    digital-safety-basic-fa.azsos
  TR/
    emergency-contacts-tr.azsos
  IQ/
    first-aid-basic-ar.azsos
```

Use ISO-style country codes when possible, for example `IR`, `TR`, `IQ`, `AF`, `DE`, `FR`, `US`.

## 4. Create the content folder

Create normal Markdown or HTML content first:

```text
my-country-pack/
  index.html
  pages/
    emergency-numbers.html
    first-aid.html
    family-checklist.html
  assets/
    icon.webp
```

Keep content small, readable, and source-backed. The first page should explain what the package contains, who published it, and when it was last reviewed.

## 5. Generate a publisher key

Run this locally. Keep the private key safe and never commit it.

```powershell
python azsos.py keygen --out-dir keys
```

This creates a publisher private key and public key. The private key signs packages. The public fingerprint helps users verify the publisher.

## 6. Build the `.azsos` package

Example:

```powershell
python azsos.py pack `
  --content .\my-country-pack `
  --id ir.first-aid-basic.fa `
  --title "First Aid Basics - Iran" `
  --version 1.0.0 `
  --publisher-name "Your Team or Name" `
  --key .\keys\publisher_private.pem `
  --out .\packages\IRirst-aid-basic-fa.azsos
```

Recommended package id format:

```text
<country-code>.<topic>.<language>
```

Examples:

```text
ir.first-aid-basic.fa
tr.emergency-contacts.tr
iq.family-preparedness.ar
```

## 7. Verify the package before submitting

```powershell
python azsos.py verify .\packages\IRirst-aid-basic-fa.azsos
```

Also install and test it locally:

```powershell
python azsos.py install .\packages\IRirst-aid-basic-fa.azsos
python azsos.py search first
```

Open it in the desktop app and check:

- package title is correct
- content opens offline
- search returns useful results
- no external links are required for essential information
- package status is valid

## 8. Build or update the registry

The maintainer may rebuild the registry after merging, but contributors can include it when requested.

```powershell
python azsos.py registry build `
  --packages-dir .\packages `
  --base-url https://raw.githubusercontent.com/TheGreatAzizi/AzSoS/IR-packages/packages `
  --out packages.index.json `
  --source-name azsos-community-packages
```

The registry is for discovery. It does not replace package signatures.

## 9. Open a pull request

Your PR should include:

- the `.azsos` package file
- source/attribution notes for the content
- country and language information
- publisher fingerprint
- a short testing note

Good PR title examples:

```text
Add IR first-aid basic package (fa)
Add TR emergency contacts package (tr)
Add IQ family preparedness package (ar)
```

## 10. PR description template

Copy this into your PR:

```markdown
## Package information

- Country:
- Language:
- Package title:
- Package id:
- Version:
- Publisher name:
- Publisher fingerprint:

## Content sources and licenses

- Source 1:
- Source 2:
- License/permission notes:

## Testing

- [ ] `python azsos.py verify <package>.azsos` passes
- [ ] The package installs in AZSOS Desktop
- [ ] Search works offline
- [ ] Essential pages open without internet
- [ ] No private keys are included
- [ ] No private personal data is included

## Notes for reviewer

Write anything the maintainer should know.
```

## 11. Review rules

A package can be rejected or delayed if:

- it fails verification
- it has unclear sources
- it includes private or unsafe material
- it is too large without a good reason
- it has misleading claims
- it ships a private key or secrets
- it depends on internet access for core content

## 12. Security reminders

- Do not commit `publisher_private.pem`.
- Do not publish secrets, tokens, or private documents.
- Sign every package.
- Keep a copy of your private key offline.
- If a key is leaked, stop using it and notify users.

## 13. Maintainer merge flow

After a PR is accepted, the maintainer can:

1. verify the package,
2. inspect the package metadata,
3. rebuild `packages.index.json`,
4. push the updated catalog branch,
5. test Fetch inside AZSOS Desktop.

After that, users can open AZSOS, go to **Get content**, press **Fetch**, and install the new package.
