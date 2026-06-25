# Live VM tests

Hermetic NixOS VM tests, exposed as flake `checks.x86_64-linux.*`. They
boot a real kernel + systemd in QEMU/KVM, drive it from a Python script,
assert on the result, and tear down. Same primitive `nixpkgs` itself
uses (`pkgs.testers.runNixOSTest`).

## Run everything

```bash
nix flake check ./phynix-os -L
```

First run is slow (downloads kernels); afterwards everything is cached
in `cache.nixos.org` + our Attic cache.

## Run one test

```bash
nix build ./phynix-os#checks.x86_64-linux.boot-workstation -L
```

## Drive a VM interactively

Useful when a test fails and you want to poke around:

```bash
nix build ./phynix-os#checks.x86_64-linux.boot-workstation.driverInteractive
./result/bin/nixos-test-driver --interactive
# Inside the Python REPL:
# >>> machine.start()
# >>> machine.wait_for_unit("multi-user.target")
# >>> machine.shell_interact()   # drops into the VM's shell
```

## Current tests

| Test | What it covers |
|------|----------------|
| `boot-workstation`   | Core + copilot modules compose, system reaches `multi-user.target`, `pcopilot` on PATH |
| `copilot-service`    | `phynix-copilot.service` registers for the phynix user; `pcopilot --backend` exits 0 with no LLM |
| `installer-iso-boot` | Installer ISO actually boots and the TUI installer binary is present |
| `python-unit`        | The pytest suite under `pkgs/phynix-copilot/tests/` |

## Adding a test

1. Copy one of `*.nix` here as a starting point.
2. Use `./lib.nix` so you inherit the phynix defaults (user, memory,
   journal config).
3. Wire it into `checks.x86_64-linux.<name>` in `phynix-os/flake.nix`.
4. Run it locally with `nix build .#checks.x86_64-linux.<name> -L`.
5. Push — Hercules CI will build it on the PR.
