{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/release-23.11";
    nixos-hardware.url =
      "github:iwanders/nixos-hardware/ms-surface-build-linux-surface-kernel-from-repo";
  };

  outputs = { self, nixpkgs, nixos-hardware }: rec {
    nixosConfigurations.papyrus = nixpkgs.lib.nixosSystem {
      system = "x86_64-linux";
      modules = [
        ./configuration-base.nix
        ./configuration.nix
        nixos-hardware.nixosModules.microsoft-surface-pro-intel

        # From https://blog.thalheim.io/2022/12/17/hacking-on-kernel-modules-in-nixos/ this adds
        # the flake to /run/booted-system/
        {
          system.extraSystemBuilderCmds = ''
            ln -s ${self} $out/flake
            ln -s ${self.nixosConfigurations.papyrus.config.boot.kernelPackages.kernel.dev} $out/kernel-dev
          '';
        }

        # This here adds the current nixpkgs to the global flake registry
        # such that nix build nixpkgs#... refers to the pinned version.
        {
          nix.registry.nixpkgs.flake = nixpkgs;
        }
        # nix develop /nix/store/v9vnzqrpfx4qpn4zygcyg1bbw9b54m92-source#nixosConfigurations.papyrus.pkgs.iptsd
        # And this one here adds 'current' that has all the os specific overrides.
        {
          nix.registry.current.to = {
            type = "path";
            path = "/run/booted-system/flake/";
          };
        }
      ];
    };

    # Custom recovery image that has this repo embedded in it, for easy debugging.
    # nix build .#nixosConfigurations.recovery.config.system.build.isoImage
    nixosConfigurations.recovery = nixpkgs.lib.nixosSystem {
      system = "x86_64-linux";
      modules = [
        ./configuration-base.nix
        nixos-hardware.nixosModules.microsoft-surface-pro-intel

      # "${nixpkgs}/nixos/modules/installer/cd-dvd/installation-cd-graphical-gnome.nix"
        "${nixpkgs}/nixos/modules/installer/cd-dvd/installation-cd-minimal.nix"
        ({ pkgs, ... }: { environment.systemPackages = [ pkgs.vim ]; })

        {

          boot.supportedFilesystems = nixpkgs.lib.mkForce [
            "btrfs"
            "ext4"
            "f2fs"
            "ntfs"
            "vfat"
            "xfs"
            # Why do we need to comment this out to prevent rebuilding a kernel with zfs
            # as compared to my default config? That doesn't have to do this?
            #"zfs"
          ];
        }

        # This here adds the current nixpkgs to the global flake registry
        # such that nix build nixpkgs#... refers to the pinned version.
        {
          nix.registry.nixpkgs.flake = nixpkgs;
          nix.settings.experimental-features = [ "nix-command" "flakes" ];
        }

        ({ pkgs, ... }: {
          services.getty.helpLine = ''The repo can be found at /home/ivor/repo.'';
        })
        ({# Not sure if this here works... can't figure out how to avoid building the squashfs yet.
          system.extraSystemBuilderCmds = ''
            mkdir -p /home/ivor/repo
            ln -s ${self} /home/ivor/repo
          '';
        })
      ];
    };
    #inherit nixpkgs;

    # Such that we can do current#pkgs.<our overlayd nixpkgs>
    pkgs = nixosConfigurations.papyrus.pkgs;

    # Allow formatting with `nix fmt`
    formatter.x86_64-linux = nixpkgs.legacyPackages.x86_64-linux.nixfmt;
  };
}
