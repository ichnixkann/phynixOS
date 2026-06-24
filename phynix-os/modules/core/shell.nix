{ config, pkgs, lib, ... }:
{
  programs.fish = {
    enable = true;
    vendor.completions.enable = true;
    vendor.config.enable = true;
    vendor.functions.enable = true;

    shellInit = ''
      set -x EDITOR vim
      set -x PAGER less
    '';

    interactiveShellInit = ''
      alias ll "ls -lah"
      alias vi "vim"
      alias nix-build "nix build"
      alias nix-check "nix flake check"

      function mkcd
        mkdir -p $argv
        cd $argv[1]
      end

      function fish_greeting
      end
    '';
  };

  users.users.phynix.shell = pkgs.fish;

  environment.systemPackages = with pkgs; [
    fish
    fishPlugins.pure
    fishPlugins.fzf
  ];
}
