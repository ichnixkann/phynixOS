"""
PHYNIX Copilot Self-Evolution Framework
Autonomous improvement with hot-reload and rollback capability
"""

import json
import subprocess
import sys
import importlib
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List


class EvolutionManager:
    """Manages agent self-improvement and hot-reloading"""

    def __init__(self, agent_dir: Path):
        self.agent_dir = agent_dir
        self.evolution_dir = agent_dir.parent / ".evolution"
        self.evolution_dir.mkdir(exist_ok=True)
        self.version_log = self.evolution_dir / "versions.jsonl"
        self.rollback_dir = self.evolution_dir / "backups"
        self.rollback_dir.mkdir(exist_ok=True)

    def analyze_performance(self, audit_log_path: Path, window: int = 100) -> Dict[str, Any]:
        """Analyze agent performance from audit log (last N entries)"""
        metrics = {
            "total_queries": 0,
            "successful_queries": 0,
            "failed_queries": 0,
            "avg_response_time": 0,
            "tool_usage": {},
            "error_patterns": [],
        }

        try:
            with open(audit_log_path, "r") as f:
                entries = [json.loads(line) for line in f.readlines()[-window:]]

            metrics["total_queries"] = len(entries)
            response_times = []

            for entry in entries:
                if entry.get("action") == "query_processed":
                    metrics["successful_queries"] += 1
                elif entry.get("action") == "error":
                    metrics["failed_queries"] += 1
                    metrics["error_patterns"].append(entry.get("details", {}).get("error"))

                if "tool" in entry.get("details", {}):
                    tool = entry["details"]["tool"]
                    metrics["tool_usage"][tool] = metrics["tool_usage"].get(tool, 0) + 1

            if metrics["total_queries"] > 0:
                metrics["success_rate"] = (
                    metrics["successful_queries"] / metrics["total_queries"]
                )

            return metrics
        except Exception as e:
            return {"error": str(e), **metrics}

    def propose_improvements(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Propose code improvements based on performance metrics"""
        proposals = []

        # Low success rate → improve error handling
        if metrics.get("success_rate", 0) < 0.8:
            proposals.append({
                "type": "error_handling",
                "priority": "high",
                "description": "Improve error handling — success rate below 80%",
                "target_file": "tools.py",
                "suggested_change": "Add retry logic and better exception handling"
            })

        # Many tool calls to same tool → optimize
        if metrics.get("tool_usage"):
            most_used = max(metrics["tool_usage"].items(), key=lambda x: x[1])
            if most_used[1] > metrics["total_queries"] * 0.5:
                proposals.append({
                    "type": "optimization",
                    "priority": "medium",
                    "description": f"Optimize {most_used[0]} — used in >50% of queries",
                    "target_file": "tools.py",
                    "suggested_change": f"Cache results for {most_used[0]}"
                })

        # Common errors → add handling
        if metrics.get("error_patterns"):
            common_error = max(set(metrics["error_patterns"]), key=metrics["error_patterns"].count)
            proposals.append({
                "type": "error_handling",
                "priority": "high",
                "description": f"Handle common error: {common_error[:50]}...",
                "target_file": "agent.py",
                "suggested_change": "Add specific exception handler"
            })

        return proposals

    def create_backup(self, file_path: Path) -> str:
        """Create backup of file before modification"""
        content = file_path.read_text()
        file_hash = hashlib.sha256(content.encode()).hexdigest()[:8]
        timestamp = datetime.now().isoformat()

        backup_name = f"{file_path.name}.{timestamp}.{file_hash}.bak"
        backup_path = self.rollback_dir / backup_name

        backup_path.write_text(content)
        return str(backup_path)

    def apply_improvement(
        self,
        file_path: Path,
        improvement_code: str,
        description: str
    ) -> Dict[str, Any]:
        """Apply improvement to file and track version"""
        try:
            # Backup original
            backup_path = self.create_backup(file_path)

            # Apply improvement
            file_path.write_text(improvement_code)

            # Record version
            version_entry = {
                "timestamp": datetime.now().isoformat(),
                "file": str(file_path.name),
                "description": description,
                "backup": backup_path,
                "status": "applied"
            }

            with open(self.version_log, "a") as f:
                f.write(json.dumps(version_entry) + "\n")

            return {"success": True, "backup": backup_path, "version_entry": version_entry}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def hot_reload_module(self, module_name: str) -> Dict[str, Any]:
        """Hot-reload Python module without stopping service"""
        try:
            if module_name in sys.modules:
                module = sys.modules[module_name]
                importlib.reload(module)
                return {"success": True, "module": module_name, "reloaded": True}
            else:
                return {"success": False, "error": f"Module {module_name} not loaded"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def rollback_to_backup(self, backup_path: str) -> Dict[str, Any]:
        """Rollback file to backup version"""
        try:
            backup_file = Path(backup_path)
            if not backup_file.exists():
                return {"success": False, "error": "Backup not found"}

            # Extract original file name
            original_name = backup_file.name.split(".")[0]
            original_path = self.agent_dir / original_name

            # Restore from backup
            original_path.write_text(backup_file.read_text())

            # Hot-reload if applicable
            if original_name.endswith(".py"):
                module_name = original_name[:-3]
                self.hot_reload_module(module_name)

            return {"success": True, "restored": str(original_path)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_evolution_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get evolution history"""
        try:
            with open(self.version_log, "r") as f:
                entries = [json.loads(line) for line in f.readlines()]
            return entries[-limit:]
        except FileNotFoundError:
            return []
