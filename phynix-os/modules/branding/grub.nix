{ config, pkgs, lib, ... }:
let
  phynix-grub-theme = pkgs.stdenv.mkDerivation {
    name = "grub-theme-phynix";
    src = ../../assets/branding;

    installPhase = ''
      DEST=$out/grub/themes/phynix
      mkdir -p $DEST

      cp theme.txt $DEST/ 2>/dev/null || cat > $DEST/theme.txt << 'EOF'
# PHYNIX OS GRUB Theme
title-text: "PHYNIX OS"
title-font: "DejaVu Sans Bold 24"
title-color: "#FF6B00"
desktop-color: "#0a0a0a"
message-font: "DejaVu Sans 12"
message-color: "#FFFFFF"
terminal-font: "DejaVu Sans Mono 14"
terminal-border: "0"

+ boot_menu {
  left = 30%
  top = 30%
  width = 40%
  height = 40%
  item_font = "DejaVu Sans 14"
  item_color = "#AAAAAA"
  selected_item_color = "#FF6B00"
  item_height = 28
  item_padding = 5
  item_spacing = 4
}
EOF
    '';
  };
in
{
  boot.loader.grub = {
    theme = "${phynix-grub-theme}/grub/themes/phynix";
    splashImage = null;
    backgroundColor = "#0a0a0a";
    font = "${pkgs.dejavu_fonts}/share/fonts/truetype/DejaVuSans.ttf";
  };
}
