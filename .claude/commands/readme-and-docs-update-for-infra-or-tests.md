---
name: readme-and-docs-update-for-infra-or-tests
description: Workflow command scaffold for readme-and-docs-update-for-infra-or-tests in phynixOS.
allowed_tools: ["Bash", "Read", "Write", "Grep", "Glob"]
---

# /readme-and-docs-update-for-infra-or-tests

Use this workflow when working on **readme-and-docs-update-for-infra-or-tests** in `phynixOS`.

## Goal

Updates documentation and README files to reflect changes in CI infrastructure, test suites, or workflows. Ensures users are informed about new processes or requirements.

## Common Files

- `README.md`
- `phynix-os/README.md`
- `docs/infra/*.md`

## Suggested Sequence

1. Understand the current state and failure mode before editing.
2. Make the smallest coherent change that satisfies the workflow goal.
3. Run the most relevant verification for touched files.
4. Summarize what changed and what still needs review.

## Typical Commit Signals

- Edit README.md and/or phynix-os/README.md to describe new CI/test setup.
- Update or add docs/infra/*.md for new infrastructure or deployment steps.
- Rename or update references to test names or workflows in documentation.

## Notes

- Treat this as a scaffold, not a hard-coded script.
- Update the command if the workflow evolves materially.