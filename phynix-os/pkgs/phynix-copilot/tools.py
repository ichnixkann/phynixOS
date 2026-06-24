"""
PHYNIX Copilot Tools — Read-only Nix operations
"""

import subprocess
import json
from pathlib import Path
from typing import Optional, Dict, Any


class NixTools:
    """Tools for read-only Nix operations"""

    @staticmethod
    def nix_search(query: str) -> Dict[str, Any]:
        """Search nixpkgs for packages matching query"""
        try:
            result = subprocess.run(
                ["nix", "search", "nixpkgs", query, "--json"],
                capture_output=True,
                text=True,
                timeout=15
            )
            if result.returncode == 0:
                return json.loads(result.stdout)
            return {"error": result.stderr}
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def nix_eval(expr: str) -> Dict[str, Any]:
        """Evaluate Nix expression (dry-run, no import)"""
        try:
            result = subprocess.run(
                ["nix", "eval", "--json", "--expr", expr],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                return {"value": result.stdout.strip()}
            return {"error": result.stderr}
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def nix_flake_check() -> Dict[str, Any]:
        """Check flake.nix for errors"""
        try:
            result = subprocess.run(
                ["nix", "flake", "check"],
                capture_output=True,
                text=True,
                timeout=30
            )
            return {"success": result.returncode == 0, "output": result.stderr}
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def read_file(path: str) -> Dict[str, Any]:
        """Read file content (audit-safe)"""
        try:
            p = Path(path).resolve()
            # Safety: only allow reading from home/phynix-flake
            if not str(p).startswith(str(Path.home())):
                return {"error": "Access denied: only home directory allowed"}
            if p.is_file() and p.stat().st_size < 1_000_000:  # Max 1MB
                return {"content": p.read_text()}
            return {"error": "File not readable or too large"}
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def nix_store_info(path: Optional[str] = None) -> Dict[str, Any]:
        """Get Nix store information"""
        try:
            if path:
                result = subprocess.run(
                    ["nix", "path-info", path],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
            else:
                result = subprocess.run(
                    ["nix", "store", "info"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
            if result.returncode == 0:
                return {"info": result.stdout}
            return {"error": result.stderr}
        except Exception as e:
            return {"error": str(e)}


class HyprlandTools:
    """Tools for querying Hyprland state (read-only)"""

    @staticmethod
    def hyprctl_command(cmd: str) -> Dict[str, Any]:
        """Execute hyprctl command (safe subset)"""
        safe_commands = ["clients", "workspaces", "monitors", "binds"]
        if not any(cmd.startswith(sc) for sc in safe_commands):
            return {"error": "Command not allowed"}

        try:
            result = subprocess.run(
                ["hyprctl", cmd],
                capture_output=True,
                text=True,
                timeout=5
            )
            return {"output": result.stdout if result.returncode == 0 else result.stderr}
        except Exception as e:
            return {"error": str(e)}


class SystemTools:
    """Tools for system introspection (read-only)"""

    @staticmethod
    def systemctl_status(unit: str) -> Dict[str, Any]:
        """Check systemd unit status"""
        try:
            result = subprocess.run(
                ["systemctl", "status", unit, "--user"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return {"status": result.stdout}
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def journalctl_tail(unit: str, lines: int = 20) -> Dict[str, Any]:
        """Tail journalctl for unit"""
        try:
            result = subprocess.run(
                ["journalctl", "--user", "-u", unit, f"-n={lines}"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return {"logs": result.stdout}
        except Exception as e:
            return {"error": str(e)}
