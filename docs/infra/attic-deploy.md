# Attic binary cache — deploy recipe

phynixOS publishes its Nix store paths through a self-hosted
[Attic](https://github.com/zhaofengli/attic) cache. This document
captures the minimal NixOS configuration so the cache is reproducible
if the server is rebuilt.

## Prerequisites

- A small NixOS VPS (1 vCPU, 2 GB RAM, 50+ GB disk is enough to start)
- DNS pointing `cache.phynix-os.example` → the VPS (replace with the
  actual hostname)
- Ports 80 + 443 open

## NixOS module

Drop this into the server's `configuration.nix`:

```nix
{ config, pkgs, lib, ... }:
{
  services.atticd = {
    enable = true;
    credentialsFile = "/var/lib/atticd/credentials.env";

    settings = {
      listen = "127.0.0.1:8080";
      api-endpoint = "https://cache.phynix-os.example/";

      chunking = {
        nar-size-threshold = 65536;
        min-size = 16384;
        avg-size = 65536;
        max-size = 262144;
      };

      compression = { type = "zstd"; level = 8; };

      storage = {
        type = "local";
        path = "/var/lib/atticd/storage";
      };

      database.url = "sqlite:///var/lib/atticd/server.db";
    };
  };

  services.nginx = {
    enable = true;
    recommendedProxySettings = true;
    recommendedTlsSettings = true;
    virtualHosts."cache.phynix-os.example" = {
      enableACME = true;
      forceSSL = true;
      locations."/".proxyPass = "http://127.0.0.1:8080";
      # Attic streams large NARs; raise the body size cap.
      extraConfig = "client_max_body_size 8G;";
    };
  };

  security.acme = {
    acceptTerms = true;
    defaults.email = "ops@phynix-os.example";
  };

  networking.firewall.allowedTCPPorts = [ 80 443 ];
}
```

## One-time provisioning

After the first `nixos-rebuild switch`:

```bash
# Generate an HS256 secret for token signing.
openssl rand -base64 32 > /var/lib/atticd/secret
chown atticd:atticd /var/lib/atticd/secret
chmod 600 /var/lib/atticd/secret

cat > /var/lib/atticd/credentials.env <<EOF
ATTIC_SERVER_TOKEN_HS256_SECRET_BASE64=$(cat /var/lib/atticd/secret)
EOF

systemctl restart atticd

# Create the public cache.
atticadm --config /etc/atticd/server.toml \
  cache create phynix --public

# Mint a write token for CI (Hercules + the release ISO job).
atticadm --config /etc/atticd/server.toml \
  make-token --sub ci --validity 1y --pull phynix --push phynix
# → record the token, paste into Hercules secret `attic` and GitHub
#   secret `ATTIC_TOKEN`.

# Print the public verification key for client-side trust.
atticadm --config /etc/atticd/server.toml \
  cache info phynix
# → copy `Public Key` and paste into:
#     phynix-os/modules/core/cachix.nix (trusted-public-keys)
#     README.md, phynix-os/README.md
```

## Verifying the cache works

From any machine with Nix:

```bash
nix-store --query --requisites $(which bash) | head -n 1 \
  | xargs nix copy --to "https://cache.phynix-os.example/phynix"

# Then on a clean machine, with only Attic as a substituter:
nix build nixpkgs#hello \
  --option substituters "https://cache.phynix-os.example/phynix" \
  --option trusted-public-keys "phynix:<the public key>"
```

## Routine maintenance

- `atticd-atticadm garbage-collect` once a month to expire old NARs.
- `journalctl -u atticd -f` for live logs.
- The store path lives under `/var/lib/atticd/storage`; back this up
  if you don't want a cold rebuild after disk loss.
