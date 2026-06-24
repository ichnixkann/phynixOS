#!/usr/bin/env python3
"""
PHYNIX Copilot CLI — pcopilot command
"""

import sys
import json
import argparse
from pathlib import Path
from agent import PhynixCopilot
from evolution import EvolutionManager
from completions import CompletionGenerator


def main():
    parser = argparse.ArgumentParser(
        description="PHYNIX Copilot — NixOS Configuration Assistant",
        prog="pcopilot"
    )

    parser.add_argument(
        "query",
        nargs="?",
        help="Query to process (interactive mode if omitted)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )
    parser.add_argument(
        "--audit-log",
        action="store_true",
        help="Show audit log"
    )
    parser.add_argument(
        "--backend",
        action="store_true",
        help="Show LLM backend info"
    )
    parser.add_argument(
        "--tui",
        action="store_true",
        help="Launch Textual UI"
    )
    parser.add_argument(
        "--generate-completions",
        metavar="DIR",
        help="Generate shell completions in directory"
    )
    parser.add_argument(
        "--evolution-status",
        action="store_true",
        help="Show agent evolution status"
    )

    args = parser.parse_args()

    copilot = PhynixCopilot()

    if args.tui:
        try:
            from tui import PhynixCopilotTUI
            app = PhynixCopilotTUI()
            app.run()
        except ImportError:
            print("Error: textual not installed. Install with: pip install textual", file=sys.stderr)
            return 1
        return 0

    if args.generate_completions:
        gen = CompletionGenerator()
        output_path = Path(args.generate_completions)
        files = gen.generate_completion_files(output_path)
        print(f"✓ Generated completions in {output_path}")
        print(f"  Bash: {files['bash']}")
        print(f"  Fish: {files['fish']}")
        print(f"  Fish Functions: {files['functions']}")
        return 0

    if args.evolution_status:
        agent_dir = Path(__file__).parent
        evolution = EvolutionManager(agent_dir)
        history = evolution.get_evolution_history(limit=5)
        print("Evolution History:")
        for entry in history:
            print(f"  {entry['timestamp']}: {entry['description']}")
        return 0

    if args.backend:
        print(f"LLM Backend: {copilot.llm_backend}")
        return 0

    if args.audit_log:
        try:
            with open(copilot.audit_log, "r") as f:
                for line in f.readlines()[-20:]:  # Last 20 entries
                    print(line.strip())
        except FileNotFoundError:
            print("No audit log found", file=sys.stderr)
        return 0

    if args.query:
        # Single query mode
        result = copilot.process_query(args.query)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            # Pretty print
            print(f"Query: {result['query']}")
            print(f"Backend: {result['backend']}")
            if "tool" in result.get("response", {}):
                print(f"Tool: {result['response']['tool']}")
            print()
            print(result.get("rag_context", ""))
        return 0

    # Interactive mode
    copilot.run_interactive()
    return 0


if __name__ == "__main__":
    sys.exit(main())
