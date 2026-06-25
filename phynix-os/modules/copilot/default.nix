{ config, pkgs, lib, phynixPackages ? null, ... }:

# The copilot derivation lives in the flake (see flake.nix) so the
# module and the published package never drift. `phynixPackages` is
# passed through `specialArgs` by nixosSystem; for the rare case the
# module is consumed outside the flake we fall back to building it
# in-tree from the same source.
let
  phynix-copilot =
    if phynixPackages != null then phynixPackages.phynix-copilot
    else pkgs.python3Packages.buildPythonApplication {
      pname = "phynix-copilot";
      version = "0.0.0-fallback";
      format = "other";
      src = ../../pkgs/phynix-copilot;
      propagatedBuildInputs = with pkgs.python3Packages; [ requests pydantic ];
      postInstall = ''
        mkdir -p $out/bin
        cp cli.py $out/bin/pcopilot
        chmod +x $out/bin/pcopilot
      '';
    };
in
{
  options.phynix.copilot.enable = lib.mkEnableOption "PHYNIX Copilot service";

  config = lib.mkIf config.phynix.copilot.enable {
    # NixOS systemd-user-service syntax (not Home Manager): the Unit /
    # Service / Install sections live at the top level as lowercase
    # attrs, with raw [Unit]/[Service] options going under
    # `unitConfig` / `serviceConfig`.
    systemd.user.services.phynix-copilot = {
      description = "PHYNIX OS Copilot — AI Assistant for NixOS Configuration";
      after = [ "graphical-session-pre.target" ];
      partOf = [ "graphical-session.target" ];
      wantedBy = [ "graphical-session.target" ];

      environment.PHYNIX_DAEMON = "1";

      serviceConfig = {
        Type = "simple";
        ExecStart = "${phynix-copilot}/bin/pcopilot";
        Restart = "on-failure";
        RestartSec = 5;
        StandardOutput = "journal";
        StandardError = "journal";
      };
    };

    environment.systemPackages = [
      phynix-copilot
      pkgs.ollama
    ];
  };
}
