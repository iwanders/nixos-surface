{ config, pkgs, ... }:
{
  imports = [ ];

  # /usr/share/gnome-shell/extensions/<extension directory>/schemas

  options = { };

  # https://github.com/NixOS/nixpkgs/blob/1a6f704d3a05efba4f1f55f69f4bab5c188f8cc4/nixos/modules/services/x11/desktop-managers/gnome.md?plain=1#L115-L117 
  # ehh :< 
  config = {
    environment.systemPackages = [pkgs.gnome-osk];
  };
}
