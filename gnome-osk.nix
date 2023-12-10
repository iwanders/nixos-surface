{ config, pkgs, ... }:
{
  imports = [ ];


  # https://github.com/NixOS/nixpkgs/blob/9a8c7261525fce16e990736b9a514d2aeb4ee95e/nixos/modules/programs/dconf.nix#L65-L89

  # https://github.com/NixOS/nixpkgs/blob/1a6f704d3a05efba4f1f55f69f4bab5c188f8cc4/nixos/modules/services/x11/desktop-managers/gnome.md?plain=1#L115-L117 

  config = {
    # Add the new gnome on screen keyboard to the packages.
    environment.systemPackages = [pkgs.gnome-osk];

    # Ensure gdm has access to the module by adding it to the XDG_DATA_DIRS path.
    # This string addition is pretty terrible, but it's necessary to avoid incorrect concatenation.
    services.xserver.displayManager.job.environment.XDG_DATA_DIRS = ":${pkgs.gnome-osk}/share:";

    # This does set the property, also for gdm at boot.
    services.xserver.desktopManager.gnome = {
      extraGSettingsOverrides = ''
          [org.gnome.shell]
          enabled-extensions=[ 'enhancedosk@cass00.github.io']
      '';
    };
  };
}
