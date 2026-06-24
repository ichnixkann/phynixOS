{
  description = "PHYNIX OS — NixOS-based distribution with AI Copilot";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    home-manager = {
      url = "github:nix-community/home-manager/master";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    hyprland.url = "github:hyprwm/hyprland/master";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, home-manager, hyprland, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            nixos-generators
            home-manager
          ];
        };
      }
    ) // {
      nixosConfigurations = {
        workstation = nixpkgs.lib.nixosSystem {
          system = "x86_64-linux";
          specialArgs = { inherit home-manager hyprland; };
          modules = [
            ./hosts/workstation/configuration.nix
            ./modules/core/default.nix
            ./modules/desktop/hyprland/default.nix
            ./modules/copilot/default.nix
          ];
        };
        installer-iso = nixpkgs.lib.nixosSystem {
          system = "x86_64-linux";
          specialArgs = { inherit home-manager hyprland; };
          modules = [
            "${nixpkgs}/nixos/modules/installer/cd-dvd/installation-cd-minimal.nix"
            ./hosts/installer/configuration.nix
          ];
        };
      };
    };
}
