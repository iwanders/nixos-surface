# NixOS Surface

Trying out NixOS on a Microsoft Surface Pro 9. Mostly keeping notes for myself and just to store the
NixOS configuration for it.



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

