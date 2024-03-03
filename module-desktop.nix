{ config, pkgs, ... }: {
  imports = [ ./gnome-osk.nix ];

  options = { };

  config = {
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
    ]) ++ (with pkgs; [ orca ]);

    # We also lose nautilus now though, so we add back stuff we actually care about...
    environment.systemPackages = (with pkgs.gnome; [
      eog # image viewer
      gnome-terminal
      gnome-system-monitor
      gnome-disk-utility
      nautilus
    ]) ++ (with pkgs; [ vlc mplayer scite chromium gimp xorg.xwininfo ]);
  };
}
