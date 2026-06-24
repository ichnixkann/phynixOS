{ config, pkgs, lib, ... }:
{
  environment.systemPackages = with pkgs; [
    # Rust toolchain
    rustup
    cargo
    rustc

    # Code assistant tools
    # claurst — Claude Rust CLI (from overlays)
    # crush — charmbracelet TUI (from overlays)
    # omo-ultimate — OpenCode assistant (from overlays)
  ];

  # User shell functions for development tools
  environment.shellAliases = {
    claurst-help = "claurst --help";
    crush-help = "crush --help";
    omo-help = "omo-ultimate --help";
    omo-init = "omo-ultimate init";
    omo-code = "omo-ultimate code";
  };
}
