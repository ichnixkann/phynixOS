{ config, pkgs, ... }:
{
  boot = {
    loader = {
      grub.enable = true;
      grub.device = "/dev/vda";
    };
    kernelPackages = pkgs.linuxPackages_latest;
  };
}
