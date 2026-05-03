from __future__ import annotations

import hashlib
import html
import json
import re
import shutil
import sqlite3
import tempfile
import time
import zipfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from . import FORMAT_VERSION, PACKAGE_EXTENSION
from .crypto import b64d, b64e, fingerprint, sign as ed_sign, verify as ed_verify
from .normalize import normalize_fa

try:
    import markdown as markdown_lib
except Exception:  # pragma: no cover
    markdown_lib = None


@dataclass
class VerifyResult:
    ok: bool
    package_path: Path
    manifest: dict | None = None
    trusted_fingerprint: str | None = None
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass
class SearchHit:
    title: str
    path: str
    snippet: str


def canonical_json_bytes(obj: object) -> bytes:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def is_safe_zip_name(name: str) -> bool:
    path = Path(name)
    if path.is_absolute():
        return False
    if "\\" in name:
        return False
    return all(part not in {"", ".", ".."} for part in path.parts)


def safe_extract_zip(zf: zipfile.ZipFile, dest: Path) -> None:
    dest_resolved = dest.resolve()
    for member in zf.infolist():
        if not is_safe_zip_name(member.filename):
            raise ValueError(f"Unsafe package path: {member.filename}")
        target = (dest / member.filename).resolve()
        try:
            target.relative_to(dest_resolved)
        except ValueError as exc:
            raise ValueError(f"Unsafe package path: {member.filename}") from exc
    zf.extractall(dest)


def sanitize_html(raw: str) -> str:
    raw = re.sub(r"<\s*script\b[^>]*>.*?<\s*/\s*script\s*>", "", raw, flags=re.I | re.S)
    raw = re.sub(r"\son[a-z]+\s*=\s*(['\"]).*?\1", "", raw, flags=re.I | re.S)
    raw = re.sub(r"\s(href|src)\s*=\s*(['\"])\s*javascript:.*?\2", "", raw, flags=re.I | re.S)
    raw = re.sub(r"\s(src|srcset)\s*=\s*(['\"])\s*https?://.*?\2", "", raw, flags=re.I | re.S)
    return raw


def html_to_text(raw: str) -> str:
    text = re.sub(r"<[^>]+>", " ", raw)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def markdown_to_html(md: str) -> str:
    if markdown_lib is not None:
        return markdown_lib.markdown(md, extensions=["tables", "fenced_code"])
    escaped = html.escape(md)
    paragraphs = "\n".join(f"<p>{line}</p>" for line in escaped.splitlines() if line.strip())
    return paragraphs or "<p></p>"


def wrap_html(title: str, body_html: str, language: str = "fa") -> str:
    direction = "rtl" if language.startswith("fa") or language.startswith("ar") else "ltr"
    return f"""<!doctype html>
<html lang=\"{html.escape(language)}\" dir=\"{direction}\">
<head>
<meta charset=\"utf-8\">
<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
<title>{html.escape(title)}</title>
<style>
:root {{ color-scheme: light dark; }}
body {{ font-family: system-ui, -apple-system, Segoe UI, Tahoma, Arial, sans-serif; line-height: 1.75; max-width: 900px; margin: 32px auto; padding: 0 20px; }}
a {{ overflow-wrap: anywhere; }}
img {{ max-width: 100%; height: auto; }}
code, pre {{ white-space: pre-wrap; }}
.card {{ border: 1px solid #ccc; border-radius: 14px; padding: 16px; margin: 16px 0; }}
</style>
</head>
<body>
{body_html}
</body>
</html>"""


def iter_content_files(content_dir: Path) -> Iterable[Path]:
    for path in content_dir.rglob("*"):
        if path.is_file() and not path.name.startswith("."):
            yield path


def safe_id(text: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "-", text).strip(".-")
    return cleaned or "package"


def build_search_index(content_root: Path, db_path: Path) -> None:
    if db_path.exists():
        db_path.unlink()
    con = sqlite3.connect(db_path)
    try:
        con.execute("CREATE VIRTUAL TABLE pages_fts USING fts5(title, body, path, tokenize='unicode61')")
        for file_path in sorted((content_root / "content").rglob("*.html")):
            rel = file_path.relative_to(content_root).as_posix()
            raw = file_path.read_text(encoding="utf-8", errors="ignore")
            title_match = re.search(r"<title>(.*?)</title>", raw, flags=re.I | re.S)
            h1_match = re.search(r"<h1[^>]*>(.*?)</h1>", raw, flags=re.I | re.S)
            title = html_to_text(title_match.group(1) if title_match else h1_match.group(1) if h1_match else file_path.stem)
            body = normalize_fa(html_to_text(raw))
            con.execute("INSERT INTO pages_fts(title, body, path) VALUES (?, ?, ?)", (title, body, rel))
        con.commit()
    finally:
        con.close()


def pack_package(
    *,
    content_dir: Path,
    package_id: str,
    title: str,
    version: str,
    publisher_name: str,
    private_key: bytes,
    public_key: bytes,
    out_path: Path,
    language: str = "fa",
) -> Path:
    if out_path.suffix.lower() != PACKAGE_EXTENSION:
        out_path = out_path.with_suffix(PACKAGE_EXTENSION)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp_name:
        tmp = Path(tmp_name)
        root = tmp / "pkg"
        content_out = root / "content"
        content_out.mkdir(parents=True)

        copied_any = False
        for src in iter_content_files(content_dir):
            rel = src.relative_to(content_dir)
            suffix = src.suffix.lower()
            dst_rel = rel
            if suffix in {".md", ".markdown"}:
                dst_rel = rel.with_suffix(".html")
                title_for_page = src.stem.replace("-", " ").replace("_", " ")
                body_html = markdown_to_html(src.read_text(encoding="utf-8", errors="ignore"))
                final_html = sanitize_html(wrap_html(title_for_page, body_html, language=language))
                dst = content_out / dst_rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_text(final_html, encoding="utf-8")
                copied_any = True
            elif suffix in {".html", ".htm"}:
                dst = content_out / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                final_html = sanitize_html(src.read_text(encoding="utf-8", errors="ignore"))
                dst.write_text(final_html, encoding="utf-8")
                copied_any = True
            else:
                dst = content_out / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
                copied_any = True

        if not copied_any:
            raise ValueError(f"No content files found in {content_dir}")

        entry = "content/index.html"
        if not (root / entry).exists():
            html_files = sorted((root / "content").rglob("*.html"))
            first_html = html_files[0] if html_files else None
            if first_html is None:
                raise ValueError("Package must contain at least one HTML or Markdown file")
            entry = first_html.relative_to(root).as_posix()

        search_db = root / "search.sqlite"
        build_search_index(root, search_db)

        files_for_hash = []
        for path in sorted(root.rglob("*")):
            if path.is_file():
                files_for_hash.append(path)

        hashes = {p.relative_to(root).as_posix(): sha256_file(p) for p in files_for_hash}
        size_bytes = sum(p.stat().st_size for p in files_for_hash)
        manifest = {
            "format": FORMAT_VERSION,
            "id": package_id,
            "title": title,
            "language": language,
            "version": version,
            "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "publisher": {
                "name": publisher_name,
                "public_key": b64e(public_key),
                "fingerprint": fingerprint(public_key),
            },
            "entry": entry,
            "search_index": "search.sqlite",
            "size_bytes": size_bytes,
            "min_app_version": "0.1.0",
        }
        (root / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        hashes["manifest.json"] = sha256_file(root / "manifest.json")
        (root / "hashes.json").write_text(json.dumps(hashes, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")

        signed_payload = canonical_json_bytes({"manifest": manifest, "hashes": hashes})
        signature = ed_sign(private_key, signed_payload)
        (root / "signature.ed25519").write_bytes(signature)

        with zipfile.ZipFile(out_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
            for path in sorted(root.rglob("*")):
                if path.is_file():
                    zf.write(path, path.relative_to(root).as_posix())
    return out_path


def verify_package(package_path: Path) -> VerifyResult:
    result = VerifyResult(ok=False, package_path=package_path)
    if not package_path.exists():
        result.errors.append("Package file does not exist")
        return result
    if package_path.suffix.lower() != PACKAGE_EXTENSION:
        result.warnings.append(f"Expected {PACKAGE_EXTENSION} extension")
    try:
        with zipfile.ZipFile(package_path, "r") as zf:
            names = set(zf.namelist())
            for required in {"manifest.json", "hashes.json", "signature.ed25519"}:
                if required not in names:
                    result.errors.append(f"Missing {required}")
            if result.errors:
                return result
            unsafe_names = [name for name in names if not is_safe_zip_name(name)]
            if unsafe_names:
                result.errors.append(f"Unsafe package path: {unsafe_names[0]}")
                return result

            manifest = json.loads(zf.read("manifest.json").decode("utf-8"))
            hashes = json.loads(zf.read("hashes.json").decode("utf-8"))
            signature = zf.read("signature.ed25519")
            result.manifest = manifest

            if manifest.get("format") != FORMAT_VERSION:
                result.errors.append(f"Unsupported format: {manifest.get('format')}")

            for rel, expected in hashes.items():
                if rel not in names:
                    result.errors.append(f"Missing hashed file: {rel}")
                    continue
                actual = sha256_bytes(zf.read(rel))
                if actual != expected:
                    result.errors.append(f"Hash mismatch: {rel}")

            public_key_text = manifest.get("publisher", {}).get("public_key", "")
            if not public_key_text:
                result.errors.append("Missing publisher public key")
            else:
                public_key = b64d(public_key_text)
                result.trusted_fingerprint = fingerprint(public_key)
                payload = canonical_json_bytes({"manifest": manifest, "hashes": hashes})
                if not ed_verify(public_key, payload, signature):
                    result.errors.append("Signature verification failed")

            entries = names - set(hashes.keys()) - {"hashes.json", "signature.ed25519"}
            if entries:
                result.warnings.append(f"Package has {len(entries)} unhashed extra file(s)")
    except zipfile.BadZipFile:
        result.errors.append("Not a valid AZSOS/ZIP package")
    except Exception as exc:
        result.errors.append(str(exc))
    result.ok = not result.errors
    return result


def install_package(package_path: Path, library_dir: Path) -> Path:
    verification = verify_package(package_path)
    if not verification.ok or not verification.manifest:
        raise ValueError("Invalid package: " + "; ".join(verification.errors))
    manifest = verification.manifest
    package_key = safe_id(f"{manifest.get('id','package')}-{manifest.get('version','0')}")
    dest = library_dir / package_key
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    with zipfile.ZipFile(package_path, "r") as zf:
        safe_extract_zip(zf, dest)
    shutil.copy2(package_path, dest / f"{package_key}{PACKAGE_EXTENSION}")
    (dest / ".installed_at").write_text(str(int(time.time())), encoding="utf-8")
    return dest


def list_installed(library_dir: Path) -> list[dict]:
    packages = []
    if not library_dir.exists():
        return packages
    for item in sorted(library_dir.iterdir()):
        manifest_path = item / "manifest.json"
        if item.is_dir() and manifest_path.exists():
            try:
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                manifest["_path"] = str(item)
                manifest["_package_file"] = str(next(item.glob(f"*{PACKAGE_EXTENSION}"), ""))
                packages.append(manifest)
            except Exception:
                continue
    return packages


def search_installed(package_dir: Path, query: str, limit: int = 20) -> list[SearchHit]:
    db = package_dir / "search.sqlite"
    if not db.exists():
        return []
    normalized = normalize_fa(query)
    hits: list[SearchHit] = []
    con = sqlite3.connect(db)
    try:
        try:
            rows = con.execute(
                "SELECT title, path, snippet(pages_fts, 1, '[', ']', '...', 12) FROM pages_fts WHERE pages_fts MATCH ? LIMIT ?",
                (normalized, limit),
            ).fetchall()
        except sqlite3.OperationalError:
            like = f"%{normalized}%"
            rows = con.execute(
                "SELECT title, path, substr(body, 1, 180) FROM pages_fts WHERE body LIKE ? LIMIT ?",
                (like, limit),
            ).fetchall()
        for title, path, snippet in rows:
            hits.append(SearchHit(title=title, path=path, snippet=snippet))
    finally:
        con.close()
    return hits


def delete_installed(package_dir: Path, library_dir: Path) -> None:
    package_dir = package_dir.resolve()
    library_dir = library_dir.resolve()
    if not package_dir.exists():
        return
    try:
        package_dir.relative_to(library_dir)
    except ValueError as exc:
        raise ValueError("Package directory is outside the AZSOS library") from exc
    if not (package_dir / "manifest.json").exists():
        raise ValueError("Selected folder does not look like an installed AZSOS package")
    shutil.rmtree(package_dir)
