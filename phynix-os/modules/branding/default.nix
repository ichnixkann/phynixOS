{ config, pkgs, lib, ... }:
{
  imports = [
    ./plymouth.nix
    ./grub.nix
  ];
}
