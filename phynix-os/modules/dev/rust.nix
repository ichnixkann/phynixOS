{ config, pkgs, lib, ... }:
{
  environment.systemPackages = with pkgs; [
    # Rust toolchain
    rustup
    cargo
    rustc

    # PHYNIX-specific Rust tools
    # claurst — Claude Rust CLI (from overlays)
    # crush — charmbracelet TUI (from overlays)
  ];

  # User shell functions for Rust tools
  environment.shellAliases = {
    claurst-help = "claurst --help";
    crush-help = "crush --help";
  };
}
