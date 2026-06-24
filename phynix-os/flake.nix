{
  description = "PHYNIX OS — NixOS-based distribution with AI Copilot";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    home-manager = {
      url = "github:nix-community/home-manager/master";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    hyprland.url = "github:hyprwm/hyprland/main";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, home-manager, hyprland, flake-utils, ... }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = (nixpkgs.legacyPackages.${system}).extend (self: super: import ./overlays/rust-tools.nix {
          pkgs = self;
          lib = nixpkgs.lib;
          inherit (super) fetchFromGitHub rustPlatform;
        });
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            pkgs.home-manager
            python3
            python3Packages.pip
            python3Packages.textual
            python3Packages.rich
            fish
          ];
        };

        packages.phynix-copilot = pkgs.python3Packages.buildPythonApplication {
          pname = "phynix-copilot";
          version = "0.2.0";
          format = "other";
          src = ./pkgs/phynix-copilot;

          propagatedBuildInputs = with pkgs.python3Packages; [
            requests
            pydantic
            textual
            rich
          ];

          postInstall = ''
            mkdir -p $out/bin
            cp $src/cli.py $out/bin/pcopilot
            chmod +x $out/bin/pcopilot

            mkdir -p $out/share/phynix-copilot
            cp $src/completions.py $out/share/phynix-copilot/
          '';

          meta = {
            description = "PHYNIX OS Copilot — Self-evolving AI Assistant for NixOS";
            license = pkgs.lib.licenses.mit;
          };
        };

        packages.default = self.packages.${system}.phynix-copilot;
      }
    ) // {
      nixosConfigurations = {
        workstation = nixpkgs.lib.nixosSystem {
          system = "x86_64-linux";
          specialArgs = { inherit home-manager; };
          modules = [
            ./hosts/workstation/configuration.nix
            ./modules/core/default.nix
            ./modules/desktop/hyprland/default.nix
            ./modules/copilot/default.nix
          ];
        };
        installer-iso = nixpkgs.lib.nixosSystem {
          system = "x86_64-linux";
          specialArgs = { inherit home-manager; };
          modules = [
            "${nixpkgs}/nixos/modules/installer/cd-dvd/installation-cd-minimal.nix"
            ./hosts/installer/configuration.nix
          ];
        };
      };
    };
}
