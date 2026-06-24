{ config, pkgs, ... }:
{
  networking = {
    networkmanager.enable = true;
    firewall.enable = true;
  };

  services.openssh.enable = false;
}
