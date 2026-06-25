{ config, pkgs, lib, ... }:
{
  imports = [
    ./boot.nix
    ./networking.nix
    ./audio.nix
    ./shell.nix
    ./cachix.nix
  ];

  system.stateVersion = "24.05";

  # `nixpkgs.config.allowUnfree` belongs in the host config — setting
  # it here conflicts with the read-only nixpkgs that the NixOS test
  # framework injects when this module is consumed by a VM test.

  environment.systemPackages = with pkgs; [
    git
    vim
    curl
    wget
    htop
  ];
}
