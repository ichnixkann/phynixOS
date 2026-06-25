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

    hercules-ci-effects = {
      url = "github:hercules-ci/hercules-ci-effects";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, home-manager, hyprland, flake-utils, hercules-ci-effects, ... }@inputs:
    let
      mkPkgs = system:
        (nixpkgs.legacyPackages.${system}).extend (final: prev:
          import ./overlays/rust-tools.nix {
            pkgs = final;
            lib = nixpkgs.lib;
            inherit (prev) fetchFromGitHub rustPlatform;
          });

      mkPhynixPackages = system:
        let pkgs = mkPkgs system; in {
          phynix-copilot = pkgs.python3Packages.buildPythonApplication {
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
        };
    in
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = mkPkgs system;
        phynixPackages = mkPhynixPackages system;
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            home-manager.packages.${system}.default
            python3
            python3Packages.pip
            python3Packages.pytest
            python3Packages.textual
            python3Packages.rich
            fish
            nix-fast-build
          ];

          shellHook = ''
            echo "phynix dev shell ready. useful targets:"
            echo "  nix flake check -L                     # everything (incl. VM tests)"
            echo "  nix build .#checks.${system}.boot-workstation -L"
            echo "  nix build .#checks.${system}.copilot-service -L"
            echo "  nix build .#checks.${system}.python-unit -L"
          '';
        };

        packages = phynixPackages // {
          default = phynixPackages.phynix-copilot;
        };

        checks = {
          boot-workstation   = import ./tests/boot-workstation.nix   { inherit pkgs self; };
          copilot-service    = import ./tests/copilot-service.nix    { inherit pkgs self; };
          installer-iso-boot = import ./tests/installer-iso-boot.nix { inherit pkgs self; };

          python-unit = pkgs.runCommand "phynix-copilot-pytest"
            {
              nativeBuildInputs = with pkgs.python3Packages; [
                python3
                pytest
                pydantic
                requests
                rich
              ];
            }
            ''
              cp -r ${./pkgs/phynix-copilot} src
              chmod -R +w src
              cd src
              python -m pytest tests/ -v
              touch $out
            '';
        };
      }
    ) // {
      # NixOS configurations consume the flake package via specialArgs so the
      # module and tests exercise the same artifact users install.
      nixosConfigurations = {
        workstation = nixpkgs.lib.nixosSystem {
          system = "x86_64-linux";
          specialArgs = {
            inherit home-manager;
            phynixPackages = mkPhynixPackages "x86_64-linux";
          };
          modules = [
            ./hosts/workstation/configuration.nix
            ./modules/core/default.nix
            ./modules/desktop/hyprland/default.nix
            ./modules/copilot/default.nix
          ];
        };
        installer-iso = nixpkgs.lib.nixosSystem {
          system = "x86_64-linux";
          specialArgs = {
            inherit home-manager;
            phynixPackages = mkPhynixPackages "x86_64-linux";
          };
          modules = [
            "${nixpkgs}/nixos/modules/installer/cd-dvd/installation-cd-minimal.nix"
            ./hosts/installer/configuration.nix
          ];
        };
      };
    };
}
