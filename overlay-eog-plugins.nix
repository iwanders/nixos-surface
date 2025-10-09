# Add the eye of gnome plugins, for https://wiki.gnome.org/Apps(2f)EyeOfGnome(2f)Plugins.html
# Mostly for the slideshow shuffle; https://help.gnome.org/users/eog/stable/plugin-slideshow-shuffle.html.en
# EOG build; https://github.com/NixOS/nixpkgs/blob/nixos-23.11/pkgs/desktops/gnome/core/eog/default.nix
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

    postInstall = ''
      makeWrapper ${prev.gnome.eog}/bin/eog $out/bin/eog \
        --prefix XDG_DATA_DIRS : $out/lib \
        --prefix PYTHONPATH :  ${prev.python3.pkgs.makePythonPath [ prev.python3Packages.pygobject3 ]} 
    '';
  };

  # Very ugly injection of the plugins into eog... this results in two eogs existing, the first to
  # build the plugins, the second one to use them... but that's light and this is easy and still results
  # in desktop integration and the like.
  eog-with-plugins = prev.gnome.eog.overrideAttrs(old: {
    postInstall = old.postInstall + ''
        wrapProgram $out/bin/eog \
          --prefix XDG_DATA_DIRS : ${final.gnome-eog-plugins}/lib \
          --prefix PYTHONPATH :  ${prev.python3.pkgs.makePythonPath [ prev.python3Packages.pygobject3 ]} 
    '';
  });
}
