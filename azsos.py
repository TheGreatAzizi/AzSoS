from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from azsos_core.catalog import (
    DEFAULT_SOURCE_URL,
    build_registry,
    discover_packages,
    download_package,
    inspect_remote_package,
)
from azsos_core.crypto import generate_keypair, load_private_key, public_from_private, save_keypair
from azsos_core.local_server import ShareServer
from azsos_core.package import (
    delete_installed,
    install_package,
    list_installed,
    pack_package,
    search_installed,
    verify_package,
)

DEFAULT_LIBRARY = Path.home() / "AZSOS" / "library"


def cmd_keygen(args: argparse.Namespace) -> int:
    private_key, public_key = generate_keypair()
    save_keypair(private_key, public_key, Path(args.out_dir))
    print(f"Wrote keys to {args.out_dir}")
    return 0


def cmd_pack(args: argparse.Namespace) -> int:
    private_key = load_private_key(Path(args.key))
    public_key = public_from_private(private_key)
    out = pack_package(
        content_dir=Path(args.content),
        package_id=args.id,
        title=args.title,
        version=args.version,
        publisher_name=args.publisher_name,
        private_key=private_key,
        public_key=public_key,
        out_path=Path(args.out),
        language=args.language,
    )
    print(f"Wrote {out}")
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    result = verify_package(Path(args.package))
    print(f"Package: {result.package_path}")
    print(f"Status: {'OK' if result.ok else 'FAILED'}")
    if result.manifest:
        print(f"Title: {result.manifest.get('title')}")
        print(f"ID: {result.manifest.get('id')}")
        print(f"Version: {result.manifest.get('version')}")
        print(f"Format: {result.manifest.get('format')}")
        print(f"Publisher: {result.manifest.get('publisher', {}).get('name')}")
        print(f"Fingerprint: {result.manifest.get('publisher', {}).get('fingerprint')}")
    for warning in result.warnings:
        print(f"Warning: {warning}")
    for error in result.errors:
        print(f"Error: {error}", file=sys.stderr)
    return 0 if result.ok else 1


def cmd_install(args: argparse.Namespace) -> int:
    dest = install_package(Path(args.package), Path(args.library))
    print(f"Installed to {dest}")
    return 0


def cmd_delete(args: argparse.Namespace) -> int:
    library = Path(args.library)
    packages = list_installed(library)
    needle = args.package
    matches = []
    for manifest in packages:
        if needle in {manifest.get("id"), manifest.get("title"), f"{manifest.get('id')}@{manifest.get('version')}"}:
            matches.append(manifest)
    if not matches:
        print(f"No installed package matched: {needle}", file=sys.stderr)
        return 1
    if len(matches) > 1:
        print("Multiple packages matched. Use id@version:", file=sys.stderr)
        for manifest in matches:
            print(f"- {manifest.get('id')}@{manifest.get('version')} ({manifest.get('title')})", file=sys.stderr)
        return 1
    delete_installed(Path(matches[0]["_path"]), library)
    print(f"Deleted {matches[0].get('title')}")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    packages = list_installed(Path(args.library))
    if not packages:
        print("No packages installed.")
        return 0
    for manifest in packages:
        print(f"- {manifest.get('title')} ({manifest.get('id')} {manifest.get('version')})")
        print(f"  publisher: {manifest.get('publisher', {}).get('name')} [{manifest.get('publisher', {}).get('fingerprint')}]")
        print(f"  path: {manifest.get('_path')}")
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    packages = list_installed(Path(args.library))
    found = 0
    for manifest in packages:
        package_dir = Path(manifest.get("_path"))
        hits = search_installed(package_dir, args.query, limit=args.limit)
        if hits:
            print(f"\n{manifest.get('title')}:")
        for hit in hits:
            found += 1
            print(f"- {hit.title} [{hit.path}]")
            print(f"  {hit.snippet}")
    if not found:
        print("No results.")
    return 0


def cmd_serve(args: argparse.Namespace) -> int:
    server = ShareServer(Path(args.library), port=args.port)
    url = server.start()
    print(f"AZSOS local share running at {url}")
    print("Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        server.stop()
        print("Stopped.")
    return 0


def cmd_catalog_fetch(args: argparse.Namespace) -> int:
    packages = discover_packages(args.source, include_releases=not args.no_releases)
    if args.json:
        print(json.dumps([package.to_dict() for package in packages], ensure_ascii=False, indent=2))
        return 0
    if not packages:
        print("No .azsos packages found.")
        return 0
    for idx, package in enumerate(packages, start=1):
        print(f"{idx}. {package.display()}")
        print(f"   url: {package.download_url}")
    return 0


def cmd_catalog_inspect(args: argparse.Namespace) -> int:
    packages = discover_packages(args.source, include_releases=not args.no_releases)
    if not packages:
        print("No .azsos packages found.", file=sys.stderr)
        return 1
    package = packages[args.index - 1]
    enriched, downloaded = inspect_remote_package(package)
    print(enriched.display())
    print(f"ID: {enriched.package_id}")
    print(f"Fingerprint: {enriched.fingerprint}")
    print(f"SHA-256: {enriched.sha256}")
    print(f"Downloaded to: {downloaded}")
    return 0


def cmd_catalog_install(args: argparse.Namespace) -> int:
    packages = discover_packages(args.source, include_releases=not args.no_releases)
    if not packages:
        print("No .azsos packages found.", file=sys.stderr)
        return 1
    package = packages[args.index - 1]
    downloaded = download_package(package)
    result = verify_package(downloaded)
    if not result.ok:
        print("Downloaded package failed verification:", file=sys.stderr)
        for error in result.errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    dest = install_package(downloaded, Path(args.library))
    print(f"Installed {package.name} to {dest}")
    return 0


def cmd_registry_build(args: argparse.Namespace) -> int:
    out = build_registry(Path(args.packages_dir), args.base_url, Path(args.out), source_name=args.source_name)
    print(f"Wrote registry to {out}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    from azsos_core import __version__

    parser = argparse.ArgumentParser(prog="azsos", description="AZSOS offline emergency package tools")
    parser.add_argument("--version", action="version", version=f"AZSOS {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("keygen", help="Create an Ed25519 publisher keypair")
    p.add_argument("--out-dir", default="keys")
    p.set_defaults(func=cmd_keygen)

    p = sub.add_parser("pack", help="Build a .azsos package from a content folder")
    p.add_argument("--content", required=True, help="Folder containing Markdown/HTML/assets")
    p.add_argument("--id", required=True, help="Stable package id, e.g. first-aid.fa.demo")
    p.add_argument("--title", required=True)
    p.add_argument("--version", required=True)
    p.add_argument("--publisher-name", required=True)
    p.add_argument("--key", required=True, help="publisher_private.pem")
    p.add_argument("--out", required=True)
    p.add_argument("--language", default="fa")
    p.set_defaults(func=cmd_pack)

    p = sub.add_parser("verify", help="Verify a .azsos package")
    p.add_argument("package")
    p.set_defaults(func=cmd_verify)

    p = sub.add_parser("install", help="Install a .azsos package into the local library")
    p.add_argument("package")
    p.add_argument("--library", default=str(DEFAULT_LIBRARY))
    p.set_defaults(func=cmd_install)

    p = sub.add_parser("delete", help="Delete an installed package by id, title, or id@version")
    p.add_argument("package")
    p.add_argument("--library", default=str(DEFAULT_LIBRARY))
    p.set_defaults(func=cmd_delete)

    p = sub.add_parser("list", help="List installed packages")
    p.add_argument("--library", default=str(DEFAULT_LIBRARY))
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("search", help="Search installed packages")
    p.add_argument("query")
    p.add_argument("--library", default=str(DEFAULT_LIBRARY))
    p.add_argument("--limit", type=int, default=10)
    p.set_defaults(func=cmd_search)

    p = sub.add_parser("serve", help="Share installed packages over local Wi-Fi/hotspot")
    p.add_argument("--library", default=str(DEFAULT_LIBRARY))
    p.add_argument("--port", type=int, default=8765)
    p.set_defaults(func=cmd_serve)

    catalog = sub.add_parser("catalog", help="Discover and install remote .azsos packages")
    cat_sub = catalog.add_subparsers(dest="catalog_command", required=True)

    p = cat_sub.add_parser("fetch", help="List packages from a GitHub/tree/release/registry/local source")
    p.add_argument("source", nargs="?", default=DEFAULT_SOURCE_URL)
    p.add_argument("--no-releases", action="store_true")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_catalog_fetch)

    p = cat_sub.add_parser("inspect", help="Download and show metadata for a remote package")
    p.add_argument("source", nargs="?", default=DEFAULT_SOURCE_URL)
    p.add_argument("--index", type=int, default=1)
    p.add_argument("--no-releases", action="store_true")
    p.set_defaults(func=cmd_catalog_inspect)

    p = cat_sub.add_parser("install", help="Install a remote package by index")
    p.add_argument("source", nargs="?", default=DEFAULT_SOURCE_URL)
    p.add_argument("--index", type=int, default=1)
    p.add_argument("--library", default=str(DEFAULT_LIBRARY))
    p.add_argument("--no-releases", action="store_true")
    p.set_defaults(func=cmd_catalog_install)

    registry = sub.add_parser("registry", help="Build a packages.index.json for publishing")
    reg_sub = registry.add_subparsers(dest="registry_command", required=True)

    p = reg_sub.add_parser("build", help="Build registry JSON from a folder of .azsos packages")
    p.add_argument("--packages-dir", required=True)
    p.add_argument("--base-url", required=True, help="Base raw/download URL where packages will be hosted")
    p.add_argument("--out", default="packages.index.json")
    p.add_argument("--source-name", default="azsos-registry")
    p.set_defaults(func=cmd_registry_build)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except IndexError:
        print("Package index is out of range.", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
