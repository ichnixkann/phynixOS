{ config, pkgs, lib, ... }:
{
  imports = [
    ./rust.nix
  ];

  # Development environment configuration
  environment.systemPackages = with pkgs; [
    # Git and version control
    git
    git-crypt

    # Build tools
    gnumake
    cmake
    pkg-config

    # Text editors (available for dev work)
    vim
    nano

    # Development shells and interpreters
    python3
    python3Packages.pip
    nodejs
  ];

  # Enable development shells
  nix.settings.experimental-features = ["nix-command" "flakes"];

  # User development aliases
  environment.shellAliases = {
    dev = "nix develop";
    build = "nix build";
    rebuild = "sudo nixos-rebuild switch --flake";
  };
}
