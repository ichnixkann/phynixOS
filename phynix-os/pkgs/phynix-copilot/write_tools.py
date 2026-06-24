"""
PHYNIX Copilot Write-Mode Tools
Mutation operations with confirmation gates and rollback capability
"""

import subprocess
import json
from pathlib import Path
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass


@dataclass
class Change:
    """Represents a proposed change"""
    file: str
    operation: str  # "modify", "create", "delete"
    before: Optional[str]
    after: Optional[str]
    reason: str
    confirmed: bool = False


class WriteGate:
    """Confirmation gate for write operations"""

    def __init__(self, callback: Optional[Callable[[str], bool]] = None):
        self.callback = callback or self.interactive_confirm
        self.pending_changes: list[Change] = []

    def interactive_confirm(self, diff: str) -> bool:
        """Interactive confirmation in terminal"""
        print("\n" + "=" * 60)
        print("PROPOSED CHANGE")
        print("=" * 60)
        print(diff)
        print("=" * 60)
        response = input("Approve? (yes/no): ").strip().lower()
        return response in ["yes", "y"]

    def propose_change(self, change: Change) -> bool:
        """Propose a change, await confirmation"""
        diff = self._format_diff(change)
        confirmed = self.callback(diff)
        change.confirmed = confirmed
        self.pending_changes.append(change)
        return confirmed

    def _format_diff(self, change: Change) -> str:
        """Format change as unified diff"""
        if change.operation == "create":
            return f"+ {change.file} (new file)\n{change.after}"
        elif change.operation == "delete":
            return f"- {change.file} (deleted)\n{change.before}"
        else:  # modify
            return f"~ {change.file}\n--- {change.before}\n+++ {change.after}"

    def rollback_all(self):
        """Rollback all applied changes"""
        for change in reversed(self.pending_changes):
            if change.confirmed:
                self._apply_rollback(change)
        self.pending_changes.clear()

    def _apply_rollback(self, change: Change):
        """Apply rollback for single change"""
        file_path = Path(change.file)
        if change.operation == "create":
            file_path.unlink()
        elif change.operation == "delete":
            file_path.write_text(change.before)
        else:  # modify
            file_path.write_text(change.before)


class FlakeTools:
    """Tools for modifying flake.nix and modules"""

    def __init__(self, write_gate: WriteGate, flake_dir: Path):
        self.gate = write_gate
        self.flake_dir = flake_dir

    def add_package(self, name: str, nix_expr: str, reason: str) -> Dict[str, Any]:
        """Propose adding package to flake"""
        # Parse and modify flake.nix
        flake_path = self.flake_dir / "flake.nix"
        before = flake_path.read_text()

        # Simple insertion (real impl would parse Nix AST)
        after = before.replace(
            "packages.phynix-copilot",
            f"packages.{name} = {nix_expr};\n\n    packages.phynix-copilot"
        )

        change = Change(
            file=str(flake_path),
            operation="modify",
            before=before,
            after=after,
            reason=reason
        )

        if self.gate.propose_change(change):
            flake_path.write_text(after)
            return {"success": True, "package": name}
        return {"success": False, "reason": "User rejected"}

    def update_module(self, module_path: str, config: Dict[str, Any], reason: str) -> Dict[str, Any]:
        """Propose updating NixOS module"""
        module_file = self.flake_dir / module_path
        if not module_file.exists():
            return {"error": f"Module {module_path} not found"}

        before = module_file.read_text()
        # Placeholder: Real implementation would modify module config
        after = before + f"\n# Updated: {reason}\n"

        change = Change(
            file=str(module_file),
            operation="modify",
            before=before,
            after=after,
            reason=reason
        )

        if self.gate.propose_change(change):
            module_file.write_text(after)
            return {"success": True, "module": module_path}
        return {"success": False, "reason": "User rejected"}


class HomeManagerTools:
    """Tools for Home Manager autonomous configuration"""

    def __init__(self, write_gate: WriteGate):
        self.gate = write_gate

    def propose_hm_config(self, config_snippet: str, reason: str) -> Dict[str, Any]:
        """Propose Home Manager configuration change"""
        hm_config = Path.home() / ".config/home-manager/home.nix"

        if not hm_config.exists():
            return {"error": "Home Manager config not found"}

        before = hm_config.read_text()
        after = before + f"\n# Auto-suggested: {reason}\n{config_snippet}\n"

        change = Change(
            file=str(hm_config),
            operation="modify",
            before=before,
            after=after,
            reason=reason
        )

        if self.gate.propose_change(change):
            hm_config.write_text(after)
            return {"success": True, "applied": True}
        return {"success": False, "reason": "User rejected"}

    def apply_hm_auto(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Auto-apply Home Manager changes within sandbox scope
        Safe scope: package installs, aliases, functions
        Unsafe scope: systemd units, authentication
        """
        safe_keys = {"packages", "shellAliases", "shellFunctions", "programs"}
        unsafe_keys = {"systemd", "services", "security"}

        for key in config:
            if key in unsafe_keys:
                return {
                    "error": f"Unsafe operation: {key}",
                    "note": "Requires manual confirmation for security-sensitive changes"
                }

        try:
            result = subprocess.run(
                ["home-manager", "switch"],
                capture_output=True,
                text=True,
                timeout=60
            )
            return {
                "success": result.returncode == 0,
                "output": result.stderr if result.returncode != 0 else result.stdout
            }
        except Exception as e:
            return {"error": str(e)}


class NixosRebuildTools:
    """Tools for nixos-rebuild with safety gates"""

    def __init__(self, write_gate: WriteGate):
        self.gate = write_gate

    def dry_activate(self) -> Dict[str, Any]:
        """Test rebuild without activating"""
        try:
            result = subprocess.run(
                ["sudo", "nixos-rebuild", "dry-activate"],
                capture_output=True,
                text=True,
                timeout=300
            )
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "errors": result.stderr
            }
        except Exception as e:
            return {"error": str(e)}

    def propose_rebuild_test(self, reason: str) -> Dict[str, Any]:
        """Propose rebuilding and testing (requires confirmation)"""
        dry_result = self.dry_activate()

        if not dry_result.get("success"):
            return {
                "error": "Dry-activate failed",
                "output": dry_result.get("output", "")
            }

        # Propose actual rebuild
        prompt = f"""
Proposed System Rebuild
Reason: {reason}
Dry-activate: OK

This will activate new system configuration.
Changes will be active until next reboot or explicit switch.
        """

        confirmed = self.gate.callback(prompt)

        if confirmed:
            try:
                result = subprocess.run(
                    ["sudo", "nixos-rebuild", "test"],
                    capture_output=True,
                    text=True,
                    timeout=600
                )
                return {
                    "success": result.returncode == 0,
                    "output": result.stdout
                }
            except Exception as e:
                return {"error": str(e)}
        else:
            return {"success": False, "reason": "User rejected"}

    def propose_rebuild_switch(self, reason: str) -> Dict[str, Any]:
        """Propose rebuild and permanently switch (high-risk)"""
        dry_result = self.dry_activate()

        if not dry_result.get("success"):
            return {"error": "Dry-activate failed"}

        prompt = f"""
⚠️  PERMANENT SYSTEM REBUILD
Reason: {reason}

This will:
1. Rebuild NixOS with new configuration
2. Activate and set as default boot
3. Persist across reboots

Are you absolutely sure? (yes/no)
        """

        confirmed = self.gate.callback(prompt)

        if confirmed:
            try:
                result = subprocess.run(
                    ["sudo", "nixos-rebuild", "switch"],
                    capture_output=True,
                    text=True,
                    timeout=600
                )
                return {
                    "success": result.returncode == 0,
                    "output": result.stdout
                }
            except Exception as e:
                return {"error": str(e)}
        else:
            return {"success": False, "reason": "User rejected"}
