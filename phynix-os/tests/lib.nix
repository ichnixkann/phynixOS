{ pkgs, self }:

# Thin wrapper around pkgs.testers.runNixOSTest with phynix-friendly
# defaults. Each test file imports this and passes a name + nodes +
# testScript.
let
  inherit (pkgs) lib;
in
{ name
, nodes
, testScript
, extraTestDriverArgs ? {}
, meta ? {}
}:

pkgs.testers.runNixOSTest ({
  inherit name testScript;

  # `hostPkgs` is bound automatically by pkgs.testers.runNixOSTest from
  # the surrounding pkgs argument; setting it again here triggers a
  # "defined multiple times" module-system error.

  # Every test gets a phynix user, journald limits raised so the test
  # script can grep journals reliably, and enough RAM for systemd-user
  # plus the Python interpreter the copilot agent spawns.
  defaults = { ... }: {
    # Modules in this repo (e.g. modules/copilot/default.nix) accept
    # `phynixPackages` as a module-system arg. The test framework
    # doesn't pass it, so default it to null here — the modules already
    # have a fallback for null.
    _module.args.phynixPackages = null;

    users.users.phynix = {
      isNormalUser = true;
      password = "phynix";
      uid = 1000;
      extraGroups = [ "wheel" ];
    };
    services.journald.extraConfig = "RuntimeMaxUse=64M";
    virtualisation = {
      memorySize = 1024;
      diskSize = 4096;
      cores = 2;
    };
  };

  inherit nodes;

  meta = {
    timeout = 1800;
    maintainers = [ ];
  } // meta;
} // extraTestDriverArgs)
