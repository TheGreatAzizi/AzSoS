from __future__ import annotations

import json
import re
import shutil
import tempfile
import threading
import webbrowser
from pathlib import Path
from tkinter import BOTH, END, LEFT, RIGHT, X, filedialog, messagebox, simpledialog, ttk
import tkinter as tk

from azsos_core.catalog import (
    DEFAULT_SOURCE_NAME,
    DEFAULT_SOURCE_URL,
    DEFAULT_UPDATE_SOURCE_URL,
    RemotePackage,
    RemoteUpdate,
    SourceConfig,
    discover_packages,
    discover_updates,
    download_package,
    download_update,
    dump_sources,
    format_bytes,
    inspect_remote_package,
    load_sources,
)
from azsos_core.local_server import ShareServer
from azsos_core.manual import DOC_TOPICS, manual_as_markdown
from azsos_core.package import (
    delete_installed,
    install_package,
    list_installed,
    search_installed,
    verify_package,
)

APP_TITLE = "AZSOS Desktop"
DEFAULT_LIBRARY = Path.home() / "AZSOS" / "library"
DEFAULT_CONFIG = Path.home() / "AZSOS" / "config.json"


class AZSOSApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1240x820")
        self.minsize(1000, 680)
        self.library_dir = DEFAULT_LIBRARY
        self.library_dir.mkdir(parents=True, exist_ok=True)
        self.config_path = DEFAULT_CONFIG
        self.config = self._load_config()
        self.sources: list[SourceConfig] = load_sources(self.config)
        self.source_index = 0
        self.trusted_publishers: dict[str, str] = self.config.get("trusted_publishers", {}) if isinstance(self.config.get("trusted_publishers"), dict) else {}
        self.packages: list[dict] = []
        self.remote_packages: list[RemotePackage] = []
        self.search_hits: list[tuple[dict, object]] = []
        self.share_server: ShareServer | None = None
        self.share_url = tk.StringVar(value="Local share is stopped")
        self.doc_topic_indices = list(range(len(DOC_TOPICS)))
        self.docs_search_query = tk.StringVar()
        self.source_name = tk.StringVar(value=self.sources[0].name if self.sources else DEFAULT_SOURCE_NAME)
        self.source_url = tk.StringVar(value=self.sources[0].url if self.sources else DEFAULT_SOURCE_URL)
        self.status = tk.StringVar(value=f"Library: {self.library_dir}")
        self.search_query = tk.StringVar()
        self._build_ui()
        self.refresh_sources_ui()
        self.refresh_packages()

    def _load_config(self) -> dict:
        try:
            if self.config_path.exists():
                data = json.loads(self.config_path.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    return data
        except Exception:
            pass
        return {"sources": [{"name": DEFAULT_SOURCE_NAME, "url": DEFAULT_SOURCE_URL, "enabled": True}], "trusted_publishers": {}}

    def _save_config(self) -> None:
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.config["sources"] = dump_sources(self.sources)
        self.config["trusted_publishers"] = self.trusted_publishers
        self.config_path.write_text(json.dumps(self.config, ensure_ascii=False, indent=2), encoding="utf-8")

    def _build_ui(self) -> None:
        root = ttk.Frame(self, padding=12)
        root.pack(fill=BOTH, expand=True)

        header = ttk.Frame(root)
        header.pack(fill=X)
        ttk.Label(header, text="AZSOS", font=("Segoe UI", 22, "bold")).pack(side=LEFT)
        ttk.Label(header, text="offline emergency content cache", foreground="#666").pack(side=LEFT, padx=(10, 0))
        ttk.Button(header, text="About", command=self.show_about).pack(side=RIGHT)
        ttk.Button(header, text="Check updates", command=self.check_for_updates).pack(side=RIGHT, padx=(0, 8))

        notebook = ttk.Notebook(root)
        notebook.pack(fill=BOTH, expand=True, pady=(12, 0))

        installed_tab = ttk.Frame(notebook, padding=10)
        catalog_tab = ttk.Frame(notebook, padding=10)
        share_tab = ttk.Frame(notebook, padding=10)
        docs_tab = ttk.Frame(notebook, padding=10)
        notebook.add(installed_tab, text="Installed")
        notebook.add(catalog_tab, text="Get content")
        notebook.add(share_tab, text="Share")
        notebook.add(docs_tab, text="Docs")

        self._build_installed_tab(installed_tab)
        self._build_catalog_tab(catalog_tab)
        self._build_share_tab(share_tab)
        self._build_docs_tab(docs_tab)

        ttk.Label(root, textvariable=self.status, foreground="#666").pack(fill=X, pady=(8, 0))

    def _build_installed_tab(self, parent: ttk.Frame) -> None:
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=X)
        ttk.Button(toolbar, text="Import .azsos", command=self.import_package).pack(side=LEFT)
        ttk.Button(toolbar, text="Verify file", command=self.verify_file).pack(side=LEFT, padx=6)
        ttk.Button(toolbar, text="Open package", command=self.open_selected).pack(side=LEFT, padx=6)
        ttk.Button(toolbar, text="Export selected", command=self.export_selected_package).pack(side=LEFT, padx=6)
        ttk.Button(toolbar, text="Delete package", command=self.delete_selected_package).pack(side=LEFT, padx=6)
        ttk.Button(toolbar, text="Trust publisher", command=self.trust_selected_publisher).pack(side=LEFT, padx=6)
        ttk.Button(toolbar, text="Refresh", command=self.refresh_packages).pack(side=LEFT, padx=6)
        ttk.Button(toolbar, text="Open library folder", command=self.open_library).pack(side=LEFT, padx=6)

        panes = ttk.PanedWindow(parent, orient=tk.HORIZONTAL)
        panes.pack(fill=BOTH, expand=True, pady=(10, 0))

        left = ttk.Frame(panes, padding=(0, 0, 8, 0))
        panes.add(left, weight=1)
        ttk.Label(left, text="Installed packages", font=("Segoe UI", 11, "bold")).pack(anchor="w")
        self.package_list = tk.Listbox(left, activestyle="dotbox", exportselection=False)
        self.package_list.pack(fill=BOTH, expand=True, pady=(6, 0))
        self.package_list.bind("<<ListboxSelect>>", lambda event: self.show_selected_details())
        self.package_list.bind("<Double-Button-1>", lambda event: self.open_selected())
        self._add_listbox_clipboard(self.package_list)

        right = ttk.Frame(panes)
        panes.add(right, weight=2)

        info = ttk.LabelFrame(right, text="Package details", padding=10)
        info.pack(fill=X)
        self.details = tk.Text(info, height=11, wrap="word", undo=False)
        self.details.pack(fill=X)
        self._make_text_readonly(self.details)
        self._add_text_clipboard_menu(self.details, writable=False)

        search = ttk.LabelFrame(right, text="Offline search", padding=10)
        search.pack(fill=BOTH, expand=True, pady=(10, 0))
        search_row = ttk.Frame(search)
        search_row.pack(fill=X)
        entry = ttk.Entry(search_row, textvariable=self.search_query)
        entry.pack(side=LEFT, fill=X, expand=True)
        entry.bind("<Return>", lambda event: self.search_selected())
        self._add_entry_clipboard_menu(entry)
        ttk.Button(search_row, text="Search selected", command=self.search_selected).pack(side=LEFT, padx=(6, 0))
        ttk.Button(search_row, text="Search all", command=self.search_all).pack(side=LEFT, padx=(6, 0))
        ttk.Button(search_row, text="Open result", command=self.open_result).pack(side=LEFT, padx=(6, 0))
        self.results = tk.Listbox(search, exportselection=False)
        self.results.pack(fill=BOTH, expand=True, pady=(8, 0))
        self.results.bind("<Double-Button-1>", lambda event: self.open_result())
        self._add_listbox_clipboard(self.results)

    def _build_catalog_tab(self, parent: ttk.Frame) -> None:
        sources = ttk.LabelFrame(parent, text="Content sources", padding=10)
        sources.pack(fill=X)

        row1 = ttk.Frame(sources)
        row1.pack(fill=X)
        ttk.Label(row1, text="Saved source:").pack(side=LEFT)
        self.source_combo = ttk.Combobox(row1, state="readonly", width=38)
        self.source_combo.pack(side=LEFT, padx=(8, 8))
        self.source_combo.bind("<<ComboboxSelected>>", lambda event: self.select_source_from_combo())
        ttk.Button(row1, text="Fetch selected", command=self.fetch_selected_source).pack(side=LEFT, padx=(0, 6))
        ttk.Button(row1, text="Fetch all", command=self.fetch_all_sources).pack(side=LEFT, padx=(0, 6))
        ttk.Button(row1, text="Open source", command=self.open_source_url).pack(side=LEFT, padx=(0, 6))
        ttk.Button(row1, text="Reset default", command=self.reset_default_sources).pack(side=LEFT)

        row2 = ttk.Frame(sources)
        row2.pack(fill=X, pady=(8, 0))
        ttk.Label(row2, text="Name:").pack(side=LEFT)
        name_entry = ttk.Entry(row2, textvariable=self.source_name, width=28)
        name_entry.pack(side=LEFT, padx=(8, 8))
        self._add_entry_clipboard_menu(name_entry)
        ttk.Label(row2, text="URL / local folder / registry:").pack(side=LEFT)
        url_entry = ttk.Entry(row2, textvariable=self.source_url)
        url_entry.pack(side=LEFT, fill=X, expand=True, padx=(8, 8))
        self._add_entry_clipboard_menu(url_entry)
        ttk.Button(row2, text="Save current", command=self.save_current_source).pack(side=LEFT, padx=(0, 6))
        ttk.Button(row2, text="Add as new", command=self.add_current_source).pack(side=LEFT, padx=(0, 6))
        ttk.Button(row2, text="Remove", command=self.remove_current_source).pack(side=LEFT)

        remote_frame = ttk.LabelFrame(parent, text="Remote packages", padding=10)
        remote_frame.pack(fill=BOTH, expand=True, pady=(10, 0))
        remote_buttons = ttk.Frame(remote_frame)
        remote_buttons.pack(fill=X)
        ttk.Button(remote_buttons, text="Install selected", command=self.install_remote_selected).pack(side=LEFT)
        ttk.Button(remote_buttons, text="Inspect selected", command=self.inspect_remote_selected).pack(side=LEFT, padx=6)
        ttk.Button(remote_buttons, text="Open package page", command=self.open_remote_page).pack(side=LEFT, padx=6)
        ttk.Button(remote_buttons, text="Copy download URL", command=self.copy_remote_url).pack(side=LEFT, padx=6)
        ttk.Button(remote_buttons, text="Clear", command=self.clear_remote_list).pack(side=LEFT, padx=6)

        self.remote_list = tk.Listbox(remote_frame, height=16, activestyle="dotbox", selectmode=tk.EXTENDED, exportselection=False)
        self.remote_list.pack(fill=BOTH, expand=True, pady=(8, 0))
        self.remote_list.bind("<Double-Button-1>", lambda event: self.install_remote_selected())
        self._add_listbox_clipboard(self.remote_list)

        hint = (
            "Supported sources: GitHub repo/tree/release, direct .azsos URL, local folder, or packages.index.json. "
            "Default: TheGreatAzizi/AzSoS branch IR-packages."
        )
        ttk.Label(parent, text=hint, foreground="#666", wraplength=1000).pack(fill=X, pady=(8, 0))

    def _build_share_tab(self, parent: ttk.Frame) -> None:
        share = ttk.LabelFrame(parent, text="Local share over Wi-Fi / hotspot", padding=10)
        share.pack(fill=X)
        ttk.Label(
            share,
            text="Start local share, connect another device to the same Wi-Fi/hotspot, then open or scan the URL. Installed packages will be downloadable as .azsos files.",
            wraplength=1000,
        ).pack(fill=X, pady=(0, 8))
        share_row = ttk.Frame(share)
        share_row.pack(fill=X)
        share_entry = ttk.Entry(share_row, textvariable=self.share_url, state="readonly")
        share_entry.pack(side=LEFT, fill=X, expand=True)
        self._add_entry_clipboard_menu(share_entry, writable=False)
        ttk.Button(share_row, text="Start", command=self.start_share).pack(side=RIGHT, padx=(6, 0))
        ttk.Button(share_row, text="Stop", command=self.stop_share).pack(side=RIGHT, padx=(6, 0))
        ttk.Button(share_row, text="QR", command=self.show_qr).pack(side=RIGHT, padx=(6, 0))
        ttk.Button(share_row, text="Copy URL", command=self.copy_share_url).pack(side=RIGHT, padx=(6, 0))

        help_box = ttk.LabelFrame(parent, text="How content reaches users", padding=10)
        help_box.pack(fill=BOTH, expand=True, pady=(10, 0))
        self.help_text = tk.Text(help_box, wrap="word", height=16)
        self.help_text.pack(fill=BOTH, expand=True)
        self.help_text.insert(
            END,
            "1. Put .azsos files on the default GitHub branch or a GitHub Release.\n"
            "2. Users click Get content -> Fetch selected -> Install selected.\n"
            "3. In an outage, one user can share installed packages with Local Share.\n"
            "4. Publishers can also distribute files through USB, LAN, Telegram, or a self-hosted Git mirror.\n"
            "5. For a curated catalog, generate packages.index.json with:\n\n"
            "   python azsos.py registry build --packages-dir ./packages --base-url <raw-download-base> --out packages.index.json\n\n"
            "Every downloaded file is verified as an AZSOS package before installation. Registry SHA-256 is checked when provided."
        )
        self._make_text_readonly(self.help_text)
        self._add_text_clipboard_menu(self.help_text, writable=False)


    def _build_docs_tab(self, parent: ttk.Frame) -> None:
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=X)
        ttk.Label(toolbar, text="Documentation", font=("Segoe UI", 12, "bold")).pack(side=LEFT)

        ttk.Label(toolbar, text="Search:").pack(side=LEFT, padx=(24, 6))
        search_entry = ttk.Entry(toolbar, textvariable=self.docs_search_query, width=34)
        search_entry.pack(side=LEFT)
        search_entry.bind("<Return>", lambda event: self.search_docs())
        self._add_entry_clipboard_menu(search_entry)
        ttk.Button(toolbar, text="Search docs", command=self.search_docs).pack(side=LEFT, padx=(6, 0))
        ttk.Button(toolbar, text="Show all", command=self.reset_docs_search).pack(side=LEFT, padx=(6, 0))
        ttk.Button(toolbar, text="Copy topic", command=self.copy_current_doc).pack(side=LEFT, padx=(6, 0))
        ttk.Button(toolbar, text="Copy Markdown", command=self.copy_current_doc_markdown).pack(side=LEFT, padx=(6, 0))
        ttk.Button(toolbar, text="Save manual", command=self.save_manual_file).pack(side=LEFT, padx=(6, 0))
        ttk.Button(toolbar, text="Open docs folder", command=self.open_docs_folder).pack(side=LEFT, padx=(6, 0))
        ttk.Button(toolbar, text="Open GitHub", command=lambda: webbrowser.open("https://github.com/TheGreatAzizi/AzSoS")).pack(side=RIGHT)

        hint = ttk.Label(
            parent,
            text=(
                "In-app Markdown manual: quick start, content sources, package creation, GitHub publishing, "
                "offline sharing, publisher trust, updates, common errors, and CLI commands."
            ),
            foreground="#666",
            wraplength=1100,
        )
        hint.pack(fill=X, pady=(8, 8))

        panes = ttk.PanedWindow(parent, orient=tk.HORIZONTAL)
        panes.pack(fill=BOTH, expand=True)

        left = ttk.Frame(panes, padding=(0, 0, 8, 0))
        panes.add(left, weight=1)
        ttk.Label(left, text="Topics", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.docs_topic_list = tk.Listbox(left, activestyle="dotbox", exportselection=False)
        self.docs_topic_list.pack(fill=BOTH, expand=True, pady=(6, 0))
        self.docs_topic_list.bind("<<ListboxSelect>>", lambda event: self.show_selected_doc())
        self.docs_topic_list.bind("<Double-Button-1>", lambda event: self.copy_current_doc())
        self._add_listbox_clipboard(self.docs_topic_list)

        right = ttk.Frame(panes)
        panes.add(right, weight=3)
        self.docs_view = tk.Text(right, wrap="word", undo=False, font=("Segoe UI", 10))
        yscroll = ttk.Scrollbar(right, orient=tk.VERTICAL, command=self.docs_view.yview)
        self.docs_view.configure(yscrollcommand=yscroll.set)
        self.docs_view.pack(side=LEFT, fill=BOTH, expand=True)
        yscroll.pack(side=RIGHT, fill=tk.Y)
        self.docs_view.tag_configure("h1", font=("Segoe UI", 20, "bold"), spacing1=6, spacing3=12)
        self.docs_view.tag_configure("h2", font=("Segoe UI", 16, "bold"), spacing1=12, spacing3=8)
        self.docs_view.tag_configure("h3", font=("Segoe UI", 12, "bold"), spacing1=10, spacing3=5)
        self.docs_view.tag_configure("paragraph", font=("Segoe UI", 10), spacing1=2, spacing3=6)
        self.docs_view.tag_configure("list_item", font=("Segoe UI", 10), lmargin1=22, lmargin2=42, spacing3=3)
        self.docs_view.tag_configure("number_item", font=("Segoe UI", 10), lmargin1=22, lmargin2=48, spacing3=3)
        self.docs_view.tag_configure("code_block", font=("Consolas", 10), background="#f3f4f6", lmargin1=16, lmargin2=16, spacing1=2, spacing3=2)
        self.docs_view.tag_configure("inline_code", font=("Consolas", 10), background="#eef2f7")
        self.docs_view.tag_configure("bold", font=("Segoe UI", 10, "bold"))
        self.docs_view.tag_configure("link", foreground="#0b57d0", underline=True)
        self.docs_view.tag_configure("callout_title", font=("Segoe UI", 10, "bold"), background="#fff7d6", lmargin1=16, lmargin2=16, spacing1=5)
        self.docs_view.tag_configure("callout_body", font=("Segoe UI", 10), background="#fffdf2", lmargin1=16, lmargin2=16, spacing3=5)
        self.docs_view.tag_configure("warning_title", font=("Segoe UI", 10, "bold"), background="#ffe5e5", lmargin1=16, lmargin2=16, spacing1=5)
        self.docs_view.tag_configure("warning_body", font=("Segoe UI", 10), background="#fff2f2", lmargin1=16, lmargin2=16, spacing3=5)
        self.docs_view.tag_configure("hr", foreground="#999", spacing1=8, spacing3=8)
        self._make_text_readonly(self.docs_view)
        self._add_text_clipboard_menu(self.docs_view, writable=False)

        self.reset_docs_search()

    def reset_docs_search(self) -> None:
        self.docs_search_query.set("")
        self.doc_topic_indices = list(range(len(DOC_TOPICS)))
        self._populate_docs_topics()
        if self.doc_topic_indices:
            self.docs_topic_list.selection_set(0)
            self.docs_topic_list.activate(0)
            self.show_selected_doc()

    def _populate_docs_topics(self) -> None:
        self.docs_topic_list.delete(0, END)
        if not self.doc_topic_indices:
            self.docs_topic_list.insert(END, "No matching docs found")
            return
        for real_index in self.doc_topic_indices:
            self.docs_topic_list.insert(END, DOC_TOPICS[real_index][0])

    def search_docs(self) -> None:
        query = self.docs_search_query.get().strip().lower()
        if not query:
            self.reset_docs_search()
            return
        matches: list[int] = []
        for idx, (title, body) in enumerate(DOC_TOPICS):
            haystack = f"{title}\n{body}".lower()
            if query in haystack:
                matches.append(idx)
        self.doc_topic_indices = matches
        self._populate_docs_topics()
        self.docs_view.delete("1.0", END)
        if matches:
            self.docs_topic_list.selection_set(0)
            self.docs_topic_list.activate(0)
            self.show_selected_doc()
            self.status.set(f"Docs search: {len(matches)} topic(s) found")
        else:
            self.docs_view.insert(END, "No matching documentation topic was found. Try a shorter or different search term.")
            self.status.set("Docs search: no matches")

    def selected_doc_topic(self) -> tuple[str, str] | None:
        if not hasattr(self, "docs_topic_list"):
            return None
        selection = self.docs_topic_list.curselection()
        if not selection or not self.doc_topic_indices:
            return None
        list_index = selection[0]
        if list_index >= len(self.doc_topic_indices):
            return None
        return DOC_TOPICS[self.doc_topic_indices[list_index]]

    def show_selected_doc(self) -> None:
        topic = self.selected_doc_topic()
        self.docs_view.delete("1.0", END)
        if not topic:
            self.docs_view.insert(END, "Select a topic from the left.", ("paragraph",))
            return
        title, body = topic
        self._render_doc_markdown(f"# {title}\n\n{body}")

    def _insert_markdown_inline(self, widget: tk.Text, text: str, base_tags: tuple[str, ...]) -> None:
        pattern = re.compile(r"(\*\*[^*]+\*\*|`[^`]+`|https?://\S+)")
        position = 0
        for match in pattern.finditer(text):
            if match.start() > position:
                widget.insert(END, text[position:match.start()], base_tags)
            token = match.group(0)
            if token.startswith("**") and token.endswith("**"):
                widget.insert(END, token[2:-2], base_tags + ("bold",))
            elif token.startswith("`") and token.endswith("`"):
                widget.insert(END, token[1:-1], base_tags + ("inline_code",))
            elif token.startswith("http"):
                widget.insert(END, token, base_tags + ("link",))
            else:
                widget.insert(END, token, base_tags)
            position = match.end()
        if position < len(text):
            widget.insert(END, text[position:], base_tags)

    def _render_doc_markdown(self, markdown: str) -> None:
        view = self.docs_view
        in_code = False
        current_callout: str | None = None
        for raw_line in markdown.splitlines():
            line = raw_line.rstrip("\n")
            stripped = line.strip()

            if stripped.startswith("```"):
                in_code = not in_code
                if not in_code:
                    view.insert(END, "\n")
                continue

            if in_code:
                view.insert(END, line + "\n", ("code_block",))
                continue

            if not stripped:
                view.insert(END, "\n")
                current_callout = None
                continue

            if stripped == "---":
                view.insert(END, "─" * 72 + "\n", ("hr",))
                continue

            if stripped.startswith("> [!"):
                label = stripped[4:].strip("[]!").upper()
                icon = {
                    "TIP": "💡 Tip",
                    "NOTE": "ℹ️ Note",
                    "IMPORTANT": "⭐ Important",
                    "WARNING": "⚠️ Warning",
                    "CAUTION": "⛔ Caution",
                }.get(label, label.title())
                current_callout = "warning" if label in {"WARNING", "CAUTION"} else "callout"
                view.insert(END, f"{icon}\n", (f"{current_callout}_title",))
                continue

            if stripped.startswith("> "):
                tag = "warning_body" if current_callout == "warning" else "callout_body"
                self._insert_markdown_inline(view, stripped[2:] + "\n", (tag,))
                continue

            if stripped.startswith("### "):
                self._insert_markdown_inline(view, stripped[4:] + "\n", ("h3",))
                continue
            if stripped.startswith("## "):
                self._insert_markdown_inline(view, stripped[3:] + "\n", ("h2",))
                continue
            if stripped.startswith("# "):
                self._insert_markdown_inline(view, stripped[2:] + "\n", ("h1",))
                continue

            task = re.match(r"^- \[( |x|X)\]\s+(.*)$", stripped)
            if task:
                marker = "☑" if task.group(1).lower() == "x" else "☐"
                self._insert_markdown_inline(view, f"{marker} {task.group(2)}\n", ("list_item",))
                continue

            bullet = re.match(r"^[-*]\s+(.*)$", stripped)
            if bullet:
                self._insert_markdown_inline(view, f"• {bullet.group(1)}\n", ("list_item",))
                continue

            number = re.match(r"^(\d+)\.\s+(.*)$", stripped)
            if number:
                self._insert_markdown_inline(view, f"{number.group(1)}. {number.group(2)}\n", ("number_item",))
                continue

            self._insert_markdown_inline(view, stripped + "\n", ("paragraph",))

    def copy_current_doc(self) -> None:
        text = self.docs_view.get("1.0", "end-1c")
        if not text.strip():
            return
        self._clipboard_set(text)
        self.status.set("Documentation topic copied")

    def copy_current_doc_markdown(self) -> None:
        topic = self.selected_doc_topic()
        if not topic:
            return
        title, body = topic
        self._clipboard_set(f"# {title}\n\n{body}\n")
        self.status.set("Documentation Markdown copied")

    def save_manual_file(self) -> None:
        filename = filedialog.asksaveasfilename(
            title="Save AZSOS manual",
            defaultextension=".md",
            initialfile="AZSOS-IN-APP-MANUAL-EN.md",
            filetypes=[("Markdown", "*.md"), ("Text", "*.txt"), ("All files", "*.*")],
        )
        if not filename:
            return
        Path(filename).write_text(manual_as_markdown(), encoding="utf-8")
        self.status.set(f"Manual saved to {filename}")

    def open_docs_folder(self) -> None:
        docs_dir = Path(__file__).resolve().parent / "docs"
        if docs_dir.exists():
            webbrowser.open(docs_dir.resolve().as_uri())
            return
        fallback = Path.home() / "AZSOS" / "IN_APP_MANUAL_EN.md"
        fallback.parent.mkdir(parents=True, exist_ok=True)
        fallback.write_text(manual_as_markdown(), encoding="utf-8")
        webbrowser.open(fallback.resolve().as_uri())

    # Clipboard helpers
    def _clipboard_set(self, value: str) -> None:
        self.clipboard_clear()
        self.clipboard_append(value)
        self.update_idletasks()

    def _event_state_has_ctrl(self, event: tk.Event) -> bool:
        return bool(getattr(event, "state", 0) & 0x4)

    def _add_entry_clipboard_menu(self, widget: tk.Widget, writable: bool = True) -> None:
        menu = tk.Menu(widget, tearoff=False)
        if writable:
            menu.add_command(label="Cut", command=lambda: widget.event_generate("<<Cut>>"))
        menu.add_command(label="Copy", command=lambda: widget.event_generate("<<Copy>>"))
        if writable:
            menu.add_command(label="Paste", command=lambda: widget.event_generate("<<Paste>>"))
        menu.add_separator()
        menu.add_command(label="Select all", command=lambda: widget.event_generate("<<SelectAll>>"))

        def show_menu(event: tk.Event) -> str:
            try:
                widget.focus_set()
                menu.tk_popup(event.x_root, event.y_root)
            finally:
                menu.grab_release()
            return "break"

        widget.bind("<Button-3>", show_menu)
        widget.bind("<Control-a>", lambda event: (widget.event_generate("<<SelectAll>>"), "break")[-1])
        widget.bind("<Control-A>", lambda event: (widget.event_generate("<<SelectAll>>"), "break")[-1])
        if writable:
            widget.bind("<Control-v>", lambda event: (widget.event_generate("<<Paste>>"), "break")[-1])
            widget.bind("<Control-V>", lambda event: (widget.event_generate("<<Paste>>"), "break")[-1])
            widget.bind("<Control-x>", lambda event: (widget.event_generate("<<Cut>>"), "break")[-1])
            widget.bind("<Control-X>", lambda event: (widget.event_generate("<<Cut>>"), "break")[-1])
        widget.bind("<Control-c>", lambda event: (widget.event_generate("<<Copy>>"), "break")[-1])
        widget.bind("<Control-C>", lambda event: (widget.event_generate("<<Copy>>"), "break")[-1])

    def _make_text_readonly(self, widget: tk.Text) -> None:
        allowed = {"c", "C", "a", "A", "Left", "Right", "Up", "Down", "Home", "End", "Prior", "Next"}

        def readonly_key(event: tk.Event) -> str | None:
            if self._event_state_has_ctrl(event) and event.keysym in {"c", "C", "a", "A"}:
                return None
            if event.keysym in allowed:
                return None
            return "break"

        widget.bind("<Key>", readonly_key)

    def _select_all_text(self, widget: tk.Text) -> str:
        widget.tag_add("sel", "1.0", "end-1c")
        widget.focus_set()
        return "break"

    def _copy_text_selection(self, widget: tk.Text) -> str:
        try:
            text = widget.get("sel.first", "sel.last")
        except tk.TclError:
            text = widget.get("1.0", "end-1c")
        self._clipboard_set(text)
        return "break"

    def _add_text_clipboard_menu(self, widget: tk.Text, writable: bool = False) -> None:
        menu = tk.Menu(widget, tearoff=False)
        if writable:
            menu.add_command(label="Cut", command=lambda: widget.event_generate("<<Cut>>"))
        menu.add_command(label="Copy", command=lambda: self._copy_text_selection(widget))
        if writable:
            menu.add_command(label="Paste", command=lambda: widget.event_generate("<<Paste>>"))
        menu.add_separator()
        menu.add_command(label="Select all", command=lambda: self._select_all_text(widget))

        def show_menu(event: tk.Event) -> str:
            try:
                widget.focus_set()
                menu.tk_popup(event.x_root, event.y_root)
            finally:
                menu.grab_release()
            return "break"

        widget.bind("<Button-3>", show_menu)
        widget.bind("<Control-a>", lambda event: self._select_all_text(widget))
        widget.bind("<Control-A>", lambda event: self._select_all_text(widget))
        widget.bind("<Control-c>", lambda event: self._copy_text_selection(widget))
        widget.bind("<Control-C>", lambda event: self._copy_text_selection(widget))
        if writable:
            widget.bind("<Control-v>", lambda event: (widget.event_generate("<<Paste>>"), "break")[-1])
            widget.bind("<Control-V>", lambda event: (widget.event_generate("<<Paste>>"), "break")[-1])

    def _listbox_selected_text(self, widget: tk.Listbox) -> str:
        selected = widget.curselection()
        if selected:
            return "\n".join(widget.get(index) for index in selected)
        values = widget.get(0, END)
        return "\n".join(values)

    def _copy_listbox_selection(self, widget: tk.Listbox) -> str:
        self._clipboard_set(self._listbox_selected_text(widget))
        return "break"

    def _add_listbox_clipboard(self, widget: tk.Listbox) -> None:
        menu = tk.Menu(widget, tearoff=False)
        menu.add_command(label="Copy selected", command=lambda: self._copy_listbox_selection(widget))
        menu.add_command(label="Copy all", command=lambda: self._clipboard_set("\n".join(widget.get(0, END))))

        def show_menu(event: tk.Event) -> str:
            try:
                index = widget.nearest(event.y)
                if index >= 0 and not widget.selection_includes(index):
                    widget.selection_clear(0, END)
                    widget.selection_set(index)
                    widget.activate(index)
                widget.focus_set()
                menu.tk_popup(event.x_root, event.y_root)
            finally:
                menu.grab_release()
            return "break"

        widget.bind("<Button-3>", show_menu)
        widget.bind("<Control-c>", lambda event: self._copy_listbox_selection(widget))
        widget.bind("<Control-C>", lambda event: self._copy_listbox_selection(widget))

    # Source management
    def refresh_sources_ui(self) -> None:
        if not self.sources:
            self.sources = [SourceConfig(DEFAULT_SOURCE_NAME, DEFAULT_SOURCE_URL)]
        values = [f"{idx + 1}. {source.name}" for idx, source in enumerate(self.sources)]
        self.source_combo["values"] = values
        self.source_index = max(0, min(self.source_index, len(self.sources) - 1))
        self.source_combo.current(self.source_index)
        current = self.sources[self.source_index]
        self.source_name.set(current.name)
        self.source_url.set(current.url)

    def select_source_from_combo(self) -> None:
        idx = self.source_combo.current()
        if idx < 0 or idx >= len(self.sources):
            return
        self.source_index = idx
        current = self.sources[idx]
        self.source_name.set(current.name)
        self.source_url.set(current.url)

    def save_current_source(self) -> None:
        name = self.source_name.get().strip() or "Custom source"
        url = self.source_url.get().strip()
        if not url:
            messagebox.showwarning("Missing URL", "Paste a GitHub/tree/release, direct .azsos URL, local folder, or registry URL first.")
            return
        self.sources[self.source_index] = SourceConfig(name=name, url=url, enabled=True)
        self._save_config()
        self.refresh_sources_ui()
        self.status.set("Source saved")

    def add_current_source(self) -> None:
        url = self.source_url.get().strip()
        if not url:
            messagebox.showwarning("Missing URL", "Paste a content source URL or local folder first.")
            return
        name = self.source_name.get().strip()
        if not name:
            name = simpledialog.askstring("Source name", "Name for this source:", initialvalue="Custom source") or "Custom source"
        self.sources.append(SourceConfig(name=name, url=url, enabled=True))
        self.source_index = len(self.sources) - 1
        self._save_config()
        self.refresh_sources_ui()
        self.status.set("Source added")

    def remove_current_source(self) -> None:
        if len(self.sources) <= 1:
            messagebox.showwarning("Cannot remove", "At least one source must remain.")
            return
        source = self.sources[self.source_index]
        if not messagebox.askyesno("Remove source", f"Remove this source?\n\n{source.name}\n{source.url}"):
            return
        del self.sources[self.source_index]
        self.source_index = 0
        self._save_config()
        self.refresh_sources_ui()
        self.status.set("Source removed")

    def reset_default_sources(self) -> None:
        self.sources = [SourceConfig(DEFAULT_SOURCE_NAME, DEFAULT_SOURCE_URL, True)]
        self.source_index = 0
        self._save_config()
        self.refresh_sources_ui()
        self.status.set("Default source restored")

    def open_source_url(self) -> None:
        url = self.source_url.get().strip() or DEFAULT_SOURCE_URL
        if Path(url).exists():
            webbrowser.open(Path(url).resolve().as_uri())
        else:
            webbrowser.open(url)

    # Installed packages
    def selected_manifest(self) -> dict | None:
        selection = self.package_list.curselection()
        if not selection:
            return None
        idx = selection[0]
        if idx >= len(self.packages):
            return None
        return self.packages[idx]

    def refresh_packages(self) -> None:
        self.packages = list_installed(self.library_dir)
        self.package_list.delete(0, END)
        for manifest in self.packages:
            publisher = manifest.get("publisher", {})
            trusted = "trusted" if publisher.get("fingerprint") in self.trusted_publishers else "unknown"
            self.package_list.insert(END, f"{manifest.get('title')}  -  {manifest.get('version')}  -  {trusted}")
        self.status.set(f"{len(self.packages)} package(s) installed | Library: {self.library_dir}")
        self.show_selected_details()

    def show_selected_details(self) -> None:
        manifest = self.selected_manifest()
        self.details.delete("1.0", END)
        if not manifest:
            self.details.insert(END, "Select a package to see details.")
            return
        publisher = manifest.get("publisher", {})
        fingerprint = publisher.get("fingerprint")
        trusted = self.trusted_publishers.get(fingerprint, "No") if fingerprint else "No fingerprint"
        size = format_bytes(manifest.get("size_bytes")) if manifest.get("size_bytes") else "unknown"
        lines = [
            f"Title: {manifest.get('title')}",
            f"ID: {manifest.get('id')}",
            f"Version: {manifest.get('version')}",
            f"Format: {manifest.get('format')}",
            f"Language: {manifest.get('language')}",
            f"Size: {size}",
            f"Publisher: {publisher.get('name')}",
            f"Fingerprint: {fingerprint}",
            f"Trusted publisher: {trusted}",
            f"Created: {manifest.get('created_at')}",
            f"Entry: {manifest.get('entry')}",
            f"Package file: {manifest.get('_package_file')}",
            f"Path: {manifest.get('_path')}",
        ]
        self.details.insert(END, "\n".join(lines))

    def import_package(self) -> None:
        filename = filedialog.askopenfilename(title="Import AZSOS package", filetypes=[("AZSOS packages", "*.azsos"), ("All files", "*.*")])
        if not filename:
            return
        package_path = Path(filename)
        result = verify_package(package_path)
        if not result.ok:
            messagebox.showerror("Invalid package", "\n".join(result.errors))
            return
        dest = install_package(package_path, self.library_dir)
        messagebox.showinfo("Imported", f"Package imported successfully.\n\n{dest}")
        self.refresh_packages()

    def verify_file(self) -> None:
        filename = filedialog.askopenfilename(title="Verify AZSOS package", filetypes=[("AZSOS packages", "*.azsos"), ("All files", "*.*")])
        if not filename:
            return
        result = verify_package(Path(filename))
        if result.ok:
            manifest = result.manifest or {}
            publisher = manifest.get("publisher", {})
            messagebox.showinfo("Package OK", f"Valid AZSOS package\n\nTitle: {manifest.get('title')}\nVersion: {manifest.get('version')}\nPublisher: {publisher.get('name')}\nFingerprint: {publisher.get('fingerprint')}")
        else:
            messagebox.showerror("Package failed", "\n".join(result.errors))

    def open_selected(self) -> None:
        manifest = self.selected_manifest()
        if not manifest:
            messagebox.showwarning("No package selected", "Select a package first.")
            return
        package_dir = Path(manifest.get("_path"))
        entry = manifest.get("entry", "content/index.html")
        target = package_dir / entry
        if not target.exists():
            messagebox.showerror("Missing entry", f"Could not find {entry}")
            return
        webbrowser.open(target.resolve().as_uri())

    def export_selected_package(self) -> None:
        manifest = self.selected_manifest()
        if not manifest:
            messagebox.showwarning("No package selected", "Select a package first.")
            return
        src = Path(manifest.get("_package_file", ""))
        if not src.exists():
            messagebox.showerror("Missing package file", "The original installed .azsos file was not found.")
            return
        filename = filedialog.asksaveasfilename(title="Export .azsos", defaultextension=".azsos", initialfile=src.name, filetypes=[("AZSOS packages", "*.azsos")])
        if not filename:
            return
        shutil.copy2(src, filename)
        self.status.set(f"Exported to {filename}")

    def delete_selected_package(self) -> None:
        manifest = self.selected_manifest()
        if not manifest:
            messagebox.showwarning("No package selected", "Select a package first.")
            return
        title = manifest.get("title") or manifest.get("id") or "selected package"
        if not messagebox.askyesno("Delete package", f"Delete this installed package?\n\n{title}"):
            return
        try:
            delete_installed(Path(manifest.get("_path")), self.library_dir)
        except Exception as exc:
            messagebox.showerror("Delete failed", str(exc))
            return
        self.refresh_packages()
        self.status.set(f"Deleted {title}")

    def trust_selected_publisher(self) -> None:
        manifest = self.selected_manifest()
        if not manifest:
            messagebox.showwarning("No package selected", "Select a package first.")
            return
        publisher = manifest.get("publisher", {})
        fingerprint = publisher.get("fingerprint")
        name = publisher.get("name") or "Unknown publisher"
        if not fingerprint:
            messagebox.showerror("Missing fingerprint", "This package does not include a publisher fingerprint.")
            return
        if not messagebox.askyesno("Trust publisher", f"Trust this publisher on this device?\n\n{name}\n{fingerprint}\n\nOnly do this if you verified the fingerprint through a trusted channel."):
            return
        self.trusted_publishers[fingerprint] = name
        self._save_config()
        self.refresh_packages()
        self.status.set(f"Trusted publisher: {name}")

    def open_library(self) -> None:
        self.library_dir.mkdir(parents=True, exist_ok=True)
        webbrowser.open(self.library_dir.resolve().as_uri())

    # Catalog / remote packages
    def clear_remote_list(self) -> None:
        self.remote_packages = []
        self.remote_list.delete(0, END)
        self.status.set("Remote list cleared")

    def fetch_selected_source(self) -> None:
        source = SourceConfig(name=self.source_name.get().strip() or "Custom source", url=self.source_url.get().strip() or DEFAULT_SOURCE_URL)
        self._fetch_sources([source])

    def fetch_all_sources(self) -> None:
        self.save_current_source()
        self._fetch_sources([source for source in self.sources if source.enabled])

    def _fetch_sources(self, sources: list[SourceConfig]) -> None:
        self.status.set("Fetching .azsos packages...")
        self.remote_list.delete(0, END)
        self.remote_list.insert(END, "Fetching...")

        def worker() -> None:
            found: list[RemotePackage] = []
            errors: list[str] = []
            for source in sources:
                try:
                    packages = discover_packages(source.url, include_releases=True)
                    for package in packages:
                        package.source = f"{source.name} / {package.source}"
                    found.extend(packages)
                except Exception as exc:
                    errors.append(f"{source.name}: {exc}")
            self.after(0, lambda found=found, errors=errors: self._fetch_done(found, errors))

        threading.Thread(target=worker, daemon=True).start()

    def _fetch_done(self, packages: list[RemotePackage], errors: list[str]) -> None:
        seen: set[str] = set()
        unique: list[RemotePackage] = []
        for package in packages:
            if package.download_url in seen:
                continue
            seen.add(package.download_url)
            unique.append(package)
        self.remote_packages = unique
        self.remote_list.delete(0, END)
        if not unique:
            self.remote_list.insert(END, "No .azsos packages found.")
        else:
            for package in unique:
                self.remote_list.insert(END, package.display())
        msg = f"Found {len(unique)} remote package(s)."
        if errors:
            msg += f" {len(errors)} source error(s)."
            messagebox.showwarning("Some sources failed", "\n".join(errors))
        self.status.set(msg)

    def selected_remote_indices(self) -> list[int]:
        if not self.remote_packages:
            return []
        return [idx for idx in self.remote_list.curselection() if idx < len(self.remote_packages)]

    def install_remote_selected(self) -> None:
        indices = self.selected_remote_indices()
        if not indices:
            messagebox.showwarning("No remote package selected", "Fetch content and select one or more .azsos packages first.")
            return
        remotes = [self.remote_packages[idx] for idx in indices]
        self.status.set(f"Installing {len(remotes)} package(s)...")

        def worker() -> None:
            installed: list[Path] = []
            errors: list[str] = []
            for remote in remotes:
                try:
                    downloaded = download_package(remote)
                    result = verify_package(downloaded)
                    if not result.ok:
                        raise ValueError("Downloaded file is not a valid AZSOS package: " + "; ".join(result.errors))
                    installed.append(install_package(downloaded, self.library_dir))
                except Exception as exc:
                    errors.append(f"{remote.name}: {exc}")
            self.after(0, lambda installed=installed, errors=errors: self._install_remote_done(installed, errors))

        threading.Thread(target=worker, daemon=True).start()

    def _install_remote_done(self, installed: list[Path], errors: list[str]) -> None:
        self.refresh_packages()
        if errors:
            messagebox.showwarning("Install completed with errors", "\n".join(errors))
        elif installed:
            messagebox.showinfo("Installed", f"Installed {len(installed)} package(s) successfully.")
        self.status.set(f"Installed {len(installed)} package(s). {len(errors)} error(s).")

    def inspect_remote_selected(self) -> None:
        indices = self.selected_remote_indices()
        if not indices:
            messagebox.showwarning("No remote package selected", "Select a remote package first.")
            return
        idx = indices[0]
        remote = self.remote_packages[idx]
        self.status.set(f"Inspecting {remote.name}...")

        def worker() -> None:
            try:
                enriched, downloaded = inspect_remote_package(remote)
            except Exception as exc:
                self.after(0, lambda exc=exc: messagebox.showerror("Inspect failed", str(exc)))
                self.after(0, lambda: self.status.set("Inspect failed"))
                return
            self.after(0, lambda enriched=enriched, downloaded=downloaded, idx=idx: self._inspect_done(idx, enriched, downloaded))

        threading.Thread(target=worker, daemon=True).start()

    def _inspect_done(self, idx: int, enriched: RemotePackage, downloaded: Path) -> None:
        self.remote_packages[idx] = enriched
        self.remote_list.delete(idx)
        self.remote_list.insert(idx, enriched.display())
        trusted = self.trusted_publishers.get(enriched.fingerprint or "", "No")
        messagebox.showinfo(
            "Remote package details",
            f"Title: {enriched.title}\nID: {enriched.package_id}\nVersion: {enriched.version}\nPublisher: {enriched.publisher}\nFingerprint: {enriched.fingerprint}\nTrusted publisher: {trusted}\nSHA-256: {enriched.sha256}\nCached file: {downloaded}",
        )
        self.status.set("Remote package inspected")

    def open_remote_page(self) -> None:
        indices = self.selected_remote_indices()
        if not indices:
            messagebox.showwarning("No remote package selected", "Select a remote package first.")
            return
        remote = self.remote_packages[indices[0]]
        webbrowser.open(remote.page_url or remote.download_url)

    def copy_remote_url(self) -> None:
        indices = self.selected_remote_indices()
        if not indices:
            messagebox.showwarning("No remote package selected", "Select a remote package first.")
            return
        urls = "\n".join(self.remote_packages[idx].download_url for idx in indices)
        self._clipboard_set(urls)
        self.status.set("Remote download URL copied")

    # Search
    def search_selected(self) -> None:
        manifest = self.selected_manifest()
        if not manifest:
            messagebox.showwarning("No package selected", "Select a package first.")
            return
        self._run_search([manifest])

    def search_all(self) -> None:
        self._run_search(self.packages)

    def _run_search(self, manifests: list[dict]) -> None:
        query = self.search_query.get().strip()
        if not query:
            messagebox.showwarning("Empty query", "Type a search query first.")
            return
        self.search_hits = []
        self.results.delete(0, END)
        for manifest in manifests:
            hits = search_installed(Path(manifest.get("_path")), query)
            for hit in hits:
                self.search_hits.append((manifest, hit))
                snippet = hit.snippet.replace("\n", " ")[:110]
                self.results.insert(END, f"{manifest.get('title')} / {hit.title} - {snippet}")
        if not self.search_hits:
            self.results.insert(END, "No results")

    def open_result(self) -> None:
        selection = self.results.curselection()
        if not selection or not self.search_hits:
            return
        idx = selection[0]
        if idx >= len(self.search_hits):
            return
        manifest, hit = self.search_hits[idx]
        target = Path(manifest.get("_path")) / hit.path
        if target.exists():
            webbrowser.open(target.resolve().as_uri())

    # Share
    def copy_share_url(self) -> None:
        value = self.share_url.get()
        if not value.startswith("http"):
            messagebox.showwarning("Share stopped", "Start local share first.")
            return
        self._clipboard_set(value)
        self.status.set("Share URL copied to clipboard")

    def start_share(self) -> None:
        if self.share_server:
            messagebox.showinfo("Already running", self.share_url.get())
            return
        self.share_server = ShareServer(self.library_dir, port=8765)
        try:
            url = self.share_server.start()
        except OSError:
            self.share_server = ShareServer(self.library_dir, port=0)
            url = self.share_server.start()
            self.status.set("Port 8765 unavailable, using another port.")
        self.share_url.set(url)

    def stop_share(self) -> None:
        if self.share_server:
            self.share_server.stop()
            self.share_server = None
        self.share_url.set("Local share is stopped")

    def show_qr(self) -> None:
        url = self.share_url.get()
        if not url.startswith("http"):
            messagebox.showwarning("Share stopped", "Start local share first.")
            return
        try:
            import qrcode
        except Exception:
            messagebox.showerror("Missing dependency", "Install qrcode with: pip install -r requirements.txt")
            return
        img = qrcode.make(url)
        output = Path(tempfile.gettempdir()) / "azsos-share-qr.png"
        img.save(output)
        webbrowser.open(output.resolve().as_uri())

    # Software updates
    def check_for_updates(self) -> None:
        self.status.set("Checking AZSOS updates...")

        def worker() -> None:
            try:
                updates = discover_updates(DEFAULT_UPDATE_SOURCE_URL, include_releases=True)
                self.after(0, lambda updates=updates: self._updates_fetch_done(updates, []))
            except Exception as exc:
                self.after(0, lambda exc=exc: self._updates_fetch_done([], [str(exc)]))

        threading.Thread(target=worker, daemon=True).start()

    def _updates_fetch_done(self, updates: list[RemoteUpdate], errors: list[str]) -> None:
        if errors:
            self.status.set("Update check failed")
            messagebox.showwarning("Update check failed", "\n".join(errors))
            return
        if not updates:
            self.status.set("No updates found")
            messagebox.showinfo(
                "No updates found",
                "No app update files were found.\n\n"
                f"Checked:\n{DEFAULT_UPDATE_SOURCE_URL}\n\n"
                "Put update.index.json or .exe/.msi/.zip files on the UPDATE branch.",
            )
            return
        self.status.set(f"Found {len(updates)} update file(s)")
        self._show_updates_window(updates)

    def _show_updates_window(self, updates: list[RemoteUpdate]) -> None:
        window = tk.Toplevel(self)
        window.title("AZSOS updates")
        window.geometry("820x420")
        window.minsize(720, 360)
        window.transient(self)

        frame = ttk.Frame(window, padding=12)
        frame.pack(fill=BOTH, expand=True)
        ttk.Label(frame, text="Available AZSOS update files", font=("Segoe UI", 12, "bold")).pack(anchor="w")
        ttk.Label(
            frame,
            text=(
                "Updates are discovered from the UPDATE branch and GitHub Releases. "
                "AZSOS downloads the selected file; run the installer/archive manually after closing the app."
            ),
            foreground="#666",
            wraplength=760,
        ).pack(fill=X, pady=(2, 8))

        listbox = tk.Listbox(frame, activestyle="dotbox", exportselection=False)
        listbox.pack(fill=BOTH, expand=True)
        for update in updates:
            listbox.insert(END, update.display())
        if updates:
            listbox.selection_set(0)
        self._add_listbox_clipboard(listbox)

        detail = tk.Text(frame, height=4, wrap="word", undo=False)
        detail.pack(fill=X, pady=(8, 0))
        self._make_text_readonly(detail)
        self._add_text_clipboard_menu(detail, writable=False)

        def selected_update() -> RemoteUpdate | None:
            selection = listbox.curselection()
            if not selection:
                messagebox.showwarning("No update selected", "Select an update file first.")
                return None
            idx = selection[0]
            if idx >= len(updates):
                return None
            return updates[idx]

        def refresh_detail(event: object | None = None) -> None:
            update = selected_update()
            if not update:
                return
            detail.delete("1.0", END)
            detail.insert(
                END,
                f"Name: {update.name}\n"
                f"Version: {update.version or 'unknown'}\n"
                f"Size: {format_bytes(update.size_bytes)}\n"
                f"Source: {update.source}\n"
                f"SHA-256: {update.sha256 or 'not provided'}\n"
                f"Download: {update.download_url}\n"
                f"Page: {update.page_url or update.download_url}\n"
                f"Notes: {update.notes or ''}",
            )

        def copy_url() -> None:
            update = selected_update()
            if not update:
                return
            self._clipboard_set(update.download_url)
            self.status.set("Update download URL copied")

        def open_page() -> None:
            update = selected_update()
            if not update:
                return
            webbrowser.open(update.page_url or update.download_url)

        def open_update_source() -> None:
            webbrowser.open(DEFAULT_UPDATE_SOURCE_URL)

        def download_selected() -> None:
            update = selected_update()
            if not update:
                return
            self.status.set(f"Downloading update: {update.name}...")

            def worker() -> None:
                try:
                    downloaded = download_update(update)
                    self.after(0, lambda downloaded=downloaded: download_done(downloaded, None))
                except Exception as exc:
                    self.after(0, lambda exc=exc: download_done(None, exc))

            threading.Thread(target=worker, daemon=True).start()

        def download_done(downloaded: Path | None, exc: Exception | None) -> None:
            if exc:
                self.status.set("Update download failed")
                messagebox.showerror("Download failed", str(exc))
                return
            assert downloaded is not None
            self.status.set(f"Update downloaded: {downloaded}")
            if messagebox.askyesno(
                "Update downloaded",
                f"Downloaded to:\n{downloaded}\n\nOpen the folder now?",
            ):
                webbrowser.open(downloaded.parent.resolve().as_uri())

        listbox.bind("<<ListboxSelect>>", refresh_detail)
        listbox.bind("<Double-Button-1>", lambda event: download_selected())
        refresh_detail()

        buttons = ttk.Frame(frame)
        buttons.pack(fill=X, pady=(8, 0))
        ttk.Button(buttons, text="Download selected", command=download_selected).pack(side=LEFT)
        ttk.Button(buttons, text="Open page", command=open_page).pack(side=LEFT, padx=6)
        ttk.Button(buttons, text="Copy URL", command=copy_url).pack(side=LEFT, padx=6)
        ttk.Button(buttons, text="Open UPDATE branch", command=open_update_source).pack(side=LEFT, padx=6)
        ttk.Button(buttons, text="Close", command=window.destroy).pack(side=RIGHT)

    # Misc
    def show_about(self) -> None:
        messagebox.showinfo(
            "About AZSOS",
            "AZSOS - offline emergency cache\n\n"
            "Default package source:\n"
            f"{DEFAULT_SOURCE_URL}\n\n"
            "App update source:\n"
            f"{DEFAULT_UPDATE_SOURCE_URL}\n\n"
            "X: https://x.com/the_azzi\n"
            "GitHub: https://github.com/TheGreatAzizi\n"
            "Self-hosted Git: https://git.theazizi.ir/TheAzizi\n"
            "Telegram: https://t.me/luluch_code",
        )

    def destroy(self) -> None:
        self.stop_share()
        self._save_config()
        super().destroy()


if __name__ == "__main__":
    AZSOSApp().mainloop()
