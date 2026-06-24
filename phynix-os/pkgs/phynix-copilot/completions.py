"""
PHYNIX Copilot Shell Completions
Auto-generate bash and fish completions from tool registry
"""

import json
from pathlib import Path
from typing import Dict, List, Any


class CompletionGenerator:
    """Generate shell completions from tool definitions"""

    def __init__(self, tools_module=None):
        self.tools = {
            "nix_search": {
                "description": "Search nixpkgs for packages",
                "args": [{"name": "query", "type": "string"}]
            },
            "nix_eval": {
                "description": "Evaluate Nix expression",
                "args": [{"name": "expr", "type": "string"}]
            },
            "nix_flake_check": {
                "description": "Check flake.nix for errors",
                "args": []
            },
            "systemctl_status": {
                "description": "Check systemd unit status",
                "args": [{"name": "unit", "type": "string"}]
            },
            "journalctl_tail": {
                "description": "View journalctl logs",
                "args": [{"name": "unit", "type": "string"}, {"name": "lines", "type": "int"}]
            },
        }

    def generate_bash_completion(self) -> str:
        """Generate bash completion script"""
        script = """#!/bin/bash
# PHYNIX Copilot bash completions
_pcopilot_completions() {
    local cur prev words cword
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    # Options
    local options="--json --audit-log --backend --help"

    # Commands/queries
    local commands="search eval check status logs"

    # Complete options
    if [[ ${cur} == -* ]] ; then
        COMPREPLY=( $(compgen -W "${options}" -- ${cur}) )
        return 0
    fi

    # Complete commands
    COMPREPLY=( $(compgen -W "${commands}" -- ${cur}) )
}

complete -F _pcopilot_completions pcopilot
"""
        return script

    def generate_fish_completion(self) -> str:
        """Generate fish completion script"""
        script = """#!/usr/bin/env fish
# PHYNIX Copilot fish completions

# Tool descriptions
set -l tools 'nix_search' 'nix_eval' 'nix_flake_check' 'systemctl_status' 'journalctl_tail'

# Main command
complete -c pcopilot -f -d "PHYNIX Copilot — NixOS Configuration Assistant"

# Options
complete -c pcopilot -l json -d "Output as JSON"
complete -c pcopilot -l audit-log -d "Show audit log"
complete -c pcopilot -l backend -d "Show LLM backend info"
complete -c pcopilot -l help -d "Show help message"

# Query suggestions based on common patterns
complete -c pcopilot -n "__fish_seen_subcommand_from search" -d "Search nixpkgs"
complete -c pcopilot -n "__fish_seen_subcommand_from eval" -d "Evaluate Nix expression"
complete -c pcopilot -n "__fish_seen_subcommand_from check" -d "Check flake.nix"
complete -c pcopilot -n "__fish_seen_subcommand_from status" -d "Check system status"
complete -c pcopilot -n "__fish_seen_subcommand_from logs" -d "View logs"
"""
        return script

    def generate_fish_functions(self) -> str:
        """Generate fish shell functions"""
        functions = """#!/usr/bin/env fish
# PHYNIX Copilot fish functions

# pcopilot wrapper with pretty output
function pcopilot --description "PHYNIX Copilot query"
    set -l args $argv

    # Check if interactive
    if test -z "$args"
        echo "🤖 PHYNIX Copilot — Interactive Mode"
        command pcopilot
    else if test "$args[1]" = "--help"
        echo "PHYNIX Copilot — NixOS Configuration Assistant"
        echo ""
        echo "Usage: pcopilot [OPTIONS] [QUERY]"
        echo ""
        echo "Options:"
        echo "  --json          Output as JSON"
        echo "  --audit-log     Show audit log"
        echo "  --backend       Show LLM backend info"
        echo "  --help          Show this message"
        echo ""
        echo "Examples:"
        echo "  pcopilot search ripgrep"
        echo "  pcopilot --backend"
    else
        echo "🔍 Query: $args"
        command pcopilot $args
    end
end

# Helper functions
function pcopilot_audit --description "View PHYNIX Copilot audit log"
    command pcopilot --audit-log
end

function pcopilot_backend --description "Show PHYNIX Copilot LLM backend"
    command pcopilot --backend
end
"""
        return functions

    def generate_completion_files(self, output_dir: Path):
        """Generate and save all completion files"""
        output_dir.mkdir(parents=True, exist_ok=True)

        # Bash completion
        bash_file = output_dir / "pcopilot.bash"
        bash_file.write_text(self.generate_bash_completion())
        bash_file.chmod(0o755)

        # Fish completion
        fish_file = output_dir / "pcopilot.fish"
        fish_file.write_text(self.generate_fish_completion())
        fish_file.chmod(0o755)

        # Fish functions
        functions_file = output_dir / "conf.d" / "pcopilot.fish"
        functions_file.parent.mkdir(parents=True, exist_ok=True)
        functions_file.write_text(self.generate_fish_functions())
        functions_file.chmod(0o755)

        return {
            "bash": str(bash_file),
            "fish": str(fish_file),
            "functions": str(functions_file)
        }
