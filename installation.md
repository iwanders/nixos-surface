# NixOS Surface

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

