{ config, pkgs, lib, phynixPackages, ... }:

# The copilot derivation lives in the flake (see flake.nix). The flake's
# nixosSystem and the tests' lib.nix both inject `phynixPackages` via
# `specialArgs` / `_module.args`, guaranteeing the module and the
# published package never drift. There is no fallback: importing this
# module without phynixPackages is a configuration error and should
# fail loudly at eval time.
let
  phynix-copilot = phynixPackages.phynix-copilot;
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
