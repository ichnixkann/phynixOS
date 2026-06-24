{ config, pkgs, ... }:
{
  services.pipewire = {
    enable = true;
    pulse.enable = true;
    alsa.enable = true;
    jack.enable = false;
  };

  hardware.pulseaudio.enable = false;
}
