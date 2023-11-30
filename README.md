# NixOS Surface

Trying out NixOS on a Microsoft Surface Pro 9. Mostly keeping notes for myself and just to store the
NixOS configuration for it.

Hostname for my system is [papyrus](https://en.wikipedia.org/wiki/Papyrus), so that will pop up in
random commands.

## Useful links;

- [NixOS configuration options](https://nixos.org/manual/nixos/stable/options)

## Useful Commands;

### Build top level:
To build the top level filesystem result, this also works from a non NixOS host;
```
nix build .#nixosConfigurations.papyrus.config.system.build.toplevel
```
From Brian McGee's [post](https://bmcgee.ie/posts/2022/12/setting-up-my-new-laptop-nix-style/) on
how to setup a nix machine.

When large local builds have to happen, add `-L` for logging and set the amount of build cores;
```
NIX_BUILD_CORES=10 nix build .#nixosConfigurations.papyrus.config.system.build.toplevel -L
```

Then, we can copy closure that with (assuming `ivor` is in `trusted-users`):
```
nix copy --to "ssh://ivor@papyrus" ./result
```

### Actually switch to the new config
```
nixos-rebuild switch --flake .#papyrus
```

### Format this repo
```
nix run nixpkgs/23.05#nixpkgs-fmt -- *.nix
```

### Discard old NixOS generations
List them with;
```
nix-env --list-generations --profile /nix/var/nix/profiles/system
```

Discard with;
```
nix-env --delete-generations --profile /nix/var/nix/profiles/system <number>
```

Discard all but most recent 5;
```
nix-env --delete-generations --profile /nix/var/nix/profiles/system  +2
```


## Installation

Some quick notes for myself.

Bios: Volume up while turning on.

Boot from USB: Volume down while turning on.

Disabling secure boot in the bios does trigger Windows' bitlocker thing, prompting for the recovery
key.

### Partition & filesystem
I resized the Windows partition from Windows, resize it, then from a live cd use `fdisk -l`, record
the size. Then from Windows I created an NTFS partition in the now available space. Both look the
same from the linux side (both ntfs); use the size to distinguish.

I went with btrfs, blew away the ntfs file system with:
```
[root@nixos:~]# mkfs.btrfs -f -L nixos /dev/nvme0n1p5
...
Devices:
   ID        SIZE  PATH
    1   118.54GiB  /dev/nvme0n1p5
```

Then, subvolume creation:
```
[root@nixos:~]# mount /dev/nvme0n1p5 /mnt

[root@nixos:/mnt]# btrfs subvolume create /mnt/root
Create subvolume '/mnt/root'

[root@nixos:/mnt]# btrfs subvolume create /mnt/home
Create subvolume '/mnt/home'

[root@nixos:/mnt]# btrfs subvolume create /mnt/nix
Create subvolume '/mnt/nix'
```

Followed by mounting;
```
[root@nixos:/]# mount -o compress=zstd,subvol=root /dev/nvme0n1p5 /mnt

[root@nixos:/]# mkdir /mnt/{home,nix}

[root@nixos:/]# mount -o compress=zstd,subvol=root /dev/nvme0n1p5 /mnt

[root@nixos:/]# mount -o compress=zstd,subvol=home /dev/nvme0n1p5 /mnt/home

[root@nixos:/]# mount -o compress=zstd,noatime,subvol=nix /dev/nvme0n1p5 /mnt/nix

# and finally, mount the EFI partition into boot;

[root@nixos:/]# mkdir /mnt/boot

[root@nixos:/]# mount /dev/nvme0n1p1 /mnt/boot
```

Then, the config can be generated;
```
[root@nixos:/]# nixos-generate-config --root /mnt/
writing /mnt/etc/nixos/hardware-configuration.nix...
writing /mnt/etc/nixos/configuration.nix...
For more hardware-specific settings, see https://github.com/NixOS/nixos-hardware.
```

Remember to edit `configuration.nix` to include [these options](https://github.com/iwanders/nixos-surface/blob/f6381fc11bc01aea1f2c7a338a701a8364142b84/configuration.nix#L41-L45) that would not be picked up if the `hardware-configuration.nix` file is ever regenerated.

Be sure to add `vim` to the system packages.

I did add myself as a user (as per the install manual) with
```
useradd -c 'Ivor' -m ivor
passwd ivor
```
and then added that user to `wheel` with [these lines](https://github.com/iwanders/nixos-surface/blob/1390c857bdce481f25ad90bfe0f543bcf82ede7a/configuration.nix#L61-L69). I'm not sure
why users need to be added manually if they're also in the `configuration.nix`.

### Connecting via SSH

Boot from minimal nixos image from usb, then run the 'start wifi' from the motd, then use:

```
$ wpa_cli
> add_network
0
> set_network 0 ssid "myhomenetwork"
OK
> set_network 0 psk "mypassword"
OK
> set_network 0 key_mgmt WPA-PSK
OK
> enable_network 0
OK
```

To connect to wifi, followed by giving `root` a password with `passwd`, then ssh in from another
machine by `ssh root@nixos`.

## Misc config

Give gnome minimize and maximize buttons;
```
gsettings set org.gnome.desktop.wm.preferences button-layout "appmenu:minimize,maximize,close"
```
(Default is `appmenu:close`).




# Todo

- Figure out how to make the gnome onscreen keyboard display normal `!@#$%^&*()_+` symbols.
- Check the false positive pen thumb button clicks in gimp, [these](https://github.com/linux-surface/iptsd/issues/102) and [issues](https://github.com/quo/iptsd/issues/5) may be applicable. [This tool is probably helpful](https://patrickhlauke.github.io/touch/pen-tracker/)
- Ensure pen talks libwacom? [libwacom-surface](https://github.com/linux-surface/libwacom-surface/tree/master) and [libwacom](https://github.com/linux-surface/libwacom), linux-surface [wiki](https://github.com/linux-surface/linux-surface/wiki/Installation-and-Setup) mentions [this flake](https://github.com/hpfr/system/blob/2e5b3b967b0436203d7add6adbd6b6f55e87cf3c/hosts/linux-surface.nix).
- Suspended over night, drained 68% to 45%, did not wake from suspend in the morning, this type cover issue [where it can't wake from suspend in some conditions seems applicable](https://github.com/linux-surface/linux-surface/issues/1183).
- Make fans turn on quicker, may just be a matter of installing thermald? Even on windows things get pretty hot, maybe that's normal?

  
## Notes on fan
Surface aggregator module; https://github.com/linux-surface/surface-aggregator-module/issues/64

Maybe we can sniff it with [irpmon](https://github.com/linux-surface/surface-aggregator-module/wiki/Development)?

```
sudo modprobe surface_aggregator_cdev
```

Return two bytes, zero when fan is off, increased as fan sped up, decreases as fan speeds down.
```
sudo python3 ctrl.py request 5 1 1 1 
[lower byte] [upper byte]
```

And fan speed control, last two bytes here:
```
sudo python3 ctrl.py request 5 1 11 1 0 185 20
sudo python3 ctrl.py request 5 1 11 1 0 0 0
```

Now, we need a kernel module that ties the acpi fan stuff to these commands. [fan_core](https://github.com/torvalds/linux/blob/18d46e76d7c2eedd8577fae67e3f1d4db25018b0/drivers/acpi/fan_core.c), the [surface platform_profile.c](https://github.com/linux-surface/kernel/blob/v6.5-surface-devel/drivers/platform/surface/surface_platform_profile.c) surface module seems to tie `platform_profile` to the `ssam` module, can probably follow that structure.

Prepare for the development shell with
```
nix build .#nixosConfigurations.papyrus.config.boot.kernelPackages.kernel.dev -L
nix develop .#nixosConfigurations.papyrus.config.boot.kernelPackages.kernel
```

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
