{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/release-23.11";
    nixos-hardware.url = "github:iwanders/nixos-hardware/ms-surface-give-iptsd-options";
  };

  outputs = { self, nixpkgs, nixos-hardware }: {
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
          '';
        }
      ];
    };
    inherit nixpkgs;
  };
}
