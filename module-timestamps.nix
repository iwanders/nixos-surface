{ config, lib, pkgs, ... }:
let 
in {
  imports = [ ];
  # https://www.reddit.com/r/NixOS/comments/17ilg97/anyone_know_how_to_show_the_time_of_configuration/
  # https://github.com/NixOS/nixpkgs/pull/366958
  # This errors.

  options = { 
    system.build.installBootLoader = lib.mkOption {
      apply = old_sh:
        pkgs.writeShellScript "wrap-boot-loader-install" ''
set -x
            old_pl=$(${pkgs.gawk}/bin/awk '/-install-grub.pl/ { print $2 }' ${old_sh})
            new_pl=$(${pkgs.coreutils}/bin/mktemp --suffix=.pl)
            ${pkgs.gnused}/bin/sed 's/%F/%F %H:%M/' "$old_pl" > "$new_pl"
            new_sh=$(${pkgs.coreutils}/bin/mktemp --suffix=.sh)
            ${pkgs.gawk}/bin/awk -v new_pl="$new_pl" '/-install-grub.pl/ { $2 = new_pl } 1' ${old_sh} > "$new_sh"
            ${pkgs.coreutils}/bin/chmod +x "$new_sh"
            "$new_sh" "$@"
          '';
    };
  };

  config = {

  };
}
