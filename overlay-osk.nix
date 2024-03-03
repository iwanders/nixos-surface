final: prev: {

  # https://github.com/cass00/enhanced-osk-gnome-ext
  # # /usr/share/gnome-shell/extensions/<extension directory>/schemas
  # /usr/share/gnome-shell/extensions/uuid
  # Uid is 
  gnome-osk = let
    src = prev.fetchFromGitHub {
      owner = "iwanders";
      repo = "gnome-enhanced-osk-extension";
      rev = "cf2317035b31a4c7d746c0b2ef58a4c6ba2e85d8";
      hash = "sha256-suFJkw+5o0Xxx+M9X+gLg/BvYB9UkVUi5KOtReq/AMM=";
    };
    uuid = "iwanders-gnome-enhanced-osk-extension";
  in prev.stdenv.mkDerivation {

    buildInputs = [ prev.pkgs.glib prev.pkgs.zip prev.pkgs.unzip ];

    name = "gnome-osk";

    inherit src;

    # Fix the path to
    # /share/gnome-shell/gnome-shell-osk-layouts.gresource
    # To point at /run/current-system/sw/share/gnome-shell/gnome-shell-osk-layouts.gresource
    patchPhase = ''
      # Fix the resource path, /../ to walk up from the 'usr' prefix.
      sed -i src/extension.js -e 's|"/share/gnome-shell/gnome-shell-osk-layouts.gresource"|"/../run/current-system/sw/share/gnome-shell/gnome-shell-osk-layouts.gresource"|g'
      # Allow using this in gdm.
      sed -i src/metadata.json -e 's|}|,"session-modes": ["user", "gdm", "unlock-dialog"]}|g'

      # Super ugly way to change the default sizes to work well with this screen.
      sed -i src/schemas/org.gnome.shell.extensions.enhancedosk.gschema.xml -e 's|33|39|g'
      sed -i src/schemas/org.gnome.shell.extensions.enhancedosk.gschema.xml -e 's|16|21|g'
    '';

    # Package the extension
    buildPhase = ''
      ./package-extension.sh
    '';

    # And then unpack it into the correct location
    installPhase = ''
      mkdir -p $out/share/gnome-shell/extensions/${uuid}/
      unzip ${uuid}.zip -d $out/share/gnome-shell/extensions/${uuid}/
    '';
    passthru = { inherit uuid; };
  };
}
