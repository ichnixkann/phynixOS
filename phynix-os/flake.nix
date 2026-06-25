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

  outputs = { self, nixpkgs, home-manager, hyprland, flake-utils, ... }@inputs:
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

            # cli.py does `from agent import …`, so the sibling .py
            # modules must be installed alongside it AND that directory
            # must be on PYTHONPATH at runtime. buildPythonApplication's
            # wrapPythonPrograms phase honours makeWrapperArgs.
            postInstall = ''
              mkdir -p $out/share/phynix-copilot
              cp $src/*.py $out/share/phynix-copilot/

              mkdir -p $out/bin
              cp $src/cli.py $out/bin/pcopilot
              chmod +x $out/bin/pcopilot
            '';

            makeWrapperArgs = [
              "--prefix" "PYTHONPATH" ":" "$out/share/phynix-copilot"
            ];

            meta = {
              description = "PHYNIX OS Copilot — Self-evolving AI Assistant for NixOS";
              license = pkgs.lib.licenses.lgpl3Plus;
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
          boot-workstation    = import ./tests/boot-workstation.nix    { inherit pkgs self phynixPackages; };
          copilot-service     = import ./tests/copilot-service.nix     { inherit pkgs self phynixPackages; };
          installer-iso-build = import ./tests/installer-iso-boot.nix  { inherit pkgs self phynixPackages; };

          python-unit =
            let
              pythonEnv = pkgs.python3.withPackages (ps: with ps; [
                pytest
                pydantic
                requests
                rich
              ]);
            in
            pkgs.runCommand "phynix-copilot-pytest"
              { nativeBuildInputs = [ pythonEnv ]; }
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
