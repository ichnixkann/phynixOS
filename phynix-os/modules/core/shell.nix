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

      # Add phynix completions
      if test -d ${placeholder "out"}/share/fish/vendor_completions.d
        set fish_complete_path ${placeholder "out"}/share/fish/vendor_completions.d $fish_complete_path
      end

      # Welcome banner
      echo "🐠 PHYNIX OS — Fish Shell"
    '';

    interactiveShellInit = ''
      # Aliases
      alias ll "ls -lah"
      alias vi "vim"
      alias nix-build "nix build"
      alias nix-check "nix flake check"
    '';

    functions = {
      mkcd = ''
        mkdir -p $argv
        cd $argv[1]
      '';

      fish_greeting = ''
        # Suppress default greeting
      '';
    };
  };

  users.users.phynix.shell = pkgs.fish;

  environment.systemPackages = with pkgs; [
    fish
    fishPlugins.pure
    fishPlugins.fzf
  ];
}
