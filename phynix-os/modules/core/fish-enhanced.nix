{ config, pkgs, lib, ... }:
{
  programs.fish = {
    enable = true;
    vendor.completions.enable = true;
    vendor.config.enable = true;
    vendor.functions.enable = true;

    shellInit = ''
      # PHYNIX OS Fish Configuration
      set -x EDITOR vim
      set -x PAGER less

      # Initialize oh-my-fish
      if test -d $HOME/.local/share/omf
        set -x OMF_PATH $HOME/.local/share/omf
      end

      # Welcome banner
      echo "🐠 PHYNIX OS — Fish Shell with oh-my-fish & Tide"
    '';

    interactiveShellInit = ''
      # Aliases
      alias ll "ls -lah"
      alias vi "vim"
      alias nix-build "nix build"
      alias nix-check "nix flake check"

      # PHYNIX-specific aliases
      alias pcopilot-claurst "claurst"
      alias crush-menu "crush"

      # Tide prompt configuration
      set -g tide_left_prompt_items pwd git
      set -g tide_right_prompt_items status cmd_duration
      set -g tide_pwd_dir_max_depth 3
      set -g tide_git_bg_color normal
    '';

    functions = {
      mkcd = ''
        mkdir -p $argv
        cd $argv[1]
      '';

      fish_greeting = ''
        # Suppress default greeting
      '';

      # PHYNIX-specific helpers
      pcopilot_query = ''
        set query $argv[1]
        if test -z "$query"
          pcopilot --tui
        else
          pcopilot "$query"
        end
      '';

      dev_shell = ''
        echo "🔨 Entering development shell..."
        nix develop
      '';

      phynix_status = ''
        echo "🐠 PHYNIX Status:"
        pcopilot --backend
        pcopilot --pending
      '';

      fish_prompt = ''
        # Use Tide prompt (if available)
        if type -q tide
          tide
        else
          # Fallback to simple prompt
          echo -n (set_color cyan)(prompt_pwd)(set_color normal)' '
        end
      '';
    };

    plugins = [
      {
        name = "tide";
        src = pkgs.fetchFromGitHub {
          owner = "IlanCosman";
          repo = "tide";
          rev = "v6.1.0";
          sha256 = "sha256-KSrVF9SrGnuaYHtE2Vgw/6L+2jL1cVzDL8nU2ynPKYc=";  # Update as needed
        };
      }
      # oh-my-fish will be installed via package
    ];
  };

  environment.systemPackages = with pkgs; [
    fish
    # Fish theme/plugin packages
    fishPlugins.pure
    fishPlugins.fzf
    # For oh-my-fish support
    git
  ];

  users.users.phynix.shell = pkgs.fish;

  # Post-install setup script
  system.activationScripts.phynix-fish-setup = lib.mkBefore ''
    echo "Setting up oh-my-fish..."

    # Install oh-my-fish if not present
    if [ ! -d "$HOME/.local/share/omf" ]; then
      mkdir -p "$HOME/.local/share"
      echo "oh-my-fish directory created"
    fi

    # Note: oh-my-fish itself and oh-my-openagent will be installed
    # via user shell commands or Home Manager after system setup
  '';
}
