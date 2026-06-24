#!/usr/bin/env python3
"""
PHYNIX Copilot — AI Assistant for NixOS Configuration
Optimized for CPU-only systems with remote LLM fallback
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Optional

class PhynixCopilot:
    def __init__(self):
        self.cache_dir = Path.home() / ".local/state/phynix"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.audit_log = self.cache_dir / "audit.jsonl"

    def detect_lm_backend(self) -> str:
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
                return "ollama_qwen3"
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        return "ollama_phi4_mini"

    def log_action(self, action: str, status: str, details: dict):
        """Audit log all actions"""
        entry = {
            "timestamp": subprocess.run(
                ["date", "-Is"],
                capture_output=True,
                text=True
            ).stdout.strip(),
            "action": action,
            "status": status,
            "details": details
        }
        with open(self.audit_log, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def run(self):
        backend = self.detect_lm_backend()
        print(f"[PHYNIX Copilot] LLM Backend: {backend}", file=sys.stderr)
        self.log_action("startup", "success", {"backend": backend})

        # Placeholder: Listen for CLI input, respond to queries
        print("PHYNIX Copilot ready. (Phase 0 stub)", file=sys.stderr)

if __name__ == "__main__":
    copilot = PhynixCopilot()
    copilot.run()
