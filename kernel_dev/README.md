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



### Patches

Some notes for myself.

#### Setup
First, install `git send-email`, follow [this excellent tutorial](https://git-send-email.io/). Including the advice:

> Warning! Some people think that they can get away with sending patches through some means other than git send-email, but you can't. Your patches will be broken and a nuisance to the maintainers whose inbox they land in. Follow the golden rule: just use git send-email.


#### Preparing the patches
From [this comment](https://github.com/linux-surface/kernel/pull/144#issuecomment-1863385341), we learn that it is possible to use a cover letter, which is not really described in [the submitting patches](https://www.kernel.org/doc/html/v6.6/process/submitting-patches.html) guide.

So, we run:

```
git format-patch -2 --cover-letter
```

This generates three files, the first being `0000-cover-letter.patch`, we can populate this to hold our explanation of why this change is proposed.

Always run the checkpatch script!
```
./scripts/checkpatch.pl
```

From the forementioned comment (and some testing) we learn that we can add `To` headers to each patch file, allowing us to specify which mailing list each file will go to, while all emails still keep the same `in-reply-to` header. (This probably ties them all together on the mailing list archive?)

Ensure signed off by is present, use `git commit -s`.

#### Send it out
```
git send-email <files>
```

When copying the send mail command from lore, by default it drops the original 'to' fields to the 'cc', always re-evaluate these.

### Versions
Make versions with
```
git format-patch -# -v2 --cover-letter
```

**Always use a cover letter for follow up versions to describe the changes**.

If sending a v2 inline with other entries (don't do this, its not common), be sure to re-evaluate the suggested recipients from lore.

Put version log in the diff, convention is adding a `---` section at the end of the commit message (after the signed off by)

