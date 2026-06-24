{ config, pkgs, lib, ... }:
{
  options.phynix.copilot.enable = lib.mkEnableOption "PHYNIX Copilot service";

  config = lib.mkIf config.phynix.copilot.enable {
    systemd.user.services.phynix-copilot = {
      Unit = {
        Description = "PHYNIX OS Copilot — AI Assistant for NixOS Configuration";
        After = [ "graphical-session-pre.target" ];
        PartOf = [ "graphical-session.target" ];
      };

      Service = {
        Type = "simple";
        ExecStart = "${pkgs.python3}/bin/python3 %h/.local/share/phynix/copilot/agent.py";
        Restart = "on-failure";
        RestartSec = 5;
        StandardOutput = "journal";
        StandardError = "journal";
      };

      Install.WantedBy = [ "graphical-session.target" ];
    };

    environment.systemPackages = with pkgs; [
      python3
      python3Packages.pip
      ollama
    ];

    phynix.copilot.enable = true;
  };
}
