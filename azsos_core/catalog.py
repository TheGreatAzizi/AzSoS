from __future__ import annotations

import hashlib
import html
import json
import os
import re
import shutil
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from . import PACKAGE_EXTENSION
from .package import sha256_file, verify_package

DEFAULT_SOURCE_URL = "https://github.com/TheGreatAzizi/AzSoS/tree/IR-packages"
OLD_DEFAULT_SOURCE_URL = "https://github.com/TheGreatAzizi/AzSoS-/tree/IR-packages"
DEFAULT_SOURCE_NAME = "AZSOS IR packages"
DEFAULT_UPDATE_SOURCE_URL = "https://github.com/TheGreatAzizi/AzSoS/tree/UPDATE"
DEFAULT_UPDATE_SOURCE_NAME = "AZSOS app updates"
USER_AGENT = "AZSOS/0.3.3 (+https://github.com/TheGreatAzizi/AzSoS)"
TIMEOUT_SECONDS = 30
MAX_DOWNLOAD_BYTES = 512 * 1024 * 1024


class CatalogError(RuntimeError):
    """User-readable catalog/discovery error."""


def _github_token() -> str | None:
    token = os.environ.get("AZSOS_GITHUB_TOKEN") or os.environ.get("GITHUB_TOKEN")
    return token.strip() if token and token.strip() else None


@dataclass
class RemotePackage:
    name: str
    download_url: str
    source: str
    size_bytes: int | None = None
    page_url: str | None = None
    branch: str | None = None
    path: str | None = None
    title: str | None = None
    package_id: str | None = None
    version: str | None = None
    publisher: str | None = None
    fingerprint: str | None = None
    sha256: str | None = None

    def display(self) -> str:
        size = format_bytes(self.size_bytes) if self.size_bytes is not None else "unknown size"
        label = self.title or self.name
        version = f" v{self.version}" if self.version else ""
        publisher = f" - {self.publisher}" if self.publisher else ""
        return f"{label}{version}  -  {size}  -  {self.source}{publisher}"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


UPDATE_ASSET_EXTENSIONS = (".exe", ".msi", ".zip")


@dataclass
class RemoteUpdate:
    name: str
    download_url: str
    source: str
    size_bytes: int | None = None
    page_url: str | None = None
    branch: str | None = None
    path: str | None = None
    version: str | None = None
    sha256: str | None = None
    notes: str | None = None

    def display(self) -> str:
        size = format_bytes(self.size_bytes) if self.size_bytes is not None else "unknown size"
        version = f" v{self.version}" if self.version else ""
        return f"{self.name}{version}  -  {size}  -  {self.source}"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SourceConfig:
    name: str
    url: str
    enabled: bool = True


def format_bytes(size: int | None) -> str:
    if size is None:
        return "unknown size"
    units = ["B", "KB", "MB", "GB"]
    value = float(size)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            if unit == "B":
                return f"{int(value)} {unit}"
            return f"{value:.1f} {unit}"
        value /= 1024
    return f"{size} B"


def is_package_url(url: str) -> bool:
    parsed = urllib.parse.urlparse(url.strip())
    path = urllib.parse.unquote(parsed.path).lower()
    return path.split("?")[0].endswith(PACKAGE_EXTENSION)


def _request(url: str, *, accept: str | None = None, github_api: bool = False) -> urllib.request.Request:
    headers = {"User-Agent": USER_AGENT}
    if accept:
        headers["Accept"] = accept
    token = _github_token()
    if github_api and token:
        headers["Authorization"] = f"Bearer {token}"
    return urllib.request.Request(url, headers=headers)


def _friendly_http_error(exc: urllib.error.HTTPError, url: str) -> CatalogError:
    try:
        body = exc.read().decode("utf-8", errors="replace")[:500]
    except Exception:
        body = ""
    message = f"HTTP Error {exc.code}"
    if exc.code == 403 and "rate limit" in body.lower():
        message = (
            "GitHub API rate limit exceeded. AZSOS will try non-API fallbacks when possible. "
            "For the most reliable publishing, upload a packages.index.json file next to your .azsos files, "
            "or set AZSOS_GITHUB_TOKEN/GITHUB_TOKEN before running the app."
        )
    elif exc.code == 404:
        message = "Not found"
    return CatalogError(f"{message} ({url})")


def _http_json(url: str, *, github_api: bool = False) -> Any:
    req = _request(url, accept="application/vnd.github+json, application/json", github_api=github_api)
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise _friendly_http_error(exc, url) from exc


def _http_text(url: str, *, github_api: bool = False) -> str:
    req = _request(url, github_api=github_api)
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as response:
            return response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        raise _friendly_http_error(exc, url) from exc


def _github_parts(url: str) -> tuple[str, str, str | None, str | None] | None:
    parsed = urllib.parse.urlparse(url.strip())
    if parsed.netloc.lower() not in {"github.com", "www.github.com"}:
        return None
    parts = [urllib.parse.unquote(part) for part in parsed.path.strip("/").split("/") if part]
    if len(parts) < 2:
        return None
    owner, repo = parts[0], parts[1]
    branch = None
    subpath = ""
    if len(parts) >= 4 and parts[2] in {"tree", "blob"}:
        branch = parts[3]
        if len(parts) > 4:
            subpath = "/".join(parts[4:]).strip("/")
    return owner, repo, branch, subpath


def _raw_github_url(owner: str, repo: str, branch: str, path: str) -> str:
    quoted_path = urllib.parse.quote(path, safe="/")
    quoted_branch = urllib.parse.quote(branch, safe="")
    return f"https://raw.githubusercontent.com/{owner}/{repo}/{quoted_branch}/{quoted_path}"


def _github_page_url(owner: str, repo: str, branch: str, path: str) -> str:
    return f"https://github.com/{owner}/{repo}/blob/{urllib.parse.quote(branch, safe='')}/{urllib.parse.quote(path, safe='/')}"


def _github_tree_page_url(owner: str, repo: str, branch: str, path: str = "") -> str:
    base = f"https://github.com/{owner}/{repo}/tree/{urllib.parse.quote(branch, safe='')}"
    return base if not path else f"{base}/{urllib.parse.quote(path.strip('/'), safe='/')}"


def default_sources() -> list[SourceConfig]:
    return [SourceConfig(name=DEFAULT_SOURCE_NAME, url=DEFAULT_SOURCE_URL, enabled=True)]


def load_sources(config: dict[str, Any]) -> list[SourceConfig]:
    raw_sources = config.get("sources")
    if isinstance(raw_sources, list):
        sources: list[SourceConfig] = []
        for item in raw_sources:
            if not isinstance(item, dict):
                continue
            url = str(item.get("url", "")).strip()
            if url == OLD_DEFAULT_SOURCE_URL:
                url = DEFAULT_SOURCE_URL
            if not url:
                continue
            name = str(item.get("name") or url)
            sources.append(SourceConfig(name=name, url=url, enabled=bool(item.get("enabled", True))))
        if sources:
            return sources
    legacy = str(config.get("content_source_url", DEFAULT_SOURCE_URL)).strip() or DEFAULT_SOURCE_URL
    if legacy == OLD_DEFAULT_SOURCE_URL:
        legacy = DEFAULT_SOURCE_URL
    return [SourceConfig(name=DEFAULT_SOURCE_NAME if legacy == DEFAULT_SOURCE_URL else "Custom source", url=legacy)]


def dump_sources(sources: list[SourceConfig]) -> list[dict[str, Any]]:
    return [asdict(source) for source in sources]


def discover_packages(source_url: str = DEFAULT_SOURCE_URL, *, include_releases: bool = True) -> list[RemotePackage]:
    source_url = source_url.strip() or DEFAULT_SOURCE_URL
    parsed = urllib.parse.urlparse(source_url)
    lower = source_url.lower()

    if is_package_url(source_url):
        return [discover_direct_package(source_url)]

    if parsed.scheme == "file":
        path = Path(urllib.parse.unquote(parsed.path))
        if path.is_dir():
            return discover_local_folder(path)
        if path.suffix.lower() == ".json":
            return discover_from_registry(source_url)
        if path.suffix.lower() == PACKAGE_EXTENSION:
            return [discover_direct_package(path.as_uri())]

    local_path = Path(source_url)
    if local_path.exists():
        local_path = local_path.resolve()
        if local_path.is_dir():
            return discover_local_folder(local_path)
        if local_path.suffix.lower() == ".json":
            return discover_from_registry(str(local_path))
        if local_path.suffix.lower() == PACKAGE_EXTENSION:
            return [RemotePackage(name=local_path.name, download_url=local_path.as_uri(), source="local-file", size_bytes=local_path.stat().st_size)]

    if lower.endswith(".json"):
        return discover_from_registry(source_url)

    github = _github_parts(source_url)
    if github:
        owner, repo, branch, subpath = github
        packages: list[RemotePackage] = []
        tree_error: Exception | None = None
        if branch:
            try:
                packages.extend(discover_github_tree(owner, repo, branch, subpath or ""))
            except Exception as exc:
                tree_error = exc
        if include_releases:
            try:
                packages.extend(discover_github_releases(owner, repo))
            except Exception:
                # Release discovery uses the GitHub API. It is useful, but it must not make
                # a branch/source fail when the user has packages in the tree or a registry.
                pass
        packages = dedupe_packages(packages)
        if packages:
            return packages
        if tree_error:
            raise tree_error
        return packages

    raise ValueError("Unsupported content source. Use a GitHub repository/tree URL, a direct .azsos URL, a local folder, or a packages.index.json URL.")


def discover_direct_package(url: str) -> RemotePackage:
    parsed = urllib.parse.urlparse(url)
    name = Path(urllib.parse.unquote(parsed.path)).name or "package.azsos"
    source = "direct-url" if parsed.scheme in {"http", "https"} else "local-file"
    size = None
    download_url = url
    page_url = url
    github = _github_parts(url)
    if github and "/blob/" in parsed.path:
        owner, repo, branch, subpath = github
        if branch and subpath:
            download_url = _raw_github_url(owner, repo, branch, subpath)
            page_url = url
            source = f"github:{branch}"
            name = Path(subpath).name
    if parsed.scheme == "file":
        p = Path(urllib.parse.unquote(parsed.path))
        if p.exists():
            size = p.stat().st_size
    return RemotePackage(name=name, download_url=download_url, source=source, size_bytes=size, page_url=page_url)


def _resolve_registry_download_url(download_url: str, registry_url: str) -> str:
    # Registry authors can use absolute URLs or relative paths such as ./first-aid.azsos.
    parsed = urllib.parse.urlparse(download_url)
    if parsed.scheme in {"http", "https", "file"} or re.match(r"^[A-Za-z]:\\", download_url):
        return download_url
    if registry_url.startswith("file://"):
        base = Path(urllib.parse.unquote(urllib.parse.urlparse(registry_url).path)).parent
        return (base / download_url).resolve().as_uri()
    if Path(registry_url).exists():
        return (Path(registry_url).resolve().parent / download_url).resolve().as_uri()
    return urllib.parse.urljoin(registry_url, download_url)


def discover_from_registry(url: str) -> list[RemotePackage]:
    if url.startswith("file://"):
        data = json.loads(Path(urllib.parse.unquote(urllib.parse.urlparse(url).path)).read_text(encoding="utf-8"))
    elif re.match(r"^[A-Za-z]:\\", url) or Path(url).exists():
        data = json.loads(Path(url).read_text(encoding="utf-8"))
    else:
        data = json.loads(_http_text(url))
    items = data.get("packages", data if isinstance(data, list) else [])
    packages: list[RemotePackage] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        raw_url = item.get("download_url") or item.get("url")
        if not raw_url:
            continue
        download_url = _resolve_registry_download_url(str(raw_url), url)
        if not urllib.parse.urlparse(download_url).path.lower().split("?")[0].endswith(PACKAGE_EXTENSION):
            continue
        name = item.get("name") or Path(urllib.parse.urlparse(str(download_url)).path).name or "package.azsos"
        publisher = item.get("publisher")
        if isinstance(publisher, dict):
            publisher_name = publisher.get("name")
            fingerprint = publisher.get("fingerprint")
        else:
            publisher_name = publisher
            fingerprint = item.get("fingerprint")
        packages.append(
            RemotePackage(
                name=str(name),
                download_url=str(download_url),
                source=str(item.get("source", "registry")),
                size_bytes=item.get("size_bytes"),
                page_url=item.get("page_url") or str(download_url),
                title=item.get("title"),
                package_id=item.get("id") or item.get("package_id"),
                version=item.get("version"),
                publisher=str(publisher_name) if publisher_name else None,
                fingerprint=str(fingerprint) if fingerprint else None,
                sha256=item.get("sha256"),
            )
        )
    return dedupe_packages(packages)


def discover_local_folder(folder: Path) -> list[RemotePackage]:
    folder = folder.resolve()
    packages: list[RemotePackage] = []
    for path in sorted(folder.rglob(f"*{PACKAGE_EXTENSION}")):
        path = path.resolve()
        rel = path.relative_to(folder).as_posix()
        packages.append(RemotePackage(name=path.name, download_url=path.as_uri(), source="local-folder", size_bytes=path.stat().st_size, path=rel))
    return dedupe_packages(packages)


def _try_github_registry(owner: str, repo: str, branch: str, subpath: str = "") -> list[RemotePackage]:
    prefix = subpath.strip("/")
    candidate_paths = []
    if prefix:
        candidate_paths.extend([
            f"{prefix}/packages.index.json",
            f"{prefix}/registry/packages.index.json",
            f"{prefix}/index.json",
        ])
    candidate_paths.extend(["packages.index.json", "registry/packages.index.json", "index.json"])
    seen: set[str] = set()
    for path in candidate_paths:
        if path in seen:
            continue
        seen.add(path)
        registry_url = _raw_github_url(owner, repo, branch, path)
        try:
            packages = discover_from_registry(registry_url)
        except Exception:
            continue
        if packages:
            for package in packages:
                package.source = f"github-registry:{branch}"
                if not package.page_url or package.page_url == package.download_url:
                    package.page_url = _github_page_url(owner, repo, branch, path)
            return packages
    return []


def _html_discover_github_tree(owner: str, repo: str, branch: str, subpath: str = "", *, max_depth: int = 4) -> list[RemotePackage]:
    visited: set[str] = set()
    packages: list[RemotePackage] = []

    def parse_page(path: str, depth: int) -> None:
        path = path.strip("/")
        if path in visited or depth > max_depth:
            return
        visited.add(path)
        page_url = _github_tree_page_url(owner, repo, branch, path)
        text = _http_text(page_url)
        hrefs = set(html.unescape(match.group(1)) for match in re.finditer(r'href=["\']([^"\']+)["\']', text))
        tree_paths: set[str] = set()
        for href in hrefs:
            href_path = urllib.parse.unquote(urllib.parse.urlparse(href).path)
            parts = [part for part in href_path.strip("/").split("/") if part]
            if len(parts) < 5:
                continue
            if parts[0].lower() != owner.lower() or parts[1].lower() != repo.lower():
                continue
            kind = parts[2]
            href_branch = parts[3]
            file_path = "/".join(parts[4:]).strip("/")
            if href_branch != branch:
                continue
            if kind == "blob" and file_path.lower().endswith(PACKAGE_EXTENSION):
                packages.append(
                    RemotePackage(
                        name=Path(file_path).name,
                        download_url=_raw_github_url(owner, repo, branch, file_path),
                        source=f"github-html:{branch}",
                        page_url=_github_page_url(owner, repo, branch, file_path),
                        branch=branch,
                        path=file_path,
                    )
                )
            elif kind == "tree" and file_path and (not subpath.strip("/") or file_path.startswith(subpath.strip("/")) or subpath.strip("/").startswith(file_path)):
                tree_paths.add(file_path)
        for tree_path in sorted(tree_paths):
            parse_page(tree_path, depth + 1)

    parse_page(subpath or "", 0)
    return dedupe_packages(packages)


def discover_github_tree(owner: str, repo: str, branch: str, subpath: str = "") -> list[RemotePackage]:
    # Fast, low-risk path: a registry JSON hosted in the branch. This avoids GitHub API rate limits.
    registry_packages = _try_github_registry(owner, repo, branch, subpath)
    if registry_packages:
        return registry_packages

    # Non-API HTML fallback. It is not as rich as the API, but it works well for public branches
    # and avoids the unauthenticated GitHub API rate limit that users frequently hit.
    html_error: Exception | None = None
    try:
        packages = _html_discover_github_tree(owner, repo, branch, subpath)
        if packages:
            return packages
    except Exception as exc:
        html_error = exc

    # API fallback. If users set AZSOS_GITHUB_TOKEN/GITHUB_TOKEN, this becomes much more reliable.
    api = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{urllib.parse.quote(branch, safe='')}?recursive=1"
    try:
        data = _http_json(api, github_api=True)
    except Exception as exc:
        if html_error:
            raise CatalogError(f"Could not scan GitHub tree. HTML fallback failed: {html_error}; API fallback failed: {exc}") from exc
        raise
    tree = data.get("tree", [])
    packages: list[RemotePackage] = []
    prefix = subpath.strip("/")
    for item in tree:
        if item.get("type") != "blob":
            continue
        path = str(item.get("path", ""))
        if prefix and not (path == prefix or path.startswith(prefix + "/")):
            continue
        if not path.lower().endswith(PACKAGE_EXTENSION):
            continue
        packages.append(
            RemotePackage(
                name=Path(path).name,
                download_url=_raw_github_url(owner, repo, branch, path),
                source=f"github-api:{branch}",
                size_bytes=item.get("size"),
                page_url=_github_page_url(owner, repo, branch, path),
                branch=branch,
                path=path,
            )
        )
    return packages


def discover_github_releases(owner: str, repo: str) -> list[RemotePackage]:
    api = f"https://api.github.com/repos/{owner}/{repo}/releases"
    data = _http_json(api, github_api=True)
    packages: list[RemotePackage] = []
    for release in data if isinstance(data, list) else []:
        release_name = release.get("name") or release.get("tag_name") or "release"
        for asset in release.get("assets", []) or []:
            name = str(asset.get("name", ""))
            if not name.lower().endswith(PACKAGE_EXTENSION):
                continue
            packages.append(
                RemotePackage(
                    name=name,
                    download_url=str(asset.get("browser_download_url")),
                    source=f"release:{release_name}",
                    size_bytes=asset.get("size"),
                    page_url=asset.get("html_url") or release.get("html_url"),
                )
            )
    return packages


def dedupe_packages(packages: list[RemotePackage]) -> list[RemotePackage]:
    seen: set[str] = set()
    unique: list[RemotePackage] = []
    for package in packages:
        key = package.download_url
        if key in seen:
            continue
        seen.add(key)
        unique.append(package)
    unique.sort(key=lambda item: ((item.title or item.name).lower(), item.source.lower()))
    return unique


def download_package(remote: RemotePackage, dest_dir: Path | None = None, *, verify_hash: bool = True) -> Path:
    if dest_dir is None:
        dest_dir = Path(tempfile.gettempdir()) / "azsos-downloads"
    dest_dir.mkdir(parents=True, exist_ok=True)
    safe_name = re.sub(r"[^A-Za-z0-9_.-]+", "-", remote.name).strip(".-") or "package.azsos"
    if not safe_name.lower().endswith(PACKAGE_EXTENSION):
        safe_name += PACKAGE_EXTENSION
    dest = dest_dir / safe_name

    parsed = urllib.parse.urlparse(remote.download_url)
    if parsed.scheme == "file":
        src = Path(urllib.parse.unquote(parsed.path))
        if src.resolve() != dest.resolve():
            shutil.copy2(src, dest)
        else:
            dest = src
    else:
        req = _request(remote.download_url)
        with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as response, dest.open("wb") as out:
            total = 0
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                total += len(chunk)
                if total > MAX_DOWNLOAD_BYTES:
                    raise ValueError("Remote package is too large for the safety limit")
                out.write(chunk)

    if verify_hash and remote.sha256:
        actual = sha256_file(dest)
        expected = str(remote.sha256).lower().replace("sha256-", "")
        if actual.lower() != expected:
            dest.unlink(missing_ok=True)
            raise ValueError("Downloaded package SHA-256 does not match the registry")
    return dest


def inspect_remote_package(remote: RemotePackage) -> tuple[RemotePackage, Path]:
    downloaded = download_package(remote)
    result = verify_package(downloaded)
    if not result.ok or not result.manifest:
        raise ValueError("Remote file is not a valid AZSOS package: " + "; ".join(result.errors))
    manifest = result.manifest
    publisher = manifest.get("publisher", {})
    enriched = RemotePackage(
        name=remote.name,
        download_url=remote.download_url,
        source=remote.source,
        size_bytes=remote.size_bytes or downloaded.stat().st_size,
        page_url=remote.page_url,
        branch=remote.branch,
        path=remote.path,
        title=manifest.get("title"),
        package_id=manifest.get("id"),
        version=manifest.get("version"),
        publisher=publisher.get("name"),
        fingerprint=publisher.get("fingerprint"),
        sha256=remote.sha256 or sha256_file(downloaded),
    )
    return enriched, downloaded


def is_update_asset_url(url: str) -> bool:
    parsed = urllib.parse.urlparse(url.strip())
    path = urllib.parse.unquote(parsed.path).lower().split("?")[0]
    return path.endswith(UPDATE_ASSET_EXTENSIONS)


def discover_updates(source_url: str = DEFAULT_UPDATE_SOURCE_URL, *, include_releases: bool = True) -> list[RemoteUpdate]:
    """Discover app update installers/archives.

    Preferred publishing model:
      UPDATE branch
        update.index.json
        releases/AZSOS-Desktop-vX.Y.Z.exe

    GitHub Releases are also scanned as a fallback, but GitHub releases are repository-wide
    rather than branch-specific. The UPDATE branch registry keeps this deterministic.
    """
    source_url = source_url.strip() or DEFAULT_UPDATE_SOURCE_URL
    parsed = urllib.parse.urlparse(source_url)
    lower = source_url.lower()

    if is_update_asset_url(source_url):
        return [discover_direct_update(source_url)]

    if parsed.scheme == "file":
        path = Path(urllib.parse.unquote(parsed.path))
        if path.is_dir():
            return discover_local_updates(path)
        if path.suffix.lower() == ".json":
            return discover_updates_from_registry(source_url)
        if is_update_asset_url(path.as_uri()):
            return [discover_direct_update(path.as_uri())]

    local_path = Path(source_url)
    if local_path.exists():
        local_path = local_path.resolve()
        if local_path.is_dir():
            return discover_local_updates(local_path)
        if local_path.suffix.lower() == ".json":
            return discover_updates_from_registry(str(local_path))
        if local_path.suffix.lower() in UPDATE_ASSET_EXTENSIONS:
            return [RemoteUpdate(name=local_path.name, download_url=local_path.as_uri(), source="local-file", size_bytes=local_path.stat().st_size)]

    if lower.endswith(".json"):
        return discover_updates_from_registry(source_url)

    github = _github_parts(source_url)
    if github:
        owner, repo, branch, subpath = github
        updates: list[RemoteUpdate] = []
        tree_error: Exception | None = None
        if branch:
            try:
                updates.extend(discover_github_update_tree(owner, repo, branch, subpath or ""))
            except Exception as exc:
                tree_error = exc
        if include_releases:
            try:
                updates.extend(discover_github_update_releases(owner, repo))
            except Exception:
                pass
        updates = dedupe_updates(updates)
        if updates:
            return updates
        if tree_error:
            raise tree_error
        return updates

    raise ValueError("Unsupported update source. Use a GitHub UPDATE branch/tree URL, a direct installer/zip URL, a local folder, or update.index.json.")


def discover_direct_update(url: str) -> RemoteUpdate:
    parsed = urllib.parse.urlparse(url)
    name = Path(urllib.parse.unquote(parsed.path)).name or "azsos-update.zip"
    source = "direct-url" if parsed.scheme in {"http", "https"} else "local-file"
    size = None
    download_url = url
    page_url = url
    github = _github_parts(url)
    if github and "/blob/" in parsed.path:
        owner, repo, branch, subpath = github
        if branch and subpath:
            download_url = _raw_github_url(owner, repo, branch, subpath)
            page_url = url
            source = f"github-update:{branch}"
            name = Path(subpath).name
    if parsed.scheme == "file":
        p = Path(urllib.parse.unquote(parsed.path))
        if p.exists():
            size = p.stat().st_size
    return RemoteUpdate(name=name, download_url=download_url, source=source, size_bytes=size, page_url=page_url)


def discover_updates_from_registry(url: str) -> list[RemoteUpdate]:
    if url.startswith("file://"):
        data = json.loads(Path(urllib.parse.unquote(urllib.parse.urlparse(url).path)).read_text(encoding="utf-8"))
    elif re.match(r"^[A-Za-z]:\\", url) or Path(url).exists():
        data = json.loads(Path(url).read_text(encoding="utf-8"))
    else:
        data = json.loads(_http_text(url))
    items = data.get("updates", data.get("assets", data if isinstance(data, list) else []))
    updates: list[RemoteUpdate] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        raw_url = item.get("download_url") or item.get("url")
        if not raw_url:
            continue
        download_url = _resolve_registry_download_url(str(raw_url), url)
        if not is_update_asset_url(download_url):
            continue
        name = item.get("name") or Path(urllib.parse.urlparse(str(download_url)).path).name or "azsos-update.zip"
        updates.append(
            RemoteUpdate(
                name=str(name),
                download_url=str(download_url),
                source=str(item.get("source", "update-registry")),
                size_bytes=item.get("size_bytes"),
                page_url=item.get("page_url") or str(download_url),
                version=item.get("version"),
                sha256=item.get("sha256"),
                notes=item.get("notes"),
            )
        )
    return dedupe_updates(updates)


def discover_local_updates(folder: Path) -> list[RemoteUpdate]:
    folder = folder.resolve()
    updates: list[RemoteUpdate] = []
    for suffix in UPDATE_ASSET_EXTENSIONS:
        for path in sorted(folder.rglob(f"*{suffix}")):
            path = path.resolve()
            rel = path.relative_to(folder).as_posix()
            updates.append(RemoteUpdate(name=path.name, download_url=path.as_uri(), source="local-update-folder", size_bytes=path.stat().st_size, path=rel))
    return dedupe_updates(updates)


def _try_github_update_registry(owner: str, repo: str, branch: str, subpath: str = "") -> list[RemoteUpdate]:
    prefix = subpath.strip("/")
    candidate_paths: list[str] = []
    if prefix:
        candidate_paths.extend([
            f"{prefix}/update.index.json",
            f"{prefix}/updates.index.json",
            f"{prefix}/releases.index.json",
            f"{prefix}/index.json",
        ])
    candidate_paths.extend(["update.index.json", "updates.index.json", "releases.index.json", "index.json"])
    seen: set[str] = set()
    for path in candidate_paths:
        if path in seen:
            continue
        seen.add(path)
        registry_url = _raw_github_url(owner, repo, branch, path)
        try:
            updates = discover_updates_from_registry(registry_url)
        except Exception:
            continue
        if updates:
            for update in updates:
                update.source = f"github-update-registry:{branch}"
                if not update.page_url or update.page_url == update.download_url:
                    update.page_url = _github_page_url(owner, repo, branch, path)
            return updates
    return []


def _html_discover_github_updates(owner: str, repo: str, branch: str, subpath: str = "", *, max_depth: int = 3) -> list[RemoteUpdate]:
    visited: set[str] = set()
    updates: list[RemoteUpdate] = []

    def parse_page(path: str, depth: int) -> None:
        path = path.strip("/")
        if path in visited or depth > max_depth:
            return
        visited.add(path)
        page_url = _github_tree_page_url(owner, repo, branch, path)
        text = _http_text(page_url)
        hrefs = set(html.unescape(match.group(1)) for match in re.finditer(r'href=["\']([^"\']+)["\']', text))
        tree_paths: set[str] = set()
        for href in hrefs:
            href_path = urllib.parse.unquote(urllib.parse.urlparse(href).path)
            parts = [part for part in href_path.strip("/").split("/") if part]
            if len(parts) < 5:
                continue
            if parts[0].lower() != owner.lower() or parts[1].lower() != repo.lower():
                continue
            kind = parts[2]
            href_branch = parts[3]
            file_path = "/".join(parts[4:]).strip("/")
            if href_branch != branch:
                continue
            if kind == "blob" and file_path.lower().endswith(UPDATE_ASSET_EXTENSIONS):
                updates.append(
                    RemoteUpdate(
                        name=Path(file_path).name,
                        download_url=_raw_github_url(owner, repo, branch, file_path),
                        source=f"github-update-html:{branch}",
                        page_url=_github_page_url(owner, repo, branch, file_path),
                        branch=branch,
                        path=file_path,
                    )
                )
            elif kind == "tree" and file_path and (not subpath.strip("/") or file_path.startswith(subpath.strip("/")) or subpath.strip("/").startswith(file_path)):
                tree_paths.add(file_path)
        for tree_path in sorted(tree_paths):
            parse_page(tree_path, depth + 1)

    parse_page(subpath or "", 0)
    return dedupe_updates(updates)


def discover_github_update_tree(owner: str, repo: str, branch: str, subpath: str = "") -> list[RemoteUpdate]:
    registry_updates = _try_github_update_registry(owner, repo, branch, subpath)
    if registry_updates:
        return registry_updates

    html_error: Exception | None = None
    try:
        updates = _html_discover_github_updates(owner, repo, branch, subpath)
        if updates:
            return updates
    except Exception as exc:
        html_error = exc

    api = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{urllib.parse.quote(branch, safe='')}?recursive=1"
    try:
        data = _http_json(api, github_api=True)
    except Exception as exc:
        if html_error:
            raise CatalogError(f"Could not scan GitHub UPDATE branch. HTML fallback failed: {html_error}; API fallback failed: {exc}") from exc
        raise
    tree = data.get("tree", [])
    updates: list[RemoteUpdate] = []
    prefix = subpath.strip("/")
    for item in tree:
        if item.get("type") != "blob":
            continue
        path = str(item.get("path", ""))
        if prefix and not (path == prefix or path.startswith(prefix + "/")):
            continue
        if not path.lower().endswith(UPDATE_ASSET_EXTENSIONS):
            continue
        updates.append(
            RemoteUpdate(
                name=Path(path).name,
                download_url=_raw_github_url(owner, repo, branch, path),
                source=f"github-update-api:{branch}",
                size_bytes=item.get("size"),
                page_url=_github_page_url(owner, repo, branch, path),
                branch=branch,
                path=path,
            )
        )
    return updates


def discover_github_update_releases(owner: str, repo: str) -> list[RemoteUpdate]:
    api = f"https://api.github.com/repos/{owner}/{repo}/releases"
    data = _http_json(api, github_api=True)
    updates: list[RemoteUpdate] = []
    for release in data if isinstance(data, list) else []:
        release_name = release.get("name") or release.get("tag_name") or "release"
        for asset in release.get("assets", []) or []:
            name = str(asset.get("name", ""))
            if not name.lower().endswith(UPDATE_ASSET_EXTENSIONS):
                continue
            updates.append(
                RemoteUpdate(
                    name=name,
                    download_url=str(asset.get("browser_download_url")),
                    source=f"update-release:{release_name}",
                    size_bytes=asset.get("size"),
                    page_url=asset.get("html_url") or release.get("html_url"),
                    version=release.get("tag_name"),
                    notes=release.get("body"),
                )
            )
    return updates


def dedupe_updates(updates: list[RemoteUpdate]) -> list[RemoteUpdate]:
    seen: set[str] = set()
    unique: list[RemoteUpdate] = []
    for update in updates:
        key = update.download_url
        if key in seen:
            continue
        seen.add(key)
        unique.append(update)
    unique.sort(key=lambda item: (item.version or "", item.name.lower()), reverse=True)
    return unique


def download_update(update: RemoteUpdate, dest_dir: Path | None = None, *, verify_hash: bool = True) -> Path:
    if dest_dir is None:
        dest_dir = Path.home() / "AZSOS" / "updates"
    dest_dir.mkdir(parents=True, exist_ok=True)
    safe_name = re.sub(r"[^A-Za-z0-9_.-]+", "-", update.name).strip(".-") or "azsos-update.zip"
    dest = dest_dir / safe_name
    parsed = urllib.parse.urlparse(update.download_url)
    if parsed.scheme == "file":
        src = Path(urllib.parse.unquote(parsed.path))
        if src.resolve() != dest.resolve():
            shutil.copy2(src, dest)
        else:
            dest = src
    else:
        req = _request(update.download_url)
        with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as response, dest.open("wb") as out:
            total = 0
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                total += len(chunk)
                if total > MAX_DOWNLOAD_BYTES:
                    raise ValueError("Remote update file is too large for the safety limit")
                out.write(chunk)
    if verify_hash and update.sha256:
        actual = sha256_file(dest)
        expected = str(update.sha256).lower().replace("sha256-", "")
        if actual.lower() != expected:
            dest.unlink(missing_ok=True)
            raise ValueError("Downloaded update SHA-256 does not match the registry")
    return dest


def build_registry(packages_dir: Path, base_url: str, out_path: Path, *, source_name: str = "azsos-registry") -> Path:
    packages_dir = packages_dir.resolve()
    base_url = base_url.rstrip("/")
    items: list[dict[str, Any]] = []
    for package_path in sorted(packages_dir.rglob(f"*{PACKAGE_EXTENSION}")):
        result = verify_package(package_path)
        if not result.ok or not result.manifest:
            continue
        manifest = result.manifest
        publisher = manifest.get("publisher", {})
        rel = package_path.relative_to(packages_dir).as_posix()
        items.append(
            {
                "name": package_path.name,
                "title": manifest.get("title"),
                "id": manifest.get("id"),
                "version": manifest.get("version"),
                "language": manifest.get("language"),
                "publisher": {
                    "name": publisher.get("name"),
                    "fingerprint": publisher.get("fingerprint"),
                },
                "size_bytes": package_path.stat().st_size,
                "sha256": sha256_file(package_path),
                "download_url": f"{base_url}/{urllib.parse.quote(rel, safe='/')}",
                "source": source_name,
            }
        )
    registry = {
        "format": "azsos.registry.v1",
        "source": source_name,
        "packages": items,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(registry, ensure_ascii=False, indent=2), encoding="utf-8")
    return out_path
