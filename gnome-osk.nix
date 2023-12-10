{ config, pkgs, ... }:
{
  imports = [ ];

  # /usr/share/gnome-shell/extensions/<extension directory>/schemas

  # This module is here mostly to be able to modify the extensions in 
  # gdm.

  # Ok, no way to run this programatically... :<
  # Manually do the thing to enable the keyboard, ugh.

  # From
  # https://github.com/NixOS/nixpkgs/pull/63790
  # DCONF_PROFILE=/etc/dconf/profile/gdm /run/current-system/sw/bin/dbus-run-session dconf write /org.gnome.shell/enabled-extensions '[ "enhancedosk@cass00.github.io" ]'
  # This did set it for gdm from the looks of it;
  # DCONF_PROFILE=/etc/dconf/profile/gdm dconf dump /
  # does make it show up.


  # https://github.com/NixOS/nixpkgs/blob/9a8c7261525fce16e990736b9a514d2aeb4ee95e/nixos/modules/programs/dconf.nix#L65-L89

  # https://github.com/NixOS/nixpkgs/blob/1a6f704d3a05efba4f1f55f69f4bab5c188f8cc4/nixos/modules/services/x11/desktop-managers/gnome.md?plain=1#L115-L117 
  # ehh :< 
  config = {
    environment.systemPackages = [pkgs.gnome-osk];

    # I think this should work... but it still doesn't load this keyboard.
    # Even doing sudo -u gdm /run/current-system/sw/bin/dbus-run-session /run/current-system/sw/bin/gsettings get org.gnome.shell enabled-extensions '["enhancedosk@cass00.github.io"]'
    # followed by systemctl restart display-manager.service  does not work.

    # https://github.com/NixOS/nixpkgs/issues/54150 

    # This does set the property, also for gdm at boot, but even with the symlink in /usr/share/ it does not yet load the extension.
    services.xserver.desktopManager.gnome = {
      extraGSettingsOverrides = ''
          [org.gnome.shell]
          enabled-extensions=[ 'enhancedosk@cass00.github.io']
      '';
    };
  };
}
