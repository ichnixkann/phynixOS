#!/usr/bin/env python3
"""
PHYNIX Copilot CLI — pcopilot command
"""

import sys
import json
import argparse
from agent import PhynixCopilot


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

    args = parser.parse_args()

    copilot = PhynixCopilot()

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
