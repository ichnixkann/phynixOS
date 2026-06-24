"""
PHYNIX Copilot RAG Index — Real ChromaDB document indexing and retrieval
"""

import json
import re
import subprocess
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime


def _chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """Split text into overlapping chunks for embedding."""
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = " ".join(words[i : i + chunk_size])
        if chunk.strip():
            chunks.append(chunk)
        i += chunk_size - overlap
    return chunks


def _doc_id(source: str, content: str) -> str:
    h = hashlib.md5(f"{source}:{content[:80]}".encode()).hexdigest()[:12]
    return f"{source}_{h}"


class RAGIndex:
    """ChromaDB-backed RAG for NixOS / Home Manager / Hyprland documentation."""

    COLLECTION_NAME = "phynix_docs"

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = Path(db_path or Path.home() / ".local/share/phynix/rag_db")
        self.db_path.mkdir(parents=True, exist_ok=True)

        self._client = None
        self._collection = None
        self._chroma_available = self._init_chroma()

        # Flat-file fallback index (always available)
        self._flat_index_path = self.db_path / "flat_index.jsonl"

    # ------------------------------------------------------------------
    # Initialisation
    # ------------------------------------------------------------------

    def _init_chroma(self) -> bool:
        try:
            import chromadb
            self._client = chromadb.PersistentClient(path=str(self.db_path))
            self._collection = self._client.get_or_create_collection(
                name=self.COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"},
            )
            return True
        except ImportError:
            return False
        except Exception:
            return False

    # ------------------------------------------------------------------
    # Document ingestion helpers
    # ------------------------------------------------------------------

    def _ingest_docs(self, source: str, docs: List[Dict[str, str]]) -> int:
        """Add document chunks to ChromaDB (or flat-file fallback)."""
        ids, texts, metas = [], [], []
        for doc in docs:
            for chunk in _chunk_text(doc["text"]):
                doc_id = _doc_id(source, chunk)
                ids.append(doc_id)
                texts.append(chunk)
                metas.append({"source": source, "title": doc.get("title", "")})

        if not ids:
            return 0

        if self._chroma_available and self._collection is not None:
            # ChromaDB upsert in batches of 100
            batch = 100
            for i in range(0, len(ids), batch):
                self._collection.upsert(
                    ids=ids[i : i + batch],
                    documents=texts[i : i + batch],
                    metadatas=metas[i : i + batch],
                )
        else:
            # Flat-file fallback
            with open(self._flat_index_path, "a") as f:
                for doc_id, text, meta in zip(ids, texts, metas):
                    f.write(json.dumps({"id": doc_id, "text": text, "meta": meta}) + "\n")

        return len(ids)

    # ------------------------------------------------------------------
    # NixOS options
    # ------------------------------------------------------------------

    def index_nixos_options(self) -> Dict[str, Any]:
        """Parse nixos-option JSON dump and index all options."""
        docs: List[Dict[str, str]] = []

        # Try nix-based options JSON
        try:
            result = subprocess.run(
                ["nix", "eval", "--json", "(import <nixpkgs/nixos> {}).options"],
                capture_output=True, text=True, timeout=60,
            )
            if result.returncode == 0:
                opts = json.loads(result.stdout)
                for name, info in opts.items():
                    desc = info.get("description", "")
                    typ = info.get("type", "")
                    default = str(info.get("default", ""))
                    text = f"NixOS option: {name}\nType: {typ}\nDescription: {desc}\nDefault: {default}"
                    docs.append({"title": name, "text": text})
        except Exception:
            pass

        # Fallback: parse nixos-option man page snippets
        if not docs:
            try:
                result = subprocess.run(
                    ["man", "-P", "cat", "configuration.nix"],
                    capture_output=True, text=True, timeout=10,
                )
                if result.returncode == 0:
                    for block in result.stdout.split("\n\n"):
                        block = block.strip()
                        if block:
                            docs.append({"title": "nixos-manpage", "text": block})
            except Exception:
                pass

        # Always add static seed docs so RAG is never empty
        docs.extend(self._nixos_seed_docs())

        count = self._ingest_docs("nixos_options", docs)
        return {"indexed": True, "source": "nixos_options", "count": count}

    def _nixos_seed_docs(self) -> List[Dict[str, str]]:
        return [
            {
                "title": "services.pipewire",
                "text": (
                    "NixOS option: services.pipewire.enable\n"
                    "Type: boolean\nDefault: false\n"
                    "Description: Enable PipeWire, a server for handling audio and video streams. "
                    "Set services.pipewire.pulse.enable = true to replace PulseAudio."
                ),
            },
            {
                "title": "programs.hyprland",
                "text": (
                    "NixOS option: programs.hyprland.enable\n"
                    "Type: boolean\nDefault: false\n"
                    "Description: Enable Hyprland Wayland compositor. "
                    "Also enables XDG portal and xwayland by default."
                ),
            },
            {
                "title": "networking.networkmanager",
                "text": (
                    "NixOS option: networking.networkmanager.enable\n"
                    "Type: boolean\nDefault: false\n"
                    "Description: Enable NetworkManager. "
                    "Add users to the networkmanager group to allow them to manage connections."
                ),
            },
            {
                "title": "nix.settings.experimental-features",
                "text": (
                    "NixOS option: nix.settings.experimental-features\n"
                    "Type: list of string\n"
                    "Description: Enable Nix experimental features such as 'nix-command' and 'flakes'. "
                    "Example: nix.settings.experimental-features = [\"nix-command\" \"flakes\"];"
                ),
            },
            {
                "title": "boot.loader.grub",
                "text": (
                    "NixOS option: boot.loader.grub.enable\n"
                    "Type: boolean\nDefault: false\n"
                    "Description: Enable the GNU GRUB boot loader. "
                    "Set boot.loader.grub.device to the disk path (e.g. \"/dev/sda\")."
                ),
            },
        ]

    # ------------------------------------------------------------------
    # Home Manager options
    # ------------------------------------------------------------------

    def index_home_manager(self) -> Dict[str, Any]:
        """Index Home Manager options from JSON or seed docs."""
        docs: List[Dict[str, str]] = []

        try:
            result = subprocess.run(
                [
                    "nix", "eval", "--json",
                    "(import <home-manager/modules> { pkgs = import <nixpkgs> {}; lib = (import <nixpkgs> {}).lib; configuration = {}; }).options",
                ],
                capture_output=True, text=True, timeout=60,
            )
            if result.returncode == 0:
                opts = json.loads(result.stdout)
                for name, info in opts.items():
                    desc = info.get("description", "")
                    text = f"Home Manager option: {name}\nDescription: {desc}"
                    docs.append({"title": name, "text": text})
        except Exception:
            pass

        docs.extend(self._hm_seed_docs())
        count = self._ingest_docs("home_manager", docs)
        return {"indexed": True, "source": "home_manager", "count": count}

    def _hm_seed_docs(self) -> List[Dict[str, str]]:
        return [
            {
                "title": "home.packages",
                "text": (
                    "Home Manager option: home.packages\n"
                    "Type: list of package\n"
                    "Description: Packages to install in the user environment. "
                    "Example: home.packages = with pkgs; [ ripgrep bat exa ];"
                ),
            },
            {
                "title": "programs.fish",
                "text": (
                    "Home Manager option: programs.fish.enable\n"
                    "Type: boolean\nDefault: false\n"
                    "Description: Enable Fish shell management via Home Manager. "
                    "Set interactiveShellInit, functions, and shellAliases for configuration."
                ),
            },
            {
                "title": "programs.git",
                "text": (
                    "Home Manager option: programs.git.enable\n"
                    "Type: boolean\nDefault: false\n"
                    "Description: Enable Git VCS. "
                    "Set programs.git.userName, programs.git.userEmail, and programs.git.extraConfig."
                ),
            },
            {
                "title": "wayland.windowManager.hyprland",
                "text": (
                    "Home Manager option: wayland.windowManager.hyprland.enable\n"
                    "Type: boolean\nDefault: false\n"
                    "Description: Enable Hyprland configuration via Home Manager. "
                    "Use wayland.windowManager.hyprland.settings for keybinds and rules."
                ),
            },
        ]

    # ------------------------------------------------------------------
    # Hyprland docs
    # ------------------------------------------------------------------

    def index_hyprland_docs(self) -> Dict[str, Any]:
        """Index Hyprland docs from man pages and seed content."""
        docs: List[Dict[str, str]] = []

        try:
            result = subprocess.run(
                ["man", "-P", "cat", "hyprland"],
                capture_output=True, text=True, timeout=10,
            )
            if result.returncode == 0:
                for block in result.stdout.split("\n\n"):
                    block = block.strip()
                    if len(block) > 40:
                        docs.append({"title": "hyprland-man", "text": block})
        except Exception:
            pass

        docs.extend(self._hyprland_seed_docs())
        count = self._ingest_docs("hyprland", docs)
        return {"indexed": True, "source": "hyprland", "count": count}

    def _hyprland_seed_docs(self) -> List[Dict[str, str]]:
        return [
            {
                "title": "hyprland-keybinds",
                "text": (
                    "Hyprland keybinds are configured in hyprland.conf with the bind directive. "
                    "Syntax: bind = MODS, KEY, dispatcher, params\n"
                    "Example: bind = SUPER, Return, exec, alacritty\n"
                    "bind = SUPER SHIFT, Q, killactive\n"
                    "bind = SUPER, F, fullscreen"
                ),
            },
            {
                "title": "hyprland-monitors",
                "text": (
                    "Hyprland monitor configuration: monitor = name, resolution, position, scale\n"
                    "Example: monitor=,preferred,auto,1 (auto-detect all monitors)\n"
                    "monitor=DP-1,1920x1080@144,0x0,1\n"
                    "monitor=HDMI-A-1,1920x1080,1920x0,1"
                ),
            },
            {
                "title": "hyprland-animations",
                "text": (
                    "Hyprland animations in hyprland.conf:\n"
                    "animations {\n"
                    "  enabled = true\n"
                    "  bezier = myBezier, 0.05, 0.9, 0.1, 1.05\n"
                    "  animation = windows, 1, 7, myBezier\n"
                    "  animation = workspaces, 1, 6, default\n"
                    "}"
                ),
            },
            {
                "title": "hyprland-rules",
                "text": (
                    "Hyprland window rules: windowrule = rule, class\n"
                    "Example: windowrule = float, ^(pavucontrol)$\n"
                    "windowrulev2 = opacity 0.8, class:^(Alacritty)$\n"
                    "windowrulev2 = workspace 2, class:^(firefox)$"
                ),
            },
        ]

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Return top_k relevant chunks for query."""
        if self._chroma_available and self._collection is not None:
            try:
                count = self._collection.count()
                if count == 0:
                    return self._flat_search(query, top_k)
                results = self._collection.query(
                    query_texts=[query],
                    n_results=min(top_k, count),
                )
                docs = results.get("documents", [[]])[0]
                metas = results.get("metadatas", [[]])[0]
                distances = results.get("distances", [[]])[0]
                return [
                    {
                        "doc_id": f"chroma_{i}",
                        "text": doc,
                        "source": meta.get("source", ""),
                        "title": meta.get("title", ""),
                        "relevance": round(1.0 - dist, 4),
                    }
                    for i, (doc, meta, dist) in enumerate(zip(docs, metas, distances))
                ]
            except Exception:
                pass

        return self._flat_search(query, top_k)

    def _flat_search(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Keyword-based fallback search over flat-file index."""
        if not self._flat_index_path.exists():
            return []

        query_lower = query.lower()
        keywords = re.findall(r"\w+", query_lower)
        scored: List[tuple] = []

        with open(self._flat_index_path) as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    text_lower = entry["text"].lower()
                    score = sum(1 for kw in keywords if kw in text_lower)
                    if score > 0:
                        scored.append((score, entry))
                except Exception:
                    continue

        scored.sort(key=lambda x: x[0], reverse=True)
        return [
            {
                "doc_id": e["id"],
                "text": e["text"],
                "source": e["meta"].get("source", ""),
                "title": e["meta"].get("title", ""),
                "relevance": round(score / max(len(keywords), 1), 4),
            }
            for score, e in scored[:top_k]
        ]

    # ------------------------------------------------------------------
    # Context builder
    # ------------------------------------------------------------------

    def build_context(self, query: str) -> str:
        """Build RAG context string for agent prompt augmentation."""
        results = self.search(query, top_k=3)
        if not results:
            return ""
        context = "## Relevant Documentation\n\n"
        for i, r in enumerate(results, 1):
            source = r.get("source", "")
            title = r.get("title", "")
            header = f"[{source}] {title}".strip(" []")
            context += f"**{i}. {header}**\n{r['text']}\n\n"
        return context.strip()

    # ------------------------------------------------------------------
    # Status & maintenance
    # ------------------------------------------------------------------

    def index_all(self) -> Dict[str, Any]:
        """Run all indexers and return summary."""
        results = {
            "nixos_options": self.index_nixos_options(),
            "home_manager": self.index_home_manager(),
            "hyprland": self.index_hyprland_docs(),
            "timestamp": datetime.now().isoformat(),
            "backend": "chromadb" if self._chroma_available else "flat_file",
        }
        total = sum(r.get("count", 0) for r in results.values() if isinstance(r, dict))
        results["total_chunks"] = total
        return results

    def status(self) -> Dict[str, Any]:
        """Return index status."""
        if self._chroma_available and self._collection is not None:
            count = self._collection.count()
            return {
                "backend": "chromadb",
                "total_docs": count,
                "db_path": str(self.db_path),
                "ready": count > 0,
            }
        flat_count = 0
        if self._flat_index_path.exists():
            with open(self._flat_index_path) as f:
                flat_count = sum(1 for _ in f)
        return {
            "backend": "flat_file",
            "total_docs": flat_count,
            "db_path": str(self._flat_index_path),
            "ready": flat_count > 0,
            "note": "Install chromadb for vector search: pip install chromadb",
        }
