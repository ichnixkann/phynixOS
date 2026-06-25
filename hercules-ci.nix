{ inputs, ... }:

# Hercules CI configuration. See https://docs.hercules-ci.com/
#
# Hercules picks up every flake `checks.*` and `packages.*` output
# automatically and posts a status check per output on each PR. This
# file only needs to declare CI systems and any *effects* (post-build
# actions) — for us, pushing successful store paths to our self-hosted
# Attic cache.

{
  herculesCI = { ... }: {
    ciSystems = [ "x86_64-linux" ];
  };

  # Push successful main-branch builds to the Attic cache.
  #
  # Requires a Hercules secret named `attic` with the shape
  # { "token": "<atticd write token>" } — register it in the Hercules
  # dashboard under Secrets.
  #
  # The cache URL placeholder must match `phynix-os/modules/core/cachix.nix`
  # once the cache is deployed (see docs/infra/attic-deploy.md).
  herculesCI.onPush.default.outputs.effects.push-to-attic =
    { pkgs, hci-effects, ... }:
    hci-effects.runIf (hci-effects.gitRef == "refs/heads/main") (
      hci-effects.mkEffect {
        name = "push-to-attic";
        secretsMap.attic = "attic";
        buildInputs = [ pkgs.attic-client pkgs.jq ];
        effectScript = ''
          token=$(jq -r '.token' < "$SECRETS_FILE")
          attic login phynix https://cache.phynix-os.example "$token"
          # Push every flake output Hercules just built.
          for path in $(cat "$HERCULES_CI_OUTPUTS_FILE"); do
            attic push phynix "$path" || true
          done
        '';
      }
    );
}
