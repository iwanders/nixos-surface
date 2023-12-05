#!/bin/bash

# This totally not nixy way... should be `nix develop .`
nix develop "$(realpath /run/booted-system/flake)#nixosConfigurations.$(hostname).config.boot.kernelPackages.kernel"
export KERNELDIR=$(nix build --print-out-paths "$(realpath /run/booted-system/flake)#nixosConfigurations.papyrus.config.boot.kernelPackages.kernel.dev")/lib/modules/*/build
