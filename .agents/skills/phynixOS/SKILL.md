```markdown
# phynixOS Development Patterns

> Auto-generated skill from repository analysis

## Overview

This skill teaches you how to contribute effectively to the **phynixOS** codebase, a Python-based project with a strong focus on NixOS infrastructure, continuous integration (CI), and modular test harnesses. You'll learn the project's coding conventions, typical workflows for CI and test infrastructure updates, documentation practices, and how to handle flake and module wiring. The guide includes step-by-step workflow instructions, code examples, and suggested commands for common tasks.

---

## Coding Conventions

**File Naming**
- Use **camelCase** for Python files and scripts.
  - Example: `myModule.py`, `testRunner.py`

**Import Style**
- Prefer **relative imports** within Python modules.
  - Example:
    ```python
    from .utils import get_config
    ```

**Export Style**
- Use **named exports**; explicitly define what is exported from each module.
  - Example:
    ```python
    __all__ = ["MyClass", "helper_function"]
    ```

**Commit Patterns**
- Mixed commit types with prefixes such as: `tests`, `ci`, `fix`, `docs`, `license`
- Commit messages are concise (average ~64 characters).

---

## Workflows

### ci-pipeline-migration-or-refactor
**Trigger:** When switching CI providers, updating build/test infrastructure, or changing caching/mirroring strategies.  
**Command:** `/migrate-ci`

1. Add or remove `.github/workflows/*.yml` files to reflect new CI jobs.
2. Add or remove infrastructure config files (e.g., `garnix.yaml`, `hercules-ci.nix`).
3. Update `flake.nix` and related Nix files to wire in new checks/builds.
4. Update `README.md` and `phynix-os/README.md` to document the new CI pipeline.
5. Remove obsolete infra/docs files (e.g., `docs/infra/attic-deploy.md`).

**Example:**
```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: nix build .#checks.x86_64-linux
```

---

### test-harness-fix-or-extension
**Trigger:** When fixing test harness bugs, adapting to upstream NixOS changes, or extending test coverage.  
**Command:** `/fix-test-harness`

1. Edit `phynix-os/tests/lib.nix` to fix or extend test harness logic.
2. Update or add `phynix-os/tests/*.nix` test files.
3. Update `phynix-os/flake.nix` to adjust test wiring or arguments.
4. Update `phynix-os/tests/README.md` to document changes.
5. (Sometimes) Update Python test files under `phynix-os/pkgs/phynix-copilot/tests/`.

**Example:**
```nix
# phynix-os/tests/lib.nix
{ pkgs, ... }:
{
  testFunction = { config, ... }: {
    # test logic here
  };
}
```

---

### readme-and-docs-update-for-infra-or-tests
**Trigger:** When CI/test setup or infrastructure changes require documentation updates.  
**Command:** `/update-docs`

1. Edit `README.md` and/or `phynix-os/README.md` to describe new CI/test setup.
2. Update or add `docs/infra/*.md` for new infrastructure or deployment steps.
3. Rename or update references to test names or workflows in documentation.

**Example:**
```markdown
## Continuous Integration

phynixOS uses GitHub Actions for CI. See `.github/workflows/ci.yml` for configuration.
```

---

### flake-nix-wiring-and-module-arg-refactor
**Trigger:** When fixing module argument passing, syncing package versions, or resolving flake evaluation errors.  
**Command:** `/refactor-flake-wiring`

1. Edit `phynix-os/flake.nix` to adjust how packages or arguments are passed to modules/tests.
2. Edit `phynix-os/modules/*/default.nix` to update argument handling or drop fallback branches.
3. Edit `phynix-os/tests/lib.nix` and test files to receive new arguments.
4. Update related test files to forward or use the new arguments.

**Example:**
```nix
# phynix-os/flake.nix
outputs = { self, nixpkgs }: {
  packages.x86_64-linux = import ./modules/core/default.nix {
    inherit nixpkgs;
    customArg = "value";
  };
};
```

---

## Testing Patterns

- **Framework:** Not explicitly detected; Python test files exist, and NixOS VM tests are used.
- **Test File Pattern:** Python tests under `phynix-os/pkgs/phynix-copilot/tests/*.py`, Nix tests under `phynix-os/tests/*.nix`.
- **Test Naming:** Use `.test.ts` for TypeScript (if present), otherwise `.py` or `.nix` as appropriate.
- **Typical Test Example (Python):**
    ```python
    import unittest
    from .myModule import my_function

    class TestMyFunction(unittest.TestCase):
        def test_basic(self):
            self.assertEqual(my_function(2), 4)
    ```
- **Typical Test Example (Nix):**
    ```nix
    { lib, ... }:
    {
      test = lib.testFunction { ... };
    }
    ```

---

## Commands

| Command               | Purpose                                                      |
|-----------------------|--------------------------------------------------------------|
| /migrate-ci           | Migrate or refactor the CI pipeline and infrastructure       |
| /fix-test-harness     | Fix or extend the test harness for NixOS VM or Python tests  |
| /update-docs          | Update documentation and READMEs for infra or test changes   |
| /refactor-flake-wiring| Refactor flake.nix and module arguments/wiring               |
```
