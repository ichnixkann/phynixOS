"""
PHYNIX Copilot Write-Mode Agent
Autonomous mutations with safety gates and rollback
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional

from write_tools import (
    WriteGate, Change, FlakeTools, HomeManagerTools, NixosRebuildTools
)


class WriteAgent:
    """Agent capable of autonomous system modifications"""

    def __init__(self, flake_dir: Path = None, interactive: bool = True):
        self.flake_dir = flake_dir or Path.home() / "phynix-flake"
        self.interactive = interactive

        # Confirmation gate
        self.write_gate = WriteGate(
            callback=self.interactive_confirm if interactive else self.auto_approve
        )

        # Tool instances
        self.flake_tools = FlakeTools(self.write_gate, self.flake_dir)
        self.hm_tools = HomeManagerTools(self.write_gate)
        self.rebuild_tools = NixosRebuildTools(self.write_gate)

    def interactive_confirm(self, prompt: str) -> bool:
        """Get user confirmation"""
        print("\n" + "=" * 70)
        print(prompt)
        print("=" * 70)
        response = input("Approve? (yes/no): ").strip().lower()
        return response in ["yes", "y"]

    def auto_approve(self, prompt: str) -> bool:
        """Auto-approve (used in daemon mode with sandbox scope)"""
        # In sandbox mode, only approve safe operations
        safe_keywords = ["package", "alias", "function", "home-manager"]
        return any(kw in prompt.lower() for kw in safe_keywords)

    def handle_query(self, query: str) -> Dict[str, Any]:
        """Route query to appropriate write tool"""
        query_lower = query.lower()

        # Home Manager package installation
        if "install" in query_lower and "hm" in query_lower:
            pkg_name = query.split("install")[-1].strip()
            config = f'home.packages = with pkgs; [ {pkg_name} ];'
            return self.hm_tools.propose_hm_config(
                config,
                f"Install {pkg_name} via Home Manager"
            )

        # System rebuild
        if "rebuild" in query_lower:
            if "switch" in query_lower:
                return self.rebuild_tools.propose_rebuild_switch(query)
            elif "test" in query_lower:
                return self.rebuild_tools.propose_rebuild_test(query)
            else:
                return self.rebuild_tools.dry_activate()

        # Flake module update
        if "add module" in query_lower or "create module" in query_lower:
            return {"note": "Flake module creation requires manual code review"}

        return {"error": "Query type not recognized"}

    def get_sandbox_status(self) -> Dict[str, Any]:
        """Report current sandbox scope"""
        return {
            "interactive_mode": self.interactive,
            "sandbox_scope": {
                "safe": ["home-manager packages", "shell aliases", "functions"],
                "unsafe": ["system rebuild switch", "security changes", "systemd units"]
            },
            "pending_changes": len(self.write_gate.pending_changes)
        }

    def rollback_pending(self) -> Dict[str, Any]:
        """Rollback all pending changes"""
        count = len(self.write_gate.pending_changes)
        self.write_gate.rollback_all()
        return {"rolled_back": count, "message": f"Rolled back {count} changes"}

    def commit_session(self) -> Dict[str, Any]:
        """Finalize session (all changes already applied on confirmation)"""
        applied = sum(1 for c in self.write_gate.pending_changes if c.confirmed)
        return {
            "session_complete": True,
            "changes_applied": applied,
            "total_proposed": len(self.write_gate.pending_changes)
        }
