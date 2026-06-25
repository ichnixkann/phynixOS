---
name: test-harness-fix-or-extension
description: Workflow command scaffold for test-harness-fix-or-extension in phynixOS.
allowed_tools: ["Bash", "Read", "Write", "Grep", "Glob"]
---

# /test-harness-fix-or-extension

Use this workflow when working on **test-harness-fix-or-extension** in `phynixOS`.

## Goal

Fixes or extends the test harness for NixOS VM or Python tests, often in response to CI failures or new test requirements. Involves changes to test/lib.nix, test files, and sometimes flake.nix wiring.

## Common Files

- `phynix-os/tests/lib.nix`
- `phynix-os/tests/*.nix`
- `phynix-os/flake.nix`
- `phynix-os/tests/README.md`
- `phynix-os/pkgs/phynix-copilot/tests/*.py`

## Suggested Sequence

1. Understand the current state and failure mode before editing.
2. Make the smallest coherent change that satisfies the workflow goal.
3. Run the most relevant verification for touched files.
4. Summarize what changed and what still needs review.

## Typical Commit Signals

- Edit phynix-os/tests/lib.nix to fix or extend test harness logic.
- Update or add phynix-os/tests/*.nix test files.
- Update phynix-os/flake.nix to adjust test wiring or arguments.
- Update phynix-os/tests/README.md to document changes.
- Sometimes update Python test files under phynix-os/pkgs/phynix-copilot/tests/.

## Notes

- Treat this as a scaffold, not a hard-coded script.
- Update the command if the workflow evolves materially.