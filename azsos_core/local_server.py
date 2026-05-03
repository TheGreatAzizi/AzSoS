from __future__ import annotations

import html
import json
import socket
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import quote

from .package import list_installed, sha256_file


def get_lan_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


class AZSOSShareHandler(SimpleHTTPRequestHandler):
    library_dir: Path

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        return

    def do_GET(self) -> None:  # noqa: N802
        if self.path in {"/", "/index.html"}:
            self._send_index()
            return
        if self.path in {"/packages.json", "/registry.json"}:
            self._send_registry()
            return
        if self.path.startswith("/download/"):
            filename = self.path.split("/download/", 1)[1]
            for manifest in list_installed(self.library_dir):
                pkg_file = Path(manifest.get("_package_file", ""))
                if pkg_file.exists() and quote(pkg_file.name) == filename:
                    self._send_file(pkg_file)
                    return
            self.send_error(404, "Package not found")
            return
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"OK")
            return
        self.send_error(404)

    def _package_rows(self) -> tuple[list[str], list[dict]]:
        rows = []
        registry_items = []
        for manifest in list_installed(self.library_dir):
            pkg_file = Path(manifest.get("_package_file", ""))
            if not pkg_file.exists():
                continue
            title = html.escape(str(manifest.get("title", pkg_file.name)))
            version = html.escape(str(manifest.get("version", "")))
            publisher = html.escape(str(manifest.get("publisher", {}).get("name", "unknown")))
            fingerprint = html.escape(str(manifest.get("publisher", {}).get("fingerprint", "")))
            link = f"/download/{quote(pkg_file.name)}"
            rows.append(
                f"<li><a href='{link}'>{title}</a><br><small>version {version} - {publisher}<br>{fingerprint}</small></li>"
            )
            registry_items.append(
                {
                    "name": pkg_file.name,
                    "title": manifest.get("title"),
                    "id": manifest.get("id"),
                    "version": manifest.get("version"),
                    "publisher": {
                        "name": manifest.get("publisher", {}).get("name"),
                        "fingerprint": manifest.get("publisher", {}).get("fingerprint"),
                    },
                    "size_bytes": pkg_file.stat().st_size,
                    "sha256": sha256_file(pkg_file),
                    "download_url": link,
                }
            )
        return rows, registry_items

    def _send_index(self) -> None:
        rows, _ = self._package_rows()
        items = "\n".join(rows) or "<li>No packages installed.</li>"
        page = f"""<!doctype html>
<html lang=\"en\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
<title>AZSOS Share</title>
<style>body{{font-family:system-ui,Segoe UI,Tahoma,Arial,sans-serif;max-width:760px;margin:32px auto;padding:0 20px;line-height:1.6}}li{{margin:14px 0}}code{{background:#eee;padding:2px 4px;border-radius:4px}}</style>
</head><body><h1>AZSOS local share</h1><p>Download an offline emergency package:</p><ul>{items}</ul><p><a href=\"/packages.json\">packages.json</a></p></body></html>"""
        encoded = page.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def _send_registry(self) -> None:
        _, items = self._package_rows()
        host = self.headers.get("Host", "localhost")
        for item in items:
            item["download_url"] = f"http://{host}{item['download_url']}"
        payload = json.dumps({"format": "azsos.registry.v1", "source": "azsos-local-share", "packages": items}, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _send_file(self, path: Path) -> None:
        data = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "application/vnd.azsos.package")
        self.send_header("Content-Disposition", f"attachment; filename=\"{path.name}\"")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


class ShareServer:
    def __init__(self, library_dir: Path, host: str = "0.0.0.0", port: int = 8765):
        self.library_dir = library_dir
        self.host = host
        self.port = port
        self.httpd: ThreadingHTTPServer | None = None
        self.thread: threading.Thread | None = None

    def start(self) -> str:
        handler = type("BoundAZSOSShareHandler", (AZSOSShareHandler,), {"library_dir": self.library_dir})
        self.httpd = ThreadingHTTPServer((self.host, self.port), handler)
        self.port = self.httpd.server_address[1]
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()
        return f"http://{get_lan_ip()}:{self.port}/"

    def stop(self) -> None:
        if self.httpd:
            self.httpd.shutdown()
            self.httpd.server_close()
            self.httpd = None
        self.thread = None
