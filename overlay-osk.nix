final: prev: {

  # https://github.com/cass00/enhanced-osk-gnome-ext
  # # /usr/share/gnome-shell/extensions/<extension directory>/schemas
  # /usr/share/gnome-shell/extensions/uuid
  # Uid is 
  gnome-osk = let
    src = prev.fetchFromGitHub {
      owner = "cass00";
      repo = "enhanced-osk-gnome-ext";
      rev = "0d4ae37d9830b823c224570c69c9a5e2f16d9ef4";
      hash = "sha256-s2bmEoOhGfpa5hVdpLEc2aECNjn9885oaVk5SYR3JD8=";
    };
    uuid = "enhancedosk@cass00.github.io";
  in 
    prev.stdenv.mkDerivation {

      buildInputs = [
        prev.pkgs.glib
        prev.pkgs.zip
        prev.pkgs.unzip
      ];

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
      '';

      # Package the extension
      buildPhase = ''
        ./package-extension.sh
      '';

      # And then unpack it into the correct location
      installPhase = ''
        mkdir -p $out/share/gnome-shell/extensions/${uuid}/
        unzip ${uuid}.shell-extension.zip -d $out/share/gnome-shell/extensions/${uuid}/
      '';
      passthru = {
        inherit uuid;
      };
    };
}
