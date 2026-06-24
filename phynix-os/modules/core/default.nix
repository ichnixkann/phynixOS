{ config, pkgs, lib, ... }:
{
  imports = [
    ./boot.nix
    ./networking.nix
    ./audio.nix
    ./shell.nix
  ];

  system.stateVersion = "24.05";
  nixpkgs.config.allowUnfree = true;

  environment.systemPackages = with pkgs; [
    git
    vim
    curl
    wget
    htop
  ];
}
