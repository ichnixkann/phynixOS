{ config, pkgs, lib, ... }:

# Binary cache configuration.
#
# Cachix is intentionally NOT used — phynixOS is a FOSS distribution and
# publishes through a self-hosted Attic cache. The public hostname is
# resolved at deploy time; until the server is live the entry below is a
# placeholder. See `docs/infra/attic-deploy.md` for the deploy recipe.

{
  nix.settings = {
    substituters = [
      "https://cache.nixos.org"
      # Self-hosted Attic cache for phynix flake outputs.
      # TODO: replace placeholder host with the live deployment URL.
      "https://cache.phynix-os.example/phynix"
      "https://hyprland.cachix.org"
      "https://nix-community.cachix.org"
    ];
    trusted-public-keys = [
      "cache.nixos.org-1:6NCHdD59X431o0gWypbMrAURkbJ16ZPMQFGspcDShjY="
      # TODO: replace with the public key emitted by `atticd-atticadm`
      # when the cache is first provisioned.
      "phynix:PLACEHOLDER_ATTIC_PUBLIC_KEY="
      "hyprland.cachix.org-1:a7pgxzMz7+chwVL3/pzj6jIBMioiJM7ypFP8PwtkuGc="
      "nix-community.cachix.org-1:mB9FSh9qf2dCimDSUo8Zy7bkq5CX+/rkCWyvRCUsRDY="
    ];
    trusted-users = [ "root" "@wheel" ];
  };
}
