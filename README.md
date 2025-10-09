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

### Build specific packages from the overlays
```
nix build .#nixosConfigurations.papyrus.pkgs.gnome-eog-plugins
```

## Installation

See [./installation.md](./installation.md) for details on the installation procedure.


## Misc config

Give gnome minimize and maximize buttons;
```
gsettings set org.gnome.desktop.wm.preferences button-layout "appmenu:minimize,maximize,close"
```
(Default is `appmenu:close`).

Ensure the file explorer always gives the location/path as a text box with a string instead of buttons;
```
gsettings set org.gnome.nautilus.preferences always-use-location-entry true
```
From [here](https://www.reddit.com/r/gnome/comments/8m2kf9/enable_url_bar_in_gnome_files/).

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
  - [ ] Machine shut down if on LUKS password in initram fs for 'n' seconds. To avoid draining battery if accidentally powered on. Perhaps with [something like this](https://bbs.archlinux.org/viewtopic.php?pid=2176578#p2176578).

- Misc usability
  - [x] Eye of Gnome [plugins](https://wiki.gnome.org/Apps(2f)EyeOfGnome(2f)Plugins.html) for [slideshowshuffle](https://help.gnome.org/users/eog/stable/plugin-slideshow-shuffle.html.en), [commit](https://github.com/iwanders/nixos-surface/commit/7c06fe62928fd5f073e84ece7eb42ccc5638da5c).
  - [x] Changing wifi settings without password [commit](https://github.com/iwanders/nixos-surface/commit/59a8c4ebf5c25628c7428d1b1af00276d49b7587).
  - [x] Caja show location as textbox [commit](https://github.com/iwanders/nixos-surface/commit/dd60564e8ebd76a722f231fb073518a579e65f22).
  - [ ] Caja HEIC thumbnails?
  - [ ] Does 'declutter' exist to hide the cursor?
  - [ ] mpv volume persistance [this](https://github.com/mpv-player/mpv/issues/1913#issuecomment-1127102576).

# Contribution / PR tracking

- Added instructions for boot logging to the IRPMon wiki: https://github.com/MartinDrab/IRPMon/issues/113
- Surface Fan module. https://github.com/linux-surface/kernel/pull/144  [upstream kernel v5 thread](https://lore.kernel.org/linux-hwmon/20240131005856.10180-1-ivor@iwanders.net/T/)
- Platform profile, switch fan profile. https://github.com/linux-surface/kernel/pull/145
- Surface Aggregator Module: IRPMon conversion script improvements. https://github.com/linux-surface/surface-aggregator-module/pull/66
- Forked gnome OSK to https://github.com/iwanders/gnome-enhanced-osk-extension
- Contribute back enhanced OSK suggestions bar: https://github.com/cass00/enhanced-osk-gnome-ext/pull/7
- Contribute mppv2+ / Slim Pen 2 fixes to iptsd: https://github.com/linux-surface/iptsd/pull/156


