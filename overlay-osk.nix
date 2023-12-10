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
  extension-uuid = "enhancedosk@cass00.github.io";
  in 
    prev.stdenv.mkDerivation {

      buildInputs = [
        prev.pkgs.glib
        prev.pkgs.zip
      ];

      name = "gnome-osk";

      inherit src;

      # This is only here to ensure it builds.
      buildPhase = ''
        ./package-extension.sh
      '';

      # Copy the relevant files to the correct location.
      installPhase = ''
        mkdir -p $out/share/gnome-shell/extensions/${extension-uuid}/
        cp -rv $src/src/* $out/share/gnome-shell/extensions/${extension-uuid}/
      '';
    };
}
