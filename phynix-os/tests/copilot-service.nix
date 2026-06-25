{ pkgs, self, phynixPackages }:

# Minimal VM that enables only the phynix.copilot module, then asserts
# the user service starts cleanly and `pcopilot --backend` exits 0 with
# no LLM available (should report "offline", not crash).

let
  mkTest = import ./lib.nix { inherit pkgs self phynixPackages; };
in
mkTest {
  name = "copilot-service";

  nodes.machine = { config, pkgs, ... }: {
    imports = [
      ../modules/copilot/default.nix
    ];

    phynix.copilot.enable = true;

    # Enable lingering so user-services start without a graphical login.
    systemd.tmpfiles.rules = [
      "f /var/lib/systemd/linger/phynix 0644 root root - -"
    ];

    systemd.services.NetworkManager-wait-online.enable = false;
  };

  testScript = ''
    machine.start()
    machine.wait_for_unit("multi-user.target")
    machine.wait_until_succeeds("loginctl show-user phynix >/dev/null 2>&1")

    # pcopilot is on PATH system-wide.
    machine.succeed("command -v pcopilot")

    # --backend probes for HF_TOKEN / ollama; with neither present it
    # must print "offline" (or similar) and exit 0, NOT raise.
    out = machine.succeed("runuser -u phynix -- pcopilot --backend")
    assert out.strip(), f"pcopilot --backend produced no output: {out!r}"

    # The systemd user unit is reachable.
    machine.succeed(
        "runuser -u phynix -- "
        "systemctl --user list-unit-files phynix-copilot.service "
        "| grep -q phynix-copilot"
    )
  '';
}
