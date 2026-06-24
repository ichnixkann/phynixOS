{ config, pkgs, lib, ... }:
{
  home.stateVersion = "24.05";

  # User packages
  home.packages = with pkgs; [
    # Rust CLI tools
    claurst
    crush

    # Common utilities
    bat
    exa
    fd
    ripgrep
    fzf
  ];

  # Bash configuration
  programs.bash.enable = true;
  programs.bash.bashrcExtra = ''
    # PHYNIX-specific aliases
    alias pcopilot-claurst="claurst"
    alias crush-ui="crush"
  '';

  # Fish configuration
  programs.fish.enable = true;
  programs.fish.functions = {
    claurst-claude = "claurst --help";
    crush-menu = "crush";
  };

  # Git configuration
  programs.git = {
    enable = true;
    userName = "PHYNIX User";
    userEmail = "phynix@localhost";
  };
}
