final: prev: {

  # From https://github.com/NixOS/nixpkgs/blob/69f966b3410d0f1caf97fb6dea639cef6fa15df4/pkgs/applications/misc/iptsd/default.nix#L18
  iptsd = prev.iptsd.overrideAttrs (old: rec {

    src = prev.fetchFromGitHub {
      owner = "iwanders";
      repo = "linux-surface-iptsd";
      rev = "aebfd31ebc2cb84ef2284ca683e6a6216b272fb4";
      hash = "sha256-bColMOOTPO7WK8ms0mhihx9CvYUGl97G1cCU5HdAlYk=";
    };

    buildInputs = old.buildInputs ++ [
      prev.cairomm
      prev.SDL2
    ];
    mesonFlags = [
      "-Dservice_manager=systemd"
      "-Dsample_config=false"
      "-Ddebug_tools=calibrate,dump,perf,plot"
      "-Db_lto=false"  # plugin needed to handle lto object -> undefined reference to ...
    ];
  });
}
