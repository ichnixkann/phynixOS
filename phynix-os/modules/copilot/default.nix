{ config, pkgs, lib, ... }:
let
  phynix-copilot = pkgs.python3Packages.buildPythonApplication {
    pname = "phynix-copilot";
    version = "0.1.0";
    src = ../../pkgs/phynix-copilot;

    propagatedBuildInputs = with pkgs.python3Packages; [
      requests
      pydantic
    ];

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
    systemd.user.services.phynix-copilot = {
      Unit = {
        Description = "PHYNIX OS Copilot — AI Assistant for NixOS Configuration";
        After = [ "graphical-session-pre.target" ];
        PartOf = [ "graphical-session.target" ];
      };

      Service = {
        Type = "simple";
        ExecStart = "${phynix-copilot}/bin/pcopilot";
        Environment = "PHYNIX_DAEMON=1";
        Restart = "on-failure";
        RestartSec = 5;
        StandardOutput = "journal";
        StandardError = "journal";
      };

      Install.WantedBy = [ "graphical-session.target" ];
    };

    environment.systemPackages = [
      phynix-copilot
      pkgs.ollama
    ];
  };
}
