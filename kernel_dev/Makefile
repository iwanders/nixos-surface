ifneq ($(KERNELRELEASE),)
obj-m += surface_fan.o

else
KERNELDIR ?= /lib/modules/$(shell uname -r)/build
PWD := $(shell pwd)

default:
	$(MAKE) -C $(KERNELDIR) M=$(PWD)  modules

modules_install:
	$(MAKE) -C $(KERNELDIR) M=$(PWD) modules_install

clean:
	$(MAKE) -C $(KERNELDIR) M=$(PWD) clean

devshell:
	export KERNELDIR=$(nix build --print-out-paths "$(shell realpath /run/booted-system/flake)#nixosConfigurations.papyrus.config.boot.kernelPackages.kernel.dev")/lib/modules/*/build
	nix develop "$(realpath /run/booted-system/flake)#nixosConfigurations.$(shell hostname).config.boot.kernelPackages.kernel"

endif