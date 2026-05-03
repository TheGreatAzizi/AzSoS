from pathlib import Path
import json
import zipfile

from azsos_core.catalog import (
    DEFAULT_SOURCE_URL,
    DEFAULT_UPDATE_SOURCE_URL,
    build_registry,
    discover_from_registry,
    discover_local_folder,
    discover_updates_from_registry,
)
from azsos_core.crypto import generate_keypair
from azsos_core.package import (
    delete_installed,
    install_package,
    pack_package,
    search_installed,
    verify_package,
)


def make_test_package(tmp_path: Path) -> Path:
    content = tmp_path / "content"
    content.mkdir()
    (content / "index.md").write_text("# First Aid\n\nBurns and bleeding basics.", encoding="utf-8")
    (content / "burns.md").write_text("# Burns\n\nCool the burn with clean water.", encoding="utf-8")

    private_key, public_key = generate_keypair()
    return pack_package(
        content_dir=content,
        package_id="test.first-aid",
        title="First Aid Test",
        version="0.1.0",
        publisher_name="Test Publisher",
        private_key=private_key,
        public_key=public_key,
        out_path=tmp_path / "first-aid.azsos",
    )


def test_pack_verify_install_search_delete(tmp_path: Path) -> None:
    package = make_test_package(tmp_path)

    result = verify_package(package)
    assert result.ok, result.errors
    assert result.manifest is not None
    assert result.manifest["format"] == "azsos.v1"

    library = tmp_path / "library"
    installed = install_package(package, library)
    hits = search_installed(installed, "burns")
    assert hits
    assert any("burn" in hit.snippet.lower() or "burn" in hit.title.lower() for hit in hits)

    delete_installed(installed, library)
    assert not installed.exists()


def test_verify_rejects_zip_slip_path(tmp_path: Path) -> None:
    package = tmp_path / "bad.azsos"
    with zipfile.ZipFile(package, "w") as zf:
        zf.writestr("manifest.json", "{}")
        zf.writestr("hashes.json", "{}")
        zf.writestr("signature.ed25519", b"")
        zf.writestr("../evil.txt", "nope")

    result = verify_package(package)
    assert not result.ok
    assert any("Unsafe package path" in error for error in result.errors)


def test_registry_discovery_from_local_json(tmp_path: Path) -> None:
    registry = tmp_path / "packages.index.json"
    registry.write_text(
        json.dumps(
            {
                "packages": [
                    {
                        "name": "demo.azsos",
                        "download_url": "https://example.com/demo.azsos",
                        "size_bytes": 123,
                        "sha256": "a" * 64,
                    },
                    {"name": "ignore.txt", "download_url": "https://example.com/ignore.txt"},
                ]
            }
        ),
        encoding="utf-8",
    )
    packages = discover_from_registry(str(registry))
    assert len(packages) == 1
    assert packages[0].name == "demo.azsos"
    assert packages[0].sha256 == "a" * 64


def test_local_folder_discovery_and_registry_build(tmp_path: Path) -> None:
    package = make_test_package(tmp_path)
    packages_dir = tmp_path / "packages"
    packages_dir.mkdir()
    target = packages_dir / package.name
    target.write_bytes(package.read_bytes())

    found = discover_local_folder(packages_dir)
    assert len(found) == 1
    assert found[0].download_url.startswith("file:")

    registry = tmp_path / "packages.index.json"
    build_registry(packages_dir, "https://example.com/packs", registry, source_name="test-registry")
    data = json.loads(registry.read_text(encoding="utf-8"))
    assert data["format"] == "azsos.registry.v1"
    assert len(data["packages"]) == 1
    assert data["packages"][0]["download_url"] == "https://example.com/packs/first-aid.azsos"
    assert len(data["packages"][0]["sha256"]) == 64


def test_default_source_points_to_ir_packages_branch() -> None:
    assert DEFAULT_SOURCE_URL == "https://github.com/TheGreatAzizi/AzSoS/tree/IR-packages"


def test_default_update_source_points_to_update_branch() -> None:
    assert DEFAULT_UPDATE_SOURCE_URL == "https://github.com/TheGreatAzizi/AzSoS/tree/UPDATE"


def test_update_registry_discovery_from_local_json(tmp_path: Path) -> None:
    registry = tmp_path / "update.index.json"
    registry.write_text(
        json.dumps(
            {
                "updates": [
                    {
                        "name": "AZSOS-Desktop-v0.3.4.exe",
                        "download_url": "https://example.com/AZSOS-Desktop-v0.3.4.exe",
                        "version": "0.3.4",
                        "sha256": "b" * 64,
                    },
                    {"name": "ignore.azsos", "download_url": "https://example.com/ignore.azsos"},
                ]
            }
        ),
        encoding="utf-8",
    )
    updates = discover_updates_from_registry(str(registry))
    assert len(updates) == 1
    assert updates[0].name == "AZSOS-Desktop-v0.3.4.exe"
    assert updates[0].version == "0.3.4"


def test_in_app_manual_has_core_topics() -> None:
    from azsos_core.manual import DOC_TOPICS, manual_as_markdown

    titles = [title for title, _body in DOC_TOPICS]
    manual = manual_as_markdown()
    assert "Quick start" in titles
    assert "Get content tab" in titles
    assert "Share tab" in titles
    assert "Security and trust" in titles
    assert ".azsos" in manual
    assert "packages.index.json" in manual
