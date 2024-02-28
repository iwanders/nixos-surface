final: prev: {

  # From https://github.com/NixOS/nixpkgs/blob/69f966b3410d0f1caf97fb6dea639cef6fa15df4/pkgs/applications/misc/iptsd/default.nix#L18
  iptsd = prev.iptsd.overrideAttrs (old: rec {

    src = prev.fetchFromGitHub {
      owner = "iwanders";
      repo = "linux-surface-iptsd";
      rev = "5f399fee731786d990e3e2982455efa4bf299621";
      hash = "sha256-LwQRGdiSwOr4t7klOXYsBRs7E0YOIELeRPPRFjWtWtM=";
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
