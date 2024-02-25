final: prev: {

  # From https://github.com/NixOS/nixpkgs/blob/69f966b3410d0f1caf97fb6dea639cef6fa15df4/pkgs/applications/misc/iptsd/default.nix#L18
  iptsd = prev.iptsd.overrideAttrs (old: rec {

    src = prev.fetchFromGitHub {
      owner = "iwanders";
      repo = "linux-surface-iptsd";
      rev = "b66f68b28b3c98143a39a1c9e6cd69ff8b835858";
      hash = "sha256-v2fS2OCeBUqABdfEra0bNB2qJCKya+vixmetieawVvM=";
    };

    buildInputs = old.buildInputs ++ [ prev.cairomm prev.SDL2 ];
    mesonFlags = [
      "-Dservice_manager=systemd"
      "-Dsample_config=false"
      "-Ddebug_tools=calibrate,dump,perf,plot"
      "-Db_lto=false" # plugin needed to handle lto object -> undefined reference to ...
    ];
  });
}
