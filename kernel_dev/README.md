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

#### Building
Try to do a `W=1` build next time, [fan module patchset](https://lore.kernel.org/linux-hwmon/202402031253.JPVKEF5X-lkp@intel.com/T/#u) got a warning back. Easily reproduced with `-Wmissing-prototypes`.

Yes, build with;
```
make W=1
```


### Patches

Some notes for myself.

#### Setup
First, install `git send-email`, follow [this excellent tutorial](https://git-send-email.io/). Including the advice:

> Warning! Some people think that they can get away with sending patches through some means other than git send-email, but you can't. Your patches will be broken and a nuisance to the maintainers whose inbox they land in. Follow the golden rule: just use git send-email.


#### Preparing the patches

Rebase them on the latest `master` from Torvald's upstream repo.

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

#### Determine the receipients
```
./scripts/get_maintainer.pl *.patch
```
Gives a list of maintainers based on the modified files.

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


### Repro of failures;

[This linker error](https://lore.kernel.org/linux-hwmon/50af81da-779b-4782-9326-043bc204bfe6@gmail.com/#R)
```
reproduce:
        # apt-get install sparse
        # sparse version: v0.6.4-61-g09411a7a-dirty
        # https://git.kernel.org/pub/scm/linux/kernel/git/groeck/linux-staging.git/commit/?id=c3747f28ebcefe34d6ea2e4eb2d3bb6b9d574b5f
        git remote add groeck-staging https://git.kernel.org/pub/scm/linux/kernel/git/groeck/linux-staging.git
        git fetch --no-tags groeck-staging hwmon-next
        git checkout c3747f28ebcefe34d6ea2e4eb2d3bb6b9d574b5f
        # save the config file
        mkdir build_dir && cp config build_dir/.config
        make W=1 C=1 CF='-fdiagnostic-prefix -D__CHECK_ENDIAN__ -fmax-errors=unlimited -fmax-warnings=unlimited' O=build_dir ARCH=x86_64 olddefconfig
        make W=1 C=1 CF='-fdiagnostic-prefix -D__CHECK_ENDIAN__ -fmax-errors=unlimited -fmax-warnings=unlimited' O=build_dir ARCH=x86_64 SHELL=/bin/bash
```

[This missing prototype](https://lore.kernel.org/linux-hwmon/382a2754-f5b0-4c71-a292-7fe2095a45cb@roeck-us.net/T/#t)

```
reproduce (this is a W=1 build):
        git clone https://github.com/intel/lkp-tests.git ~/lkp-tests
        # https://git.kernel.org/pub/scm/linux/kernel/git/groeck/linux-staging.git/commit/?id=6652888f0379f01027bb1d7bbdb377710833b4f2
        git remote add groeck-staging https://git.kernel.org/pub/scm/linux/kernel/git/groeck/linux-staging.git
        git fetch --no-tags groeck-staging hwmon-next
        git checkout 6652888f0379f01027bb1d7bbdb377710833b4f2
        # save the config file
        mkdir build_dir && cp config build_dir/.config
        COMPILER_INSTALL_PATH=$HOME/0day COMPILER=gcc-13.2.0 ~/lkp-tests/kbuild/make.cross W=1 O=build_dir ARCH=loongarch olddefconfig
        COMPILER_INSTALL_PATH=$HOME/0day COMPILER=gcc-13.2.0 ~/lkp-tests/kbuild/make.cross W=1 O=build_dir ARCH=loongarch SHELL=/bin/bash drivers/hwmon/
```