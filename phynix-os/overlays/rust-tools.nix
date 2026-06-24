{ pkgs, lib, fetchFromGitHub, rustPlatform, ... }:
{
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
