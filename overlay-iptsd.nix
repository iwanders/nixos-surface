final: prev: {

  # From https://github.com/NixOS/nixpkgs/blob/69f966b3410d0f1caf97fb6dea639cef6fa15df4/pkgs/applications/misc/iptsd/default.nix#L18
  iptsd = prev.iptsd.overrideAttrs (old: rec {
        
    version = "1.4.0";

    src = prev.fetchFromGitHub {
      owner = "linux-surface";
      repo = old.pname;
      rev = "v${version}";
      hash = "sha256-qBABt0qEePGrZH4khnikvStrSi/OVmP3yVMJZbEd36M=";
    };

    # Original installs udev rules and service config into global paths
    postPatch = ''
      substituteInPlace etc/meson.build \
        --replace "install_dir: unitdir" "install_dir: '$out/etc/systemd/system'" \
        --replace "install_dir: rulesdir" "install_dir: '$out/etc/udev/rules.d'"
      substituteInPlace etc/systemd/iptsd-find-service \
        --replace "iptsd-find-hidraw" "$out/bin/iptsd-find-hidraw" \
        --replace "systemd-escape" "${prev.systemd}/bin/systemd-escape "systemd-escape"}"
      substituteInPlace etc/udev/50-iptsd.rules.in \
        --replace "systemd-escape" "${prev.systemd}/bin/systemd-escape "systemd-escape"}"
    '';
  });
}
