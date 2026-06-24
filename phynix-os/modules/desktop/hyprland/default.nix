{ config, pkgs, lib, ... }:
{
  imports = [
    ./hyprland.nix
    ./waybar.nix
    ./mako.nix
  ];

  programs.dconf.enable = true;

  services.greetd = {
    enable = true;
    settings = {
      default_session = {
        command = "${pkgs.greetd.tuigreet}/bin/tuigreet --time --time-format '%R' --cmd Hyprland";
        user = "greeter";
      };
    };
  };

  environment.systemPackages = with pkgs; [
    wofi
    swaylock
    wl-clipboard
  ];
}
