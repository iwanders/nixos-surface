final: prev: {

  # From https://github.com/NixOS/nixpkgs/blob/69f966b3410d0f1caf97fb6dea639cef6fa15df4/pkgs/applications/misc/iptsd/default.nix#L18
  iptsd = prev.iptsd.overrideAttrs (old: rec {

    src = prev.fetchFromGitHub {
      owner = "iwanders";
      repo = "linux-surface-iptsd";
      rev = "4f1ac151358a0cf063055bcd42993adba31d508e";
      hash = "sha256-w5+fwfcTLJu6TTrSzhbPBZCFFUs4VIOYNOih11L93fY=";
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
