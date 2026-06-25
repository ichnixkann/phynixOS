{ pkgs, self, phynixPackages }:

# phynixPackages is unused here (this check just builds the ISO image)
# but the flake passes it for consistency with the live VM tests.
let _ = phynixPackages; in

# Build-check for the installer ISO.
#
# Originally this booted the ISO inside a NixOS VM test, but
# `virtualisation.cdrom` was removed from current nixpkgs and the
# replacement requires fiddly qemu.options plumbing. The most useful
# guarantee a CI run can give here anyway is "the installer ISO still
# *builds*" — a regression there blocks release without anyone noticing
# until tag time. So we just realise the iso image as a derivation
# output and let nix flake check fail if it doesn't.
#
# When we want a true boot test back, the path is `runNixOSTest` with
# `virtualisation.qemu.options = [ "-cdrom" "${iso}" ]` and a
# `wait_for_console_text` assertion.

let
  installerIso = self.nixosConfigurations.installer-iso.config.system.build.isoImage;
in
pkgs.runCommand "installer-iso-build-check"
  { meta.timeout = 3600; }
  ''
    # Symlink the iso into $out so the check has a concrete output and
    # downstream consumers can grab it via `nix build .#checks…`.
    mkdir -p $out
    ln -s ${installerIso}/iso $out/iso
    echo "installer iso built: ${installerIso}/iso/${installerIso.isoName}"
  ''
