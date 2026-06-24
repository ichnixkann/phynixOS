{ config, pkgs, lib, ... }:
{
  boot = {
    loader = {
      grub.enable = true;
      grub.device = lib.mkDefault "/dev/vda";
    };
    kernelPackages = pkgs.linuxPackages_latest;
  };
}
