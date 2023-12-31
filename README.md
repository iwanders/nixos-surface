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

## Random things

keyboard backlight
```
$/home/ivor/.nix-profile/bin/python ./ctrl.py request 0x17 2 1 1 0 0

$/home/ivor/.nix-profile/bin/python ./ctrl.py request 0x17 2 1 1 0 1
```

# Flake reminders

- This flake is always available in `/run/booted-system/flake/`, flake `current` is that.
- The `current#pkgs` points to `nixosConfigurations.papyrus.pkgs`.
- The `nixpkgs#` flake points at the pinned upstream nixpkgs without overlays.


# Todo

- On screen keyboard
  - [x] Figure out how to make the gnome onscreen keyboard display normal `!@#$%^&*()_+` symbols. Forked [enhanced osk](https://github.com/iwanders/gnome-enhanced-osk-extension).
  - [x] Make on screen keyboard not waste precious pixels. Filed https://github.com/cass00/enhanced-osk-gnome-ext/pull/7

- Pen
  - [This tool is probably helpful](https://patrickhlauke.github.io/touch/pen-tracker/)
  - [x] Check the false positive pen thumb-button clicks in gimp, [these](https://github.com/linux-surface/iptsd/issues/102) and [issues](https://github.com/quo/iptsd/issues/5) may be applicable. 
  - [ ] Pen contact detection is also glitchy.
  - [ ] Ensure pen talks libwacom? [libwacom-surface](https://github.com/linux-surface/libwacom-surface/tree/master) and [libwacom](https://github.com/linux-surface/libwacom), linux-surface [wiki](https://github.com/linux-surface/linux-surface/wiki/Installation-and-Setup) mentions [this flake](https://github.com/hpfr/system/blob/2e5b3b967b0436203d7add6adbd6b6f55e87cf3c/hosts/linux-surface.nix).

- Power / Battery
  - [ ] Suspended over night, drained 68% to 45%, did not wake from suspend in the morning, this type cover issue [where it can't wake from suspend in some conditions seems applicable](https://github.com/linux-surface/linux-surface/issues/1183).
  - [ ] Can we investigate trickle charging / not keeping battery at 100% for longevity? Battery charge IC likely is `BQ25713`.

- Thermal stuff
  - [x] Make fans turn on quicker, may just be a matter of installing thermald? Even on windows things get pretty hot, maybe that's normal? Research!
  - [x] Logging messages from windows, all the way from boot. [irpmon wiki improvements](https://github.com/MartinDrab/IRPMon/issues/113)
  - [ ] Make fan rpm monitoring module: https://github.com/linux-surface/kernel/pull/144
  - [ ] Make platform profile switch the fan profile: https://github.com/linux-surface/kernel/pull/145
  - [ ] Have to make `thermald` do the thing instead, figure this out, contrib config to [thermald contrib dir](https://github.com/linux-surface/linux-surface/tree/master/contrib/thermald).

- OS / System / Nix stuff
  - [ ] Deploy some encryption, either LUKS & TPM or ecryptfs on the homedir.
  - [ ] Look at home manager

# Contribution / PR tracking

- Added instructions for boot logging to the IRPMon wiki: https://github.com/MartinDrab/IRPMon/issues/113
- Surface Fan module. https://github.com/linux-surface/kernel/pull/144
- Platform profile, switch fan profile. https://github.com/linux-surface/kernel/pull/145
- Surface Aggregator Module: IRPMon conversion script improvements. https://github.com/linux-surface/surface-aggregator-module/pull/66
- Forked gnome OSK to https://github.com/iwanders/gnome-enhanced-osk-extension
- Contribute back enhanced OSK suggestions bar: https://github.com/cass00/enhanced-osk-gnome-ext/pull/7
