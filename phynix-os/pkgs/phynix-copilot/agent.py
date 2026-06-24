#!/usr/bin/env python3
"""
PHYNIX Copilot — AI Assistant for NixOS Configuration
Phase 1: Read-only intelligence with smolagents
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

# Import local modules
from tools import NixTools, HyprlandTools, SystemTools
from rag import RAGIndex
from write_agent import WriteAgent


class PhynixCopilot:
    def __init__(self, interactive: bool = True):
        self.cache_dir = Path.home() / ".local/state/phynix"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.audit_log = self.cache_dir / "audit.jsonl"

        self.nix_tools = NixTools()
        self.hyprland_tools = HyprlandTools()
        self.system_tools = SystemTools()
        self.rag = RAGIndex()
        self.write_agent = WriteAgent(interactive=interactive)

        self.llm_backend = self._detect_lm_backend()
        self.interactive = interactive

    def _detect_lm_backend(self) -> str:
        """
        Route LLM backend for CPU-only systems:
        1. Try HuggingFace Inference API (remote, primary)
        2. Fallback to Ollama (local, requires setup)
        3. Fallback to phi-4-mini via Ollama (3.8B, ~2GB RAM)
        """
        # Check HF_TOKEN for inference API
        if os.getenv("HF_TOKEN"):
            return "hf_inference"

        # Check if Ollama is available
        try:
            result = subprocess.run(
                ["ollama", "--version"],
                capture_output=True,
                timeout=2
            )
            if result.returncode == 0:
                # Check if qwen3-coder-next is available
                try:
                    subprocess.run(
                        ["ollama", "show", "qwen3-coder-next"],
                        capture_output=True,
                        timeout=2
                    )
                    return "ollama_qwen3"
                except:
                    return "ollama_phi4_mini"
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        return "offline_mode"

    def log_action(self, action: str, status: str, details: Dict[str, Any]):
        """Audit log all actions"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "status": status,
            "details": details
        }
        with open(self.audit_log, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def ensure_rag_ready(self):
        """Bootstrap RAG index if empty on first run."""
        status = self.rag.status()
        if not status.get("ready"):
            print("[PHYNIX Copilot] Bootstrapping RAG index...", file=sys.stderr)
            self.rag.index_all()

    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Process user query:
        1. Retrieve RAG context
        2. Route to appropriate tool
        3. Format response
        """
        self.log_action("query_received", "processing", {"query": query})

        # Retrieve RAG context (real documents now)
        rag_context = self.rag.build_context(query)

        # Route query based on keywords
        response = self._route_query(query)

        # Build response with RAG context
        result = {
            "query": query,
            "response": response,
            "rag_context": rag_context,
            "backend": self.llm_backend
        }

        self.log_action("query_processed", "success", {"query": query})
        return result

    def _route_query(self, query: str) -> Dict[str, Any]:
        """Route query to appropriate tool (read-only or write)"""
        query_lower = query.lower()

        # WRITE OPERATIONS (Phase 3+)
        if any(x in query_lower for x in ["install", "add", "remove", "rebuild", "switch"]):
            return {
                "tool": "write_agent",
                "mode": "interactive" if self.interactive else "sandbox",
                "result": self.write_agent.handle_query(query)
            }

        # READ-ONLY OPERATIONS (Phase 1+)

        # Nix operations - search
        if "search" in query_lower:
            search_term = query.split("search")[-1].strip()
            return {"tool": "nix_search", "result": self.nix_tools.nix_search(search_term)}

        # Flake checks
        if any(x in query_lower for x in ["flake", "check", "error"]):
            return {"tool": "nix_flake_check", "result": self.nix_tools.nix_flake_check()}

        # Hyprland queries
        if "hyprland" in query_lower or "keybind" in query_lower:
            return {"tool": "hyprctl", "result": self.hyprland_tools.hyprctl_command("binds")}

        # System status
        if "status" in query_lower or "log" in query_lower:
            unit = "phynix-copilot"  # Default unit
            return {"tool": "systemctl_status", "result": self.system_tools.systemctl_status(unit)}

        # Default: Placeholder for LLM-based reasoning
        return {
            "tool": "llm_reasoning",
            "backend": self.llm_backend,
            "note": "LLM reasoning pending (read-only tools available)"
        }

    def run_interactive(self):
        """Interactive CLI mode"""
        self.ensure_rag_ready()
        print("PHYNIX Copilot — Interactive Mode", file=sys.stderr)
        print(f"LLM Backend: {self.llm_backend}", file=sys.stderr)
        rag_status = self.rag.status()
        print(f"RAG: {rag_status['backend']} ({rag_status['total_docs']} docs)", file=sys.stderr)
        print("Type 'exit' to quit", file=sys.stderr)
        print()

        while True:
            try:
                query = input("pcopilot> ").strip()
                if query.lower() in ["exit", "quit"]:
                    break
                if not query:
                    continue

                result = self.process_query(query)
                print(json.dumps(result, indent=2))
            except KeyboardInterrupt:
                print("\nExiting...", file=sys.stderr)
                break
            except Exception as e:
                self.log_action("error", "exception", {"error": str(e)})
                print(f"Error: {e}", file=sys.stderr)

    def run_daemon(self):
        """Run as systemd service"""
        print("PHYNIX Copilot service started", file=sys.stderr)
        self.log_action("daemon_started", "success", {"backend": self.llm_backend})
        try:
            # Keep service alive
            import time
            while True:
                time.sleep(3600)
        except KeyboardInterrupt:
            self.log_action("daemon_stopped", "success", {})


def main():
    copilot = PhynixCopilot()

    # Run mode based on environment
    if os.getenv("PHYNIX_DAEMON"):
        copilot.run_daemon()
    else:
        copilot.run_interactive()


if __name__ == "__main__":
    main()
