{ config, pkgs, ... }:
{
  imports = [
    ./gnome-osk.nix
  ];

  options = { };

  config = {
    # https://github.com/NixOS/nixpkgs/blob/4ecab3273592f27479a583fb6d975d4aba3486fe/nixos/modules/services/x11/desktop-managers/gnome.nix#L459

    # Configure keymap in X11
    services.xserver.layout = "us";
    # services.xserver.xkbOptions = "eurosign:e,caps:escape";
    services.xserver.enable = true;
    services.xserver.displayManager.gdm.enable = true;
    services.xserver.displayManager.gdm.debug = true;
    services.xserver.desktopManager.gnome.enable = true;

    services.gnome.core-utilities.enable = false;


    # well, that still pulls in orca, with speech synthesis, for many megabytes.
    # https://github.com/NixOS/nixpkgs/blob/4ecab3273592f27479a583fb6d975d4aba3486fe/nixos/modules/services/x11/desktop-managers/gnome.nix#L459
    # https://discourse.nixos.org/t/howto-disable-most-gnome-default-applications-and-what-they-are/13505
    environment.gnome.excludePackages = (with pkgs.gnome; [
      baobab # disk usage analyzer
      eog # image viewer
      epiphany # web browser
      gedit # text editor
      simple-scan # document scanner
      totem # video player
      yelp # help viewer
      evince # document viewer
      file-roller # archive manager
      geary # email client
      seahorse # password manager
      gnome-calculator
      gnome-calendar
      gnome-characters
      gnome-clocks
      gnome-contacts
      gnome-font-viewer
      gnome-logs
      gnome-maps
      gnome-music
      gnome-screenshot
      gnome-weather
      pkgs.gnome-connections
    ]) ++ (with pkgs;[
      orca
    ]);


    # We also lose nautilus now though...
    environment.systemPackages =
      (with pkgs.gnome; [
        nautilus
        gnome-terminal
        gnome-system-monitor
        gnome-disk-utility
      ]) ++ (with pkgs;[
        vlc
        mplayer
        scite
        chromium
        gimp
        xorg.xwininfo
      ]);
  };
}
