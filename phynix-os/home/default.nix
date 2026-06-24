{ config, pkgs, lib, ... }:
{
  home.stateVersion = "24.05";

  # User packages
  home.packages = with pkgs; [
    # Code assistant & CLI tools
    claurst
    crush
    omo-ultimate

    # Fish shell enhancements
    fishPlugins.pure
    fishPlugins.fzf

    # Common utilities
    bat
    exa
    fd
    ripgrep
    fzf
  ];

  # Enhanced Fish configuration with oh-my-fish support
  programs.fish = {
    enable = true;

    shellInit = ''
      # PHYNIX OS Fish Setup
      set -x EDITOR vim

      # Initialize oh-my-fish
      if test -d $HOME/.local/share/omf
        set OMF_PATH $HOME/.local/share/omf
      else
        echo "💡 Install oh-my-fish: curl https://get.oh-my.fish | fish"
      end

      echo "🐠 PHYNIX OS — Fish Shell"
    '';

    interactiveShellInit = ''
      # Shell aliases
      alias ll "exa -lah"
      alias vi "vim"
      alias nix-build "nix build"
      alias nix-check "nix flake check"
      alias dev "nix develop"

      # PHYNIX tools
      alias pcopilot-tui "pcopilot --tui"
      alias pcopilot-status "pcopilot --backend"
      alias claurst-help "claurst --help"
    '';

    functions = {
      mkcd = ''
        mkdir -p $argv
        cd $argv[1]
      '';

      # PHYNIX system functions
      phynix-dev = ''
        echo "🔨 Entering PHYNIX development environment..."
        nix develop
      '';

      phynix-rebuild = ''
        echo "🔄 Rebuilding PHYNIX configuration..."
        sudo nixos-rebuild switch --flake .
      '';

      phynix-status = ''
        echo "🐠 PHYNIX Status:"
        pcopilot --backend
        pcopilot --pending
      '';

      # Code assistant functions
      ask-omo = ''
        set query $argv
        if test -z "$query"
          omo-ultimate
        else
          omo-ultimate code "$query"
        end
      '';

      ask-claude = ''
        set query $argv[1]
        if test -z "$query"
          pcopilot --tui
        else
          pcopilot "$query"
        end
      '';

      code-review = ''
        echo "🔍 Starting Omo code review..."
        omo-ultimate code --review (pwd)
      '';

      fish_greeting = ''
        # Greeting handled by oh-my-fish/Tide
      '';
    };
  };

  # Bash configuration
  programs.bash.enable = true;
  programs.bash.bashrcExtra = ''
    # PHYNIX-specific aliases
    alias pcopilot-tui="pcopilot --tui"
    alias crush-menu="crush"
  '';

  # Git configuration
  programs.git = {
    enable = true;
    userName = "PHYNIX User";
    userEmail = "phynix@localhost";
  };
}
