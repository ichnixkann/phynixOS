{ config, pkgs, home-manager, ... }:
{
  imports = [
    ./hardware-configuration.nix
    home-manager.nixosModules.home-manager
  ];

  boot.loader.grub.device = "/dev/sda";

  networking.hostName = "phynix-workstation";
  networking.networkmanager.enable = true;

  time.timeZone = "Europe/Berlin";
  i18n.defaultLocale = "de_DE.UTF-8";

  users.users.phynix = {
    isNormalUser = true;
    extraGroups = [ "wheel" "networkmanager" ];
    home = "/home/phynix";
  };

  home-manager.users.phynix = {
    home.stateVersion = "24.05";
  };

  system.stateVersion = "24.05";
}
