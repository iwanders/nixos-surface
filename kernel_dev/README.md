# Kernel development


Still working on the whole in tree build, but out of tree finally works with:

```
nix develop "$(realpath /run/booted-system/flake)#nixosConfigurations.$(hostname).config.boot.kernelPackages.kernel"
export KERNELDIR=$(nix build --print-out-paths "$(realpath /run/booted-system/flake)#nixosConfigurations.papyrus.config.boot.kernelPackages.kernel.dev")/lib/modules/*/build
```

And then the [Makefile](https://github.com/Mic92/uptime_hack) from the [very useful blog post](https://blog.thalheim.io/2022/12/17/hacking-on-kernel-modules-in-nixos/).
