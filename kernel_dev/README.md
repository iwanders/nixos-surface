# Kernel development


Still working on the whole in tree build, but out of tree finally works with:

```
nix develop "$(realpath /run/booted-system/flake)#nixosConfigurations.$(hostname).config.boot.kernelPackages.kernel"
export KERNELDIR=$(nix build --print-out-paths "$(realpath /run/booted-system/flake)#nixosConfigurations.papyrus.config.boot.kernelPackages.kernel.dev")/lib/modules/*/build
```

And then the [Makefile](https://github.com/Mic92/uptime_hack) from the [very useful blog post](https://blog.thalheim.io/2022/12/17/hacking-on-kernel-modules-in-nixos/).


### in tree notes

Then build the in-tree surface modules with:
```
export KERNELDIR=$(nix build --print-out-paths ".#nixosConfigurations.papyrus.config.boot.kernelPackages.kernel.dev")
# go to linux surface kernel tree, copy configuration from active system.
cp $KERNELDIR/lib/modules/*/build/.config .config
cp $KERNELDIR/lib/modules/6.5.11/build/Module.symvers .
# prepare build environment
make scripts prepare modules_prepare
make -C . M=drivers/platform/surface
```

This [post](https://blog.thalheim.io/2022/12/17/hacking-on-kernel-modules-in-nixos/) may be helpful.

Ah... the linux kernel tree I built in does not match the tree that my os is running; I branched from the surface kernel, which is different from the one used from my nixos configuration. I think.

