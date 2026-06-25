---
name: ci-pipeline-migration-or-refactor
description: Workflow command scaffold for ci-pipeline-migration-or-refactor in phynixOS.
allowed_tools: ["Bash", "Read", "Write", "Grep", "Glob"]
---

# /ci-pipeline-migration-or-refactor

Use this workflow when working on **ci-pipeline-migration-or-refactor** in `phynixOS`.

## Goal

Migrates or refactors the CI pipeline to use new infrastructure, runners, or caching solutions. Typically involves adding or removing workflow YAMLs, updating documentation, and adjusting Nix flake or module wiring.

## Common Files

- `.github/workflows/*.yml`
- `README.md`
- `phynix-os/README.md`
- `garnix.yaml`
- `hercules-ci.nix`
- `phynix-os/flake.nix`

## Suggested Sequence

1. Understand the current state and failure mode before editing.
2. Make the smallest coherent change that satisfies the workflow goal.
3. Run the most relevant verification for touched files.
4. Summarize what changed and what still needs review.

## Typical Commit Signals

- Add or remove .github/workflows/*.yml files to reflect new CI jobs.
- Add or remove infrastructure config files (e.g., garnix.yaml, hercules-ci.nix).
- Update flake.nix and related Nix files to wire in new checks/builds.
- Update README.md and phynix-os/README.md to document new CI pipeline.
- Remove obsolete infra/docs files (e.g., docs/infra/attic-deploy.md).

## Notes

- Treat this as a scaffold, not a hard-coded script.
- Update the command if the workflow evolves materially.