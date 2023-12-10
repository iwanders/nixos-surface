{ config, pkgs, ... }:
{
  imports = [ ];

  # /usr/share/gnome-shell/extensions/<extension directory>/schemas

  options = { };

  config = {
    environment.systemPackages = [pkgs.gnome-osk];
  };
}
