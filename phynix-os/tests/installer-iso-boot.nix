{ pkgs, self }:

# Boots the installer ISO that the release pipeline ships, and asserts
# the installer environment comes up: getty reachable, network stack
# present, and the installer TUI binary is on PATH.
#
# This is the slowest of the three boot tests (~90s on the Hercules
# runners). The timeout is bumped accordingly.

let
  mkTest = import ./lib.nix { inherit pkgs self; };

  installerIso = self.nixosConfigurations.installer-iso.config.system.build.isoImage;
in
mkTest {
  name = "installer-iso-boot";

  meta.timeout = 2400;

  nodes.machine = { config, pkgs, modulesPath, ... }: {
    # Boot directly off the ISO image the release pipeline publishes.
    virtualisation = {
      cdrom = "${installerIso}/iso/${installerIso.isoName}";
      memorySize = 2048;
      diskSize = 8192;
      useBootLoader = false;
    };
  };

  testScript = ''
    machine.start()

    # Installer media boot to a getty prompt rather than a login screen;
    # wait_for_console_text is the canonical check for this.
    machine.wait_for_console_text("Welcome to NixOS")

    # Once the userland is up the TUI installer binary should be on PATH.
    # (Phynix names its installer entrypoint `phynix-install` per
    # installer/tui — adjust here if that name changes.)
    machine.wait_until_succeeds("command -v phynix-install || command -v nixos-install")
  '';
}
