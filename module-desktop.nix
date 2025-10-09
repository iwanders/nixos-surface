{ config, pkgs, ... }: {

  # https://github.com/fthx/no-overview/tree/main
  # is also helpful to ensure we end up on a desktop instead of the launcher.
  # Forked to https://github.com/iwanders/gnome-no-overview-extension
  # Currently installed through the gnome extension system.

  imports = [
    ./gnome-osk.nix
  ];

  options = { };

  config = {

    # Surface related stuff.
    services.iptsd.enable = true;

    sound.enable = true;

    hardware.pulseaudio.enable = false;
    # https://discourse.nixos.org/t/bluetooth-a2dp-sink-not-showing-up-in-pulseaudio-on-nixos/32447/3
    services.pipewire = {
        enable = true;
        pulse.enable = true;
    };

    # https://github.com/NixOS/nixpkgs/blob/4ecab3273592f27479a583fb6d975d4aba3486fe/nixos/modules/services/x11/desktop-managers/gnome.nix#L459

    # Configure keymap in X11
    services.xserver.layout = "us";
    # services.xserver.xkbOptions = "eurosign:e,caps:escape";
    services.xserver.enable = true;
    services.xserver.displayManager.gdm.enable = true;
    services.xserver.displayManager.gdm.autoSuspend = false;

    # This block is here to ensure we get GDM with the custom on screen keyboard extension
    # in the settings I want.
    programs.dconf.profiles.gdm.databases = [
      {
        #lockAll = false;
        settings."org/gnome/shell/extensions/enhancedosk" = {
          show-statusbar-icon = true;
          locked = true;
        };
      }

      {
        #lockAll = false;
        settings."org/gnome/shell" = {
          enabled-extensions = [ "iwanders-gnome-enhanced-osk-extension" ];
        };
      }

      {
        #lockAll = false;
        settings."org/gnome/desktop/a11y/applications" = {
          screen-keyboard-enabled = true;
        };
      }
    ];

    services.xserver.desktopManager.gnome.enable = true;

    services.gnome.core-utilities.enable = false;

    services.usbmuxd.enable = true; # For mounting ios devices.

    # well, that (utilities false) still pulls in orca, with speech synthesis, for many megabytes.
    # https://github.com/NixOS/nixpkgs/blob/4ecab3273592f27479a583fb6d975d4aba3486fe/nixos/modules/services/x11/desktop-managers/gnome.nix#L459
    # https://discourse.nixos.org/t/howto-disable-most-gnome-default-applications-and-what-they-are/13505
    environment.gnome.excludePackages = (with pkgs.gnome; [
      baobab # disk usage analyzer
      epiphany # web browser
      gedit # text editor
      simple-scan # document scanner
      totem # video player
      yelp # help viewer
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
    ]) ++ (with pkgs; [ orca ]);

    # We also lose nautilus now though, so we add back stuff we actually care about...
    environment.systemPackages = (with pkgs.gnome; [
      #eog # image viewer
      evince # document viewer
      file-roller # archive manager
      gnome-terminal
      gnome-system-monitor
      gnome-disk-utility
      nautilus
      gvfs # for mounting ios devices.
    ]) ++ (with pkgs; [
      vlc
      mplayer
      scite
      chromium
      gimp
      xorg.xwininfo
      thunderbird
      firefox
      # For mounting ios devices:
      libimobiledevice
      ifuse # optional, to mount using 'ifuse'
      eog-with-plugins # Eye of gnome with plugins.

      # for thumbnailing heic files. https://github.com/NixOS/nixpkgs/issues/164021#issuecomment-2120161608
      libheif 
      libheif.out 
    ]);
  };
}
