{ pkgs, self }:

# Boots a VM with the phynix core + copilot modules composed the same way
# the workstation host composes them, and asserts the system reaches
# multi-user.target with the copilot service registered for the phynix
# user.

let
  mkTest = import ./lib.nix { inherit pkgs self; };
in
mkTest {
  name = "boot-workstation";

  nodes.machine = { config, pkgs, ... }: {
    imports = [
      ../modules/core/default.nix
      ../modules/copilot/default.nix
    ];

    networking.hostName = "phynix-workstation";

    phynix.copilot.enable = true;

    # Host configs override the VM's loader; the test framework provides
    # its own boot path so we mkForce these out to nothing.
    boot.loader.grub.enable = pkgs.lib.mkForce false;

    # We have no live network in the sandbox; cut the NetworkManager
    # wait so multi-user.target doesn't stall.
    systemd.services.NetworkManager-wait-online.enable = false;
  };

  testScript = ''
    machine.start()
    machine.wait_for_unit("multi-user.target")

    # Hostname propagates from the module config.
    machine.succeed("hostname | grep -qx phynix-workstation")

    # The copilot CLI from the flake package is on PATH system-wide.
    machine.succeed("command -v pcopilot")
    machine.succeed("pcopilot --help >/dev/null")

    # The user-service unit is installed for the phynix user.
    machine.wait_until_succeeds("loginctl show-user phynix >/dev/null 2>&1 || loginctl enable-linger phynix")
    machine.succeed(
        "su - phynix -c 'systemctl --user list-unit-files phynix-copilot.service' "
        "| grep -q phynix-copilot"
    )
  '';
}
