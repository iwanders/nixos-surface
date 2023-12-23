{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/release-23.11";
    nixos-hardware.url = "github:iwanders/nixos-hardware/ms-surface-build-linux-surface-kernel-from-repo";
  };

  outputs = { self, nixpkgs, nixos-hardware }: rec {
    nixosConfigurations.papyrus = nixpkgs.lib.nixosSystem {
      system = "x86_64-linux";
      modules = [
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
          nix.registry.current.to =  {
            type = "path";
            path = "/run/booted-system/flake/";
          };
        }
      ];
    };
    #inherit nixpkgs;
    # Such that we can do current#pkgs.<our overlayd nixpkgs>
    pkgs = nixosConfigurations.papyrus.pkgs;
  };
}
