# NixOS Surface

Trying out NixOS on a Microsoft Surface Pro 9. Mostly keeping notes for myself and just to store the
NixOS configuration for it.

Hostname for my system is [papyrus](https://en.wikipedia.org/wiki/Papyrus), so that will pop up in
random commands.

I moved notes and scripts from development into the [linux-surface-dev](https://github.com/iwanders/linux-surface-dev)
repo to not clutter my nix files here.

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
nix fmt
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
nix-env --delete-generations --profile /nix/var/nix/profiles/system  +5
```

### Build the recovery image
The `flake.nix` file has some custom settings for generating a recovery image that includes this repository in the `/home/nixos/nixos-surface/` path.

The USB image can be built with:
```
nix build .#nixosConfigurations.recovery.config.system.build.isoImage --out-link recovery.priv.result -L
```

## Installation

Some quick notes for myself.

Bios: Volume up while turning on.

Boot from USB: Volume down while turning on.

Disabling secure boot in the bios does trigger Windows' bitlocker thing, prompting for the recovery
key.

### Installing windows

It is nigh impossible to resize the EFI partition after Windows is installed. I tried following a few 
guides from stackoverflow, but managed to brick Windows several times. In the end I followed [this](https://superuser.com/a/1308330)
stackoverflow answer on how to install Windows with a differently sized efi partition:

1. In the windows installer, go to the partition selection.
2. Press `shift + f10` to open a prompt. 
3. Start `diskpart`.
4. List disks with `list disk`, identify your harddisk's number.
5. Use `select disk 0` (or number from step 4).
6. Create EFI with your size `create partition efi size=1000`, size is in MiB.
7. Exit diskpart with `exit`
8. Click refresh in the partition selection. 

### Partition & filesystem

Original setup was:

> I resized the Windows partition from Windows, resize it, then from a live cd use `fdisk -l`, record
the size. Then from Windows I created an NTFS partition in the now available space. Both look the
same from the linux side (both ntfs); use the size to distinguish.

With the new harddisk I used `fdisk` to create two new partitions;

```
nvme0n1     259:0    0 931.5G  0 disk 
├─nvme0n1p1 259:1    0  1000M  0 part 
├─nvme0n1p2 259:9    0    16M  0 part 
├─nvme0n1p3 259:10   0   230G  0 part 
├─nvme0n1p4 259:11   0    50G  0 part 
└─nvme0n1p5 259:12   0 650.5G  0 part 
```

A 50 GB disk in case I need to transfer between operating systems, then a 650gb disk
to be used for NixOS.

The, we proceed with setup, [guided by NixOS full disk encryption](https://nixos.wiki/wiki/Full_Disk_Encryption#zimbatm.27s_laptop_recommendation):


```
# Setup luks
cryptsetup luksFormat /dev/nvme0n1p5
# Open the encrypted partition.
cryptsetup luksOpen /dev/nvme0n1p5 cryptroot
```

I installed btrfs on that cryptroot partition;
I went with btrfs, blew away the ntfs file system with:
```
[root@nixos:~]# mkfs.btrfs -f -L nixos /dev/mapper/cryptroot
...
Devices:
   ID        SIZE  PATH
    1   650.52GiB  /dev/mapper/cryptroot
```

Then, subvolume creation:
```
[root@nixos:~]# mount /dev/mapper/cryptroot /mnt

[root@nixos:/mnt]# btrfs subvolume create /mnt/root
Create subvolume '/mnt/root'

[root@nixos:/mnt]# btrfs subvolume create /mnt/home
Create subvolume '/mnt/home'

[root@nixos:/mnt]# btrfs subvolume create /mnt/nix
Create subvolume '/mnt/nix'

# Now unmount /mnt;
umount /mnt

```

Followed by mounting the respectivy btrfs subvolumes:
```
[root@nixos:/]# mount -o compress=zstd,subvol=root /dev/mapper/cryptroot /mnt

[root@nixos:/]# mkdir /mnt/{home,nix}

[root@nixos:/]# mount -o compress=zstd,subvol=home /dev/mapper/cryptroot /mnt/home

[root@nixos:/]# mount -o compress=zstd,noatime,subvol=nix /dev/mapper/cryptroot /mnt/nix

# and finally, mount the EFI partition into boot;

[root@nixos:/]# mkdir /mnt/boot

[root@nixos:/]# mount /dev/nvme0n1p1 /mnt/boot
```

So then we end up with;
```
# lsblk
NAME          MAJ:MIN RM   SIZE RO TYPE  MOUNTPOINTS
loop0           7:0    0 799.6M  1 loop  /nix/.ro-store
sda             8:0    1  29.8G  0 disk  
├─sda1          8:1    1   833M  0 part  /iso
└─sda2          8:2    1     3M  0 part  
nvme0n1       259:0    0 931.5G  0 disk  
├─nvme0n1p1   259:1    0  1000M  0 part  /mnt/boot
├─nvme0n1p2   259:9    0    16M  0 part  
├─nvme0n1p3   259:10   0   230G  0 part  
├─nvme0n1p4   259:11   0    50G  0 part  
└─nvme0n1p5   259:12   0 650.5G  0 part  
  └─cryptroot 254:0    0 650.5G  0 crypt /mnt/nix
                                         /mnt/home
                                         /mnt

# mount -l
/dev/mapper/cryptroot on /mnt type btrfs (rw,relatime,compress=zstd:3,ssd,space_cache=v2,subvolid=256,subvol=/root) [nixos]
/dev/mapper/cryptroot on /mnt/home type btrfs (rw,relatime,compress=zstd:3,ssd,space_cache=v2,subvolid=257,subvol=/home) [nixos]
/dev/mapper/cryptroot on /mnt/nix type btrfs (rw,noatime,compress=zstd:3,ssd,space_cache=v2,subvolid=258,subvol=/nix) [nixos]
/dev/nvme0n1p1 on /mnt/boot type vfat (rw,relatime,fmask=0022,dmask=0022,codepage=437,iocharset=iso8859-1,shortname=mixed,errors=remount-ro)

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

Then, do the install with;
```
cd /mnt
nixos-install
```


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

### Recovery if Windows uninstalls / disables the bootloader
Boot live cd, then manually mount the partitions with:
```
cryptsetup luksOpen /dev/nvme0n1p6 cryptroot
mount -o compress=zstd,subvol=root /dev/mapper/cryptroot /mnt
mount -o compress=zstd,subvol=home /dev/mapper/cryptroot /mnt/home
mount -o compress=zstd,noatime,subvol=nix /dev/mapper/cryptroot /mnt/nix
mount /dev/nvme0n1p1 /mnt/boot
```

Chroot to our real system that's now at `/mnt/`:
```
nixos-enter
```
Calling it without arguments uses the root at `/mnt`

First attempt was:
```
# nixos-rebuild switch --flake .#papyrus
```
But that complained about systemd-boot not being installed in ESP, which
was likely the problem in the first place, that was fixed with:
```
bootctl install
```

Boot now succeeded.

Build the recovery image with `nix build .#nixosConfigurations.recovery.config.system.build.isoImage`.

## Misc config

Give gnome minimize and maximize buttons;
```
gsettings set org.gnome.desktop.wm.preferences button-layout "appmenu:minimize,maximize,close"
```
(Default is `appmenu:close`).

# Flake reminders

- This flake is always available in `/run/booted-system/flake/`, flake `current` is that.
- The `current#pkgs` points to `nixosConfigurations.papyrus.pkgs`.
- The `nixpkgs#` flake points at the pinned upstream nixpkgs without overlays.


# Todo

- On screen keyboard
  - [x] Figure out how to make the gnome onscreen keyboard display normal `!@#$%^&*()_+` symbols. Forked [enhanced osk](https://github.com/iwanders/gnome-enhanced-osk-extension).
  - [x] Make on screen keyboard not waste precious pixels. Filed https://github.com/cass00/enhanced-osk-gnome-ext/pull/7
  - [x] Make the new on screen keyboard appear in lock screen. Magically solved itself with the reinstall...
  - [x] Give it an 'inhibit' option, where it doesn't automatically pops up when you click text, for when you have the typecover attached.
  - [x] Extension is again gone in gdm, fixed with the gnome dconf database now such that it's always good.

- Pen
  - [This tool is probably helpful](https://patrickhlauke.github.io/touch/pen-tracker/)
  - [x] Check the false positive pen thumb-button clicks in gimp, [these](https://github.com/linux-surface/iptsd/issues/102) and [issues](https://github.com/quo/iptsd/issues/5) may be applicable. Filed [this](https://github.com/linux-surface/iptsd/pull/156).
  - [x] Pen contact detection is also glitchy.
  - [x] Ensure pen talks libwacom? [libwacom-surface](https://github.com/linux-surface/libwacom-surface/tree/master) and [libwacom](https://github.com/linux-surface/libwacom), linux-surface [wiki](https://github.com/linux-surface/linux-surface/wiki/Installation-and-Setup) mentions [this flake](https://github.com/hpfr/system/blob/2e5b3b967b0436203d7add6adbd6b6f55e87cf3c/hosts/linux-surface.nix). Is this relevant? Not really, marking as done.

- Power / Battery
  - [x] Suspended over night, drained 68% to 45%, did not wake from suspend in the morning, this type cover issue [where it can't wake from suspend in some conditions seems applicable](https://github.com/linux-surface/linux-surface/issues/1183). Currently disabled the buttons, see also [this issue](https://github.com/linux-surface/linux-surface/issues/1224) and [wiki entry](https://github.com/linux-surface/linux-surface/wiki/Known-Issues-and-FAQ#suspend-aka-sleep-vs-lid-closingopening-events). Likely caused by incorrect suspend from cover.
  - [x] Can we investigate trickle charging / not keeping battery at 100% for longevity? Battery charge IC likely is `BQ25713`. See [smart charging](https://support.microsoft.com/en-us/surface/smart-charging-on-surface-dda48e48-950b-421c-a436-c48c55e158c4), ruled out by `BatteryDm.cs`, it explicitly throws when trying to ste it to true, likely really not possible. 
  - [x] Disabled `enable_psr` for now to mitigate screen flickering, could pursue it against latest kernel, intel seems to be [doing work on it](https://lore.kernel.org/all/PH7PR11MB59817424A663BFE56322E1ADF9472@PH7PR11MB5981.namprd11.prod.outlook.com/).


- Thermal stuff
  - [x] Make fans turn on quicker, may just be a matter of installing thermald? Even on windows things get pretty hot, maybe that's normal? Research!
  - [x] Logging messages from windows, all the way from boot. [irpmon wiki improvements](https://github.com/MartinDrab/IRPMon/issues/113)
  - [x] Make fan rpm monitoring module: https://github.com/linux-surface/kernel/pull/144
  - [x] Make platform profile switch the fan profile: https://github.com/linux-surface/kernel/pull/145
  - [x] Have to make `thermald` do the thing instead, figure this out, contrib config to [thermald contrib dir](https://github.com/linux-surface/linux-surface/tree/master/contrib/thermald). Thermald is really hard to configure, are there alternatives? Can't find alternatives, current profile is clunky, but at least we don't to the overheat stage. Currently piggybacks off of wifi, should revisit once [this](https://github.com/linux-surface/surface-aggregator-module/issues/59) is merged. Good enough for now, but should get more tuning before contrib upstream.

- OS / System / Nix stuff
  - [x] Deploy some encryption, either LUKS & TPM or ecryptfs on the homedir. See also [this](https://github.com/linux-surface/linux-surface/wiki/Disk-Encryption), now using LUKS2, typecover works with appropriate kernel modules.
  - [x] Fix multiboot clock, done by setting the registry key found in the [windows](./windows) subdirectory.
  - [x] Create live cd with this readme and config, in case we need to recover.
  - [x] Sometimes we can't type at the full disk encryption page, if we use USB keyboard, only half of the kernel modules get loaded, platform profile for example is missing. Not seen since kernel update.



# Contribution / PR tracking

- Added instructions for boot logging to the IRPMon wiki: https://github.com/MartinDrab/IRPMon/issues/113
- Surface Fan module. https://github.com/linux-surface/kernel/pull/144  [upstream kernel v5 thread](https://lore.kernel.org/linux-hwmon/20240131005856.10180-1-ivor@iwanders.net/T/)
- Platform profile, switch fan profile. https://github.com/linux-surface/kernel/pull/145
- Surface Aggregator Module: IRPMon conversion script improvements. https://github.com/linux-surface/surface-aggregator-module/pull/66
- Forked gnome OSK to https://github.com/iwanders/gnome-enhanced-osk-extension
- Contribute back enhanced OSK suggestions bar: https://github.com/cass00/enhanced-osk-gnome-ext/pull/7
- Contribute mppv2+ / Slim Pen 2 fixes to iptsd: https://github.com/linux-surface/iptsd/pull/156

