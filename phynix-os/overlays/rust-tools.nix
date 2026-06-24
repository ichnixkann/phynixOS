{ pkgs, lib, fetchFromGitHub, rustPlatform, python3Packages, ... }:
{
  # Omo Ultimate — OpenCode assistant
  omo-ultimate = pkgs.python3Packages.buildPythonApplication rec {
    pname = "omo-ultimate";
    version = "1.0.0";

    src = fetchFromGitHub {
      owner = "omolabs";  # Adjust owner if different
      repo = "omo";
      rev = "main";
      sha256 = lib.fakeSha256;
    };

    propagatedBuildInputs = with pkgs.python3Packages; [
      requests
      click
      pyyaml
      pydantic
    ];

    meta = {
      description = "Omo Ultimate — Advanced code assistant for OpenCode";
      license = lib.licenses.mit;
      maintainers = [ ];
    };
  };

  # claurst — Claude Rust CLI Tool
  claurst = rustPlatform.buildRustPackage rec {
    pname = "claurst";
    version = "0.1.0";

    src = fetchFromGitHub {
      owner = "Kuberwastaken";
      repo = "claurst";
      rev = "main";
      sha256 = lib.fakeSha256;  # Update with actual hash after first build
    };

    cargoSha256 = lib.fakeSha256;  # Update with actual hash after first build

    meta = {
      description = "Claude Rust CLI Tool for Claude Code";
      license = lib.licenses.mit;
      maintainers = [ ];
    };
  };

  # crush — charmbracelet TUI tool
  crush = rustPlatform.buildRustPackage rec {
    pname = "crush";
    version = "0.1.0";

    src = fetchFromGitHub {
      owner = "charmbracelet";
      repo = "crush";
      rev = "main";
      sha256 = lib.fakeSha256;  # Update with actual hash
    };

    cargoSha256 = lib.fakeSha256;  # Update with actual hash

    buildInputs = with pkgs; [
      pkg-config
      openssl
    ];

    meta = {
      description = "A charmbracelet TUI tool for userspace";
      license = lib.licenses.mit;
      maintainers = [ ];
    };
  };
}
