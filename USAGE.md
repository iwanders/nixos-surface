# Usage

Some notes regarding usage


## Mounting iOS devices

Automatic mounting in nautilus doesn't work; [issue](https://github.com/NixOS/nixpkgs/issues/152592), use this as a workaround:
```
mkdir /tmp/iphone
ifuse /tmp/iphone
```
