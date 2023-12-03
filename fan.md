# Surface fan

A totally incoherent dump of things.


Surface aggregator module; https://github.com/linux-surface/surface-aggregator-module/issues/64



Maybe we can sniff it with [irpmon](https://github.com/linux-surface/surface-aggregator-module/wiki/Development)?

```
sudo modprobe surface_aggregator_cdev
```

Return two bytes, zero when fan is off, increased as fan sped up, decreases as fan speeds down.
```
sudo python3 ctrl.py request 5 1 1 1 1
[lower byte] [upper byte]
```

And fan speed control, last two bytes here:
```
sudo python3 ctrl.py request 5 1 11 1 0 185 20
sudo python3 ctrl.py request 5 1 11 1 0 0 0
```

Now, we need a kernel module that ties the acpi fan stuff to these commands. [fan_core](https://github.com/torvalds/linux/blob/18d46e76d7c2eedd8577fae67e3f1d4db25018b0/drivers/acpi/fan_core.c), the [surface platform_profile.c](https://github.com/linux-surface/kernel/blob/v6.5-surface-devel/drivers/platform/surface/surface_platform_profile.c) surface module seems to tie `platform_profile` to the `ssam` module, can probably follow that structure.

Requests;
```

# /home/ivor/.nix-profile/bin/python ./ctrl.py request 5 1 0 1 1
TimeoutError: [Errno 110] ETIMEDOUT

# /home/ivor/.nix-profile/bin/python ./ctrl.py request 5 1 1 1 1
32 11

# Later, after rebooting windows;
00 00 

# /home/ivor/.nix-profile/bin/python ./ctrl.py request 5 1 2 1 1
 00 00 00 40 00 00 00 3f cd cc 4c 3e 14 64
| 2.0 f32  | 0.5 f32    | 0.2 f32   |
# unmodified after reboot.

# /home/ivor/.nix-profile/bin/python ./ctrl.py request 5 1 3 1 1
01

# /home/ivor/.nix-profile/bin/python ./ctrl.py request 5 1 4 1 1
01 00 51 75 69 65 74 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 b8 0b 00 00 31 0c 14 00 3b 0c bd 0c 28 00 00 00 c8 41 64 00 63 0c 00 00 00 00 00 00 00 00
\x01\x00Quiet\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00¸\x0b\x00\x001\x0c\x14\x00;\x0c½\x0c(\x00\x00\x00ÈAd\x00c\x0c\x00\x00\x00\x00\x00\x00\x00\x00

40 bytes total

Split in 20 bytes:
01 00 51 75 69 65 74 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
     | name
00 00 b8 0b 00 00 31 0c 14 00 3b 0c bd 0c 28 00 00 00 c8 41 64 00 63 0c 00 00 00 00 00 00 00 00
     |3000u|     |3121|                        |25.0 f32   |     |3171u|

# /home/ivor/.nix-profile/bin/python ./ctrl.py request 5 1 5 1 1
01 00 4f 76 65 72 72 69 64 65 00 00 00 00 00 00 00 00 00 00 00 00 f0 41 00 00 00 00 00 00 00 00 40 1f b8 0b 34 21 3b 0c 14 00 45 0c 03 0d 28 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
\x01\x00Override\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00ðA\x00\x00\x00\x00\x00\x00\x00\x00@\x1f¸\x0b4!;\x0c\x14\x00E\x0c\x03\r(\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
40 bytes, split in 20 bytes:
01 00 4f 76 65 72 72 69 64 65 00 00 00 00 00 00 00 00 00 00 00 00 f0 41 00 00 00 00 00 00 00 00
                                                                 |16880u...
                                                           |30.0 f32   |

40 1f b8 0b 34 21 3b 0c 14 00 45 0c 03 0d 28 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
8000u|3000u|8500u|3131u|20   |3141u|3331u|40

# /home/ivor/.nix-profile/bin/python ./ctrl.py request 5 1 6 1 1
33 33 ff ff b8 0b f8 2a ff 3f f4 01 64 00 85 ab 35 43 cd 9c 12 c4 00 00 00 00
           |3000u|11e3u|                 |181.67 f32 |-586.45 f32| 

# /home/ivor/.nix-profile/bin/python ./ctrl.py request 5 1 7 1 1
01 00 00 00 09 00 00 00 00 00 00 00 00 00 00 00 32 00 00 00 4a 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00

# After restarting windows;
# /home/ivor/.nix-profile/bin/python ./ctrl.py request 5 1 7 1 1
01 00 00 00 09 00 00 00 ef 04 00 00 90 00 00 00 d1 00 00 00 f3 00 00 00 05 00 00 00 05 00 00 00 32 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00


# /home/ivor/.nix-profile/bin/python ./ctrl.py request 5 1 8 1 1
00

# /home/ivor/.nix-profile/bin/python ./ctrl.py request 5 1 9 1 1
1a ae 00 00
44570|0
# Later, after I managed to wipe it and it reported 0 0 0 1, after starting windows:
# /home/ivor/.nix-profile/bin/python ./ctrl.py request 5 1 9 1 1
05 10 cc 10
4101u|4300u

# Next day
# /home/ivor/.nix-profile/bin/python ./ctrl.py request 5 1 9 1 1
6d 07 3c 0f
1901u|3900u

Some temporary target? Maybe the desired setpoint??

# /home/ivor/.nix-profile/bin/python ./ctrl.py request 5 1 10 1 1
TimeoutError: [Errno 110] ETIMEDOUT

# /home/ivor/.nix-profile/bin/python ./ctrl.py request 5 1 11 1 1
TimeoutError: [Errno 110] ETIMEDOUT

# /home/ivor/.nix-profile/bin/python ./ctrl.py request 5 1 12 1 1
TimeoutError: [Errno 110] ETIMEDOUT

# /home/ivor/.nix-profile/bin/python ./ctrl.py request 5 1 13 1 1
00 00 f0 41
Float 30.0?!
# unmodified after reboot

# /home/ivor/.nix-profile/bin/python ./ctrl.py request 5 1 14 1 1
TimeoutError: [Errno 110] ETIMEDOUT

# /home/ivor/.nix-profile/bin/python ./ctrl.py request 5 1 15 1 1
TimeoutError: [Errno 110] ETIMEDOUT

# /home/ivor/.nix-profile/bin/python ./ctrl.py request 5 1 16 1 1
01
# unmodified after reboot
# /home/ivor/.nix-profile/bin/python ./ctrl.py request 5 1 17 1 1
1d
# unmodified after reboot
# /home/ivor/.nix-profile/bin/python ./ctrl.py request 5 1 17 1 1
1d
# unmodified after reboot
# /home/ivor/.nix-profile/bin/python ./ctrl.py request 5 1 18 1 1
TimeoutError: [Errno 110] ETIMEDOUT

# /home/ivor/.nix-profile/bin/python ./ctrl.py request 5 1 19 1 1
TimeoutError: [Errno 110] ETIMEDOUT

# /home/ivor/.nix-profile/bin/python ./ctrl.py request 5 1 20 1 1
TimeoutError: [Errno 110] ETIMEDOUT

# /home/ivor/.nix-profile/bin/python ./ctrl.py request 5 1 21 1 1
TimeoutError: [Errno 110] ETIMEDOUT

# /home/ivor/.nix-profile/bin/python ./ctrl.py request 5 1 22 1 1
TimeoutError: [Errno 110] ETIMEDOUT

# /home/ivor/.nix-profile/bin/python ./ctrl.py request 5 1 23 1 1
TimeoutError: [Errno 110] ETIMEDOUT

# /home/ivor/.nix-profile/bin/python ./ctrl.py request 5 1 24 1 1
TimeoutError: [Errno 110] ETIMEDOUT

# 
```

Sniff with irpmon with platform switches;
```
{"ctrl": {"type": 64, "len": 0, "pad": 0, "seq": 124}}, {"ctrl": {"type": 128, "len": 12, "pad": 0, "seq": 12}, "cmd": {"type": 128, "tc": 3, "sid": 0, "tid": 1, "iid": 0, "rqid_lo": 53, "rqid_hi": 7, "cid": 3}, "payload": [3, 0, 0, 0], "time": "2023-12-03 12:42:53 AM"}, 
{"ctrl": {"type": 64, "len": 0, "pad": 0, "seq": 13}}, {"ctrl": {"type": 128, "len": 9, "pad": 0, "seq": 14}, "cmd": {"type": 128, "tc": 5, "sid": 0, "tid": 1, "iid": 1, "rqid_lo": 55, "rqid_hi": 7, "cid": 14}, "payload": [3], "time": "2023-12-03 12:42:53 AM"}, 

{"ctrl": {"type": 64, "len": 0, "pad": 0, "seq": 126}}, {"ctrl": {"type": 128, "len": 12, "pad": 0, "seq": 17}, "cmd": {"type": 128, "tc": 3, "sid": 0, "tid": 1, "iid": 0, "rqid_lo": 58, "rqid_hi": 7, "cid": 3}, "payload": [4, 0, 0, 0], "time": "2023-12-03 12:42:58 AM"}, 
{"ctrl": {"type": 64, "len": 0, "pad": 0, "seq": 18}}, {"ctrl": {"type": 128, "len": 9, "pad": 0, "seq": 19}, "cmd": {"type": 128, "tc": 5, "sid": 0, "tid": 1, "iid": 1, "rqid_lo": 60, "rqid_hi": 7, "cid": 14}, "payload": [4], "time": "2023-12-03 12:42:58 AM"}, 

{"ctrl": {"type": 64, "len": 0, "pad": 0, "seq": 130}}, {"ctrl": {"type": 128, "len": 12, "pad": 0, "seq": 24}, "cmd": {"type": 128, "tc": 3, "sid": 0, "tid": 1, "iid": 0, "rqid_lo": 65, "rqid_hi": 7, "cid": 3}, "payload": [1, 0, 0, 0], "time": "2023-12-03 12:43:01 AM"}, 
{"ctrl": {"type": 64, "len": 0, "pad": 0, "seq": 25}}, {"ctrl": {"type": 128, "len": 9, "pad": 0, "seq": 26}, "cmd": {"type": 128, "tc": 5, "sid": 0, "tid": 1, "iid": 1, "rqid_lo": 67, "rqid_hi": 7, "cid": 14}, "payload": [2], "time": "2023-12-03 12:43:01 AM"}, 

```

Shows a fan command going out with a platform change, probably switches the mode? But from the fan dump we know there's just two profiles, Quiet and Override. Switching this actively from linux with a hot tablet does not change the fan speeds.

```
rg '"tc": 5' cpu_load.json 
440:{"ctrl": {"type": 64, "len": 0, "pad": 0, "seq": 237}}, {"ctrl": {"type": 128, "len": 8, "pad": 0, "seq": 106}, "cmd": {"type": 128, "tc": 5, "sid": 1, "tid": 0, "iid": 1, "rqid_lo": 5, "rqid_hi": 0, "cid": 10}, "payload": [], "time": "2023-12-03 1:54:47 AM"},
442:{"ctrl": {"type": 64, "len": 0, "pad": 0, "seq": 107}}, {"ctrl": {"type": 128, "len": 8, "pad": 0, "seq": 238}, "cmd": {"type": 128, "tc": 5, "sid": 0, "tid": 1, "iid": 1, "rqid_lo": 23, "rqid_hi": 7, "cid": 1}, "payload": [], "time": "2023-12-03 1:54:47 AM"},
443:{"ctrl": {"type": 64, "len": 0, "pad": 0, "seq": 238}}, {"ctrl": {"type": 128, "len": 10, "pad": 0, "seq": 108}, "cmd": {"type": 128, "tc": 5, "sid": 1, "tid": 0, "iid": 1, "rqid_lo": 23, "rqid_hi": 7, "cid": 1}, "payload": [73, 10], "time": "2023-12-03 1:54:47 AM"},
444:{"ctrl": {"type": 64, "len": 0, "pad": 0, "seq": 108}}, {"ctrl": {"type": 128, "len": 12, "pad": 0, "seq": 239}, "cmd": {"type": 128, "tc": 5, "sid": 0, "tid": 1, "iid": 1, "rqid_lo": 24, "rqid_hi": 7, "cid": 8}, "payload": [109, 7, 60, 15], "time": "2023-12-03 1:54:47 AM"},
445:{"ctrl": {"type": 64, "len": 0, "pad": 0, "seq": 239}}, {"ctrl": {"type": 128, "len": 9, "pad": 0, "seq": 109}, "cmd": {"type": 128, "tc": 5, "sid": 1, "tid": 0, "iid": 1, "rqid_lo": 24, "rqid_hi": 7, "cid": 8}, "payload": [0], "time": "2023-12-03 1:54:47 AM"},
533:{"ctrl": {"type": 64, "len": 0, "pad": 0, "seq": 138}}, {"ctrl": {"type": 128, "len": 10, "pad": 0, "seq": 15}, "cmd": {"type": 128, "tc": 5, "sid": 0, "tid": 1, "iid": 1, "rqid_lo": 56, "rqid_hi": 7, "cid": 11}, "payload": [210, 11], "time": "2023-12-03 1:55:16 AM"},
538:{"ctrl": {"type": 64, "len": 0, "pad": 0, "seq": 140}}, {"ctrl": {"type": 128, "len": 10, "pad": 0, "seq": 18}, "cmd": {"type": 128, "tc": 5, "sid": 0, "tid": 1, "iid": 1, "rqid_lo": 59, "rqid_hi": 7, "cid": 11}, "payload": [204, 11], "time": "2023-12-03 1:55:17 AM"},
553:{"ctrl": {"type": 64, "len": 0, "pad": 0, "seq": 146}}, {"ctrl": {"type": 128, "len": 10, "pad": 0, "seq": 25}, "cmd": {"type": 128, "tc": 5, "sid": 0, "tid": 1, "iid": 1, "rqid_lo": 66, "rqid_hi": 7, "cid": 11}, "payload": [0, 0], "time": "2023-12-03 1:55:21 AM"},
559:{"ctrl": {"type": 64, "len": 0, "pad": 0, "seq": 148}}, {"ctrl": {"type": 128, "len": 10, "pad": 0, "seq": 28}, "cmd": {"type": 128, "tc": 5, "sid": 0, "tid": 1, "iid": 1, "rqid_lo": 69, "rqid_hi": 7, "cid": 11}, "payload": [0, 0], "time": "2023-12-03 1:55:25 AM"},
```
