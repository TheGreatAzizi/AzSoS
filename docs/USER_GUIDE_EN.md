# AZSOS User Guide

## What AZSOS is

AZSOS is an offline-first content cache for emergency and public-interest information. A user downloads signed `.azsos` packages while internet is available, then reads, searches, exports, and shares them offline later.

## Installing packages

1. Open **Get content**.
2. Select the default source or add your own source.
3. Click **Fetch selected** or **Fetch all**.
4. Select one or more packages.
5. Click **Install selected**.
6. AZSOS downloads and verifies every package before installation.

## Importing a local file

Use **Installed -> Import .azsos** and select a local package file. This works without internet.

## Searching offline

Use **Search selected** for one package or **Search all** for every installed package. Search uses the package's local `search.sqlite` index.

## Sharing offline

1. Open **Share**.
2. Click **Start**.
3. Copy the local URL or show the QR code.
4. Other devices on the same network open that URL in a browser and download packages.
5. Click **Stop** when finished.

## Deleting packages

Use **Installed -> Delete package**. This removes the installed copy from the AZSOS library.

## Exporting packages

Use **Installed -> Export selected** to save an installed package as a `.azsos` file for USB, LAN, or offline transfer.

## Trusting publishers

A package can be valid even if its publisher is unknown. Trust a publisher only after checking the fingerprint through an official or trusted channel.
