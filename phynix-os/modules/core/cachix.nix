{ config, pkgs, lib, ... }:
{
  nix.settings = {
    substituters = [
      "https://cache.nixos.org"
      "https://phynix.cachix.org"
      "https://hyprland.cachix.org"
      "https://nix-community.cachix.org"
    ];
    trusted-public-keys = [
      "cache.nixos.org-1:6NCHdD59X431o0gWypbMrAURkbJ16ZPMQFGspcDShjY="
      "phynix.cachix.org-1:PLACEHOLDER_KEY="   # Replace after cachix push-key
      "hyprland.cachix.org-1:a7pgxzMz7+chwVL3/pzj6jIBMioiJM7ypFP8PwtkuGc="
      "nix-community.cachix.org-1:mB9FSh9qf2dCimDSUo8Zy7bkq5CX+/rkCWyvRCUsRDY="
    ];
    trusted-users = [ "root" "@wheel" ];
  };
}
