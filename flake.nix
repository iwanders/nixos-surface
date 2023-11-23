{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/release-23.05";
    nixos-hardware.url = "github:NixOS/nixos-hardware/master";
  };

  outputs = { self, nixpkgs, nixos-hardware }: {
    nixosConfigurations.papyrus = nixpkgs.lib.nixosSystem {
      system = "x86_64-linux";
      modules = [
        ./configuration.nix
        nixos-hardware.nixosModules.microsoft-surface-pro-intel
      ];
    };
    inherit nixpkgs;
  };
}
