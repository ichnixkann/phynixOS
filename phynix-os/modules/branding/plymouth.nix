{ config, pkgs, lib, ... }:
let
  # Build the PHYNIX Plymouth theme from SVG assets
  phynix-plymouth-theme = pkgs.stdenv.mkDerivation {
    name = "plymouth-theme-phynix";
    src = ../../assets/branding;

    installPhase = ''
      DEST=$out/share/plymouth/themes/phynix
      mkdir -p $DEST

      cp phynix.plymouth $DEST/
      cp phynix.script  $DEST/
      cp -r images/     $DEST/ 2>/dev/null || mkdir -p $DEST/images
    '';
  };
in
{
  boot.plymouth = {
    enable = true;
    theme = "phynix";
    themePackages = [ phynix-plymouth-theme ];
  };

  # Quiet boot for clean Plymouth experience
  boot.kernelParams = [ "quiet" "splash" "rd.udev.log_level=3" ];
  boot.initrd.verbose = false;
}
