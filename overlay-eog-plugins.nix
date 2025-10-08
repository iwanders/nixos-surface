  # BUild as in https://github.com/NixOS/nixpkgs/blob/nixos-23.11/pkgs/desktops/gnome/core/eog/default.nix
final: prev: {
  # git clone https://gitlab.gnome.org/GNOME/eog-plugins.git
  gnome-eog-plugins = prev.stdenv.mkDerivation rec {
    pname = "eog-plugins";
    version = "44.1";

    outputs = [ "out" "dev" ];

    src = prev.fetchFromGitHub {
      owner = "GNOME";
      repo = "eog-plugins";
      rev = "b1b0f9cf18bb09e1bea9aa4cfe39251ed3a9b848"; # 44.1
      hash = "sha256-V+e0Bo7HwauJAkRqVMV1fJsI0F+qTnTrUpnURh4HQho=";
    };


    nativeBuildInputs = with prev; [
      gnome.eog
      python3
      glib
      gtk3 
      meson
      ninja
      pkg-config
      gnome.libchamplain
      libgdata
      libpeas
      libhandy
      libexif
      makeWrapper
    ];

    buildInputs = with prev; [python3 glib libpeas gtk3];

    mesonFlags = [];

    #postInstall = ''
    #  # Pull in WebP support for gnome-backgrounds.
    #  # In postInstall to run before gappsWrapperArgsHook.
    #  export GDK_PIXBUF_MODULE_FILE="${prev.gnome._gdkPixbufCacheBuilder_DO_NOT_USE {
    #    extraLoaders = with prev; [
    #      librsvg
    #      webp-pixbuf-loader
    #      libheif.out
    #    ];
    #  }}"
    #'';

    # https://github.com/NixOS/nixpkgs/blob/1ec96f776b2c5a5789005ecc6afedcb4b30e8fef/pkgs/build-support/setup-hooks/make-wrapper.sh#L13


    postInstall = ''

      #mkdir -p $out/bin/
      #cp ${prev.gnome.eog}/bin/eog $out/bin/
      makeWrapper ${prev.gnome.eog}/bin/eog $out/bin/eog \
        --prefix XDG_DATA_DIRS : $out/lib \
        --prefix PYTHONPATH :  ${prev.python3.pkgs.makePythonPath [ prev.python3Packages.pygobject3 ]} 
  '';
    preFixup = ''
    '';



    #passthru = {
    #  updateScript = prev.gnome.updateScript {
    #    packageName = pname;
    #    attrPath = "gnome.${pname}";
    #  };
    #};

    meta = with prev.lib; {
      description = "GNOME image viewer";
      homepage = "https://wiki.gnome.org/Apps/EyeOfGnome";
      license = licenses.gpl2Plus;
      maintainers = teams.gnome.members;
      platforms = platforms.unix;
      mainProgram = "eog";
    };
  };

  eog-with-plugins = prev.gnome.eog.overrideAttrs(old: {
    postInstall = ''
        wrapProgram $out/bin/eog \
          --prefix XDG_DATA_DIRS : ${final.gnome-eog-plugins}/lib \
          --prefix PYTHONPATH :  ${prev.python3.pkgs.makePythonPath [ prev.python3Packages.pygobject3 ]} 
    '';
  });
}
