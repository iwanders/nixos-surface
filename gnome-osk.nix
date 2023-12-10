{ config, pkgs, ... }:
{
  imports = [ ];

  # /usr/share/gnome-shell/extensions/<extension directory>/schemas

  options = { };

  # This module is here mostly to be able to modify the extensions in 
  # gdm.

  # Ok, no way to run this programatically... :<
  # Manually do the thing to enable the keyboard, ugh.

  # https://github.com/NixOS/nixpkgs/blob/9a8c7261525fce16e990736b9a514d2aeb4ee95e/nixos/modules/programs/dconf.nix#L65-L89

  # https://github.com/NixOS/nixpkgs/blob/1a6f704d3a05efba4f1f55f69f4bab5c188f8cc4/nixos/modules/services/x11/desktop-managers/gnome.md?plain=1#L115-L117 
  # ehh :< 
  config = {
    environment.systemPackages = [pkgs.gnome-osk];
  };
}
