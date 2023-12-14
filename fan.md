# Surface fan

Some notes from trying to figure out how to keep the thing cool(er).

Lots of analysis on https://github.com/linux-surface/kernel/pull/144

Windows does NOT command the fan directly, it does switch the fan profile when the platform profile is switched. This does affect the fan's rotation speed.

## Current understanding

Windows appears to command the fan directly, not purely relying on the system controllers. Overheat tablet on linux -> switch to windows makes the fan go faster. Likely that it uses the `override` profile, but so far it is unknown how to switch to that.

Current platform profile switching does not send the appropriate fan profile switches, but manually doing so appears to do nothing.

Now, we need a kernel module that ties the acpi fan stuff to these commands. [fan_core](https://github.com/torvalds/linux/blob/18d46e76d7c2eedd8577fae67e3f1d4db25018b0/drivers/acpi/fan_core.c), the [surface platform_profile.c](https://github.com/linux-surface/kernel/blob/v6.5-surface-devel/drivers/platform/surface/surface_platform_profile.c) surface module seems to tie `platform_profile` to the `ssam` module, can probably follow that structure.


## Notes on sniffing;
Surface aggregator module; https://github.com/linux-surface/surface-aggregator-module/issues/64

Maybe we can sniff it with [irpmon](https://github.com/linux-surface/surface-aggregator-module/wiki/Development)?

```
sudo modprobe surface_aggregator_cdev
```


# Command analysis

### CID 0
```
# /home/ivor/.nix-profile/bin/python ./ctrl.py request 5 1 0 1 1
TimeoutError: [Errno 110] ETIMEDOUT
```

### CID 1 Fan speed
```
# /home/ivor/.nix-profile/bin/python ./ctrl.py request 5 1 1 1 1
32 11

```

Return two bytes, zero when fan is off, increased as fan sped up, decreases as fan speeds down.
```
sudo python3 ctrl.py request 5 1 1 1 1
[lower byte] [upper byte]
```


### CID 2

```
# /home/ivor/.nix-profile/bin/python ./ctrl.py request 5 1 2 1 1
 00 00 00 40 00 00 00 3f cd cc 4c 3e 14 64
| 2.0 f32  | 0.5 f32    | 0.2 f32   |
# unmodified after reboot.
```

### CID 3
```
# /home/ivor/.nix-profile/bin/python ./ctrl.py request 5 1 3 1 1
01

```

### CID 4 & 5, Quiet and Override profile
```
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
```

### CID 6 Coefficients?
```
# /home/ivor/.nix-profile/bin/python ./ctrl.py request 5 1 6 1 1
33 33 ff ff b8 0b f8 2a ff 3f f4 01 64 00 85 ab 35 43 cd 9c 12 c4 00 00 00 00
           |3000u|11e3u|                 |181.67 f32 |-586.45 f32| 
```

```python
import matplotlib.pyplot as plt
import numpy as np

xpoints = np.arange(0.0, 80.0, 0.1)
#            |3000u|11e3u|                 |181.67 f32 |-586.45 f32| 

ypoints = xpoints * 181.67 - 586.45
lower_bound = np.ones(xpoints.size) * 3000
upper_bound = np.ones(xpoints.size) * 11000
plt.plot(xpoints, ypoints)
plt.plot(xpoints, lower_bound)
plt.plot(xpoints, upper_bound)
plt.xlabel("temperature C");
plt.ylabel("Rpm (T * 181.67 - 586.45) ");
plt.show()
```
crosses 3000 at 20 deg, 8000 at 47'ish...


Could be lower threshold (3000), upper threshold (11e3=11000), followed by fan coefficient. Can't figure out how to set this though.

Tried;
```
/home/ivor/.nix-profile/bin/python ./ctrl.py request 5 1 6 1 1 0x33 0x33 0xff 0xff 0xb9 0x0b 0xf8 0x2a 0xff 0x3f 0xf4 0x01 0x64 0x00 0x85 0xab 0x35 0x43 0xcd 0x9c 0x12 0xc4 0x00 0x00 0x00 0x00
```

But the b8 didn't change into a b9.


### CID 7
```
# /home/ivor/.nix-profile/bin/python ./ctrl.py request 5 1 7 1 1
01 00 00 00 09 00 00 00 00 00 00 00 00 00 00 00 32 00 00 00 4a 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00

# After restarting windows;
# /home/ivor/.nix-profile/bin/python ./ctrl.py request 5 1 7 1 1
01 00 00 00 09 00 00 00 ef 04 00 00 90 00 00 00 d1 00 00 00 f3 00 00 00 05 00 00 00 05 00 00 00 32 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
```


### CID 8, 9

Clearly a getter / setter pair, no idea what it sets though, setting it doesn't seem to affect the fan operation from linux.

```
# /home/ivor/.nix-profile/bin/python ./ctrl.py request 5 1 8 1 1
00

CID 8 sets CID 9 values;
/home/ivor/.nix-profile/bin/python ./ctrl.py request 5 1 8 1 1 0x05 0x10 0xcc 0x10
/home/ivor/.nix-profile/bin/python ./ctrl.py request 5 1 9 1 1
05 10 cc 10


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
It is not set by command 11, 

```

With the bootlog we get:
```
{"ctrl": {"type": 64, "len": 0, "pad": 0, "seq": 30}}, {"ctrl": {"type": 128, "len": 12, "pad": 0, "seq": 2}, "cmd": {"type": 128, "tc": 5, "sid": 0, "tid": 1, "iid": 1, "rqid_lo": 43, "rqid_hi": 0, "cid": 8}, "payload": [0, 0, 0, 0], "time": "2023-12-08 12:16:08 AM"},
{"ctrl": {"type": 64, "len": 0, "pad": 0, "seq": 2}}, {"ctrl": {"type": 128, "len": 9, "pad": 0, "seq": 31}, "cmd": {"type": 128, "tc": 5, "sid": 1, "tid": 0, "iid": 1, "rqid_lo": 43, "rqid_hi": 0, "cid": 8}, "payload": [0], "time": "2023-12-08 12:16:08 AM"},
{"ctrl": {"type": 64, "len": 0, "pad": 0, "seq": 36}}, {"ctrl": {"type": 128, "len": 8, "pad": 0, "seq": 8}, "cmd": {"type": 128, "tc": 5, "sid": 0, "tid": 1, "iid": 1, "rqid_lo": 49, "rqid_hi": 0, "cid": 1}, "payload": [], "time": "2023-12-08 12:16:08 AM"},
{"ctrl": {"type": 64, "len": 0, "pad": 0, "seq": 8}}, {"ctrl": {"type": 128, "len": 10, "pad": 0, "seq": 37}, "cmd": {"type": 128, "tc": 5, "sid": 1, "tid": 0, "iid": 1, "rqid_lo": 49, "rqid_hi": 0, "cid": 1}, "payload": [0, 0], "time": "2023-12-08 12:16:08 AM"},
{"ctrl": {"type": 64, "len": 0, "pad": 0, "seq": 40}}, {"ctrl": {"type": 128, "len": 12, "pad": 0, "seq": 12}, "cmd": {"type": 128, "tc": 5, "sid": 0, "tid": 1, "iid": 1, "rqid_lo": 53, "rqid_hi": 0, "cid": 8}, "payload": [0, 0, 1, 0], "time": "2023-12-08 12:16:08 AM"},
{"ctrl": {"type": 64, "len": 0, "pad": 0, "seq": 13}}, {"ctrl": {"type": 128, "len": 9, "pad": 0, "seq": 42}, "cmd": {"type": 128, "tc": 5, "sid": 1, "tid": 0, "iid": 1, "rqid_lo": 53, "rqid_hi": 0, "cid": 8}, "payload": [0], "time": "2023-12-08 12:16:08 AM"},
```


### CID 10

```
# /home/ivor/.nix-profile/bin/python ./ctrl.py request 5 1 10 1 1
TimeoutError: [Errno 110] ETIMEDOUT
```


### CID 11 Override fan speed
This is the only command found so far that actually sets the speed, but the way
it is set means it is overwritten by controller as soon as the temperature
reaches approximately 40 degrees.
```
# /home/ivor/.nix-profile/bin/python ./ctrl.py request 5 1 11 1 1
TimeoutError: [Errno 110] ETIMEDOUT
```

And fan speed control, last two bytes here:
```
sudo python3 ctrl.py request 5 1 11 1 0 185 20
sudo python3 ctrl.py request 5 1 11 1 0 0 0
```


Seems to only really be used to provide an indication to the firmware, even in Windows this is never seen above 4500.

## Cid 14 platform profile
Sniff with irpmon with platform switches;

This is likely the fan profile, as it goes out with the platform profile change, ~but it doesn't affect fan speed.~ Does affect fan speed.

```
{"ctrl": {"type": 64, "len": 0, "pad": 0, "seq": 124}}, {"ctrl": {"type": 128, "len": 12, "pad": 0, "seq": 12}, "cmd": {"type": 128, "tc": 3, "sid": 0, "tid": 1, "iid": 0, "rqid_lo": 53, "rqid_hi": 7, "cid": 3}, "payload": [3, 0, 0, 0], "time": "2023-12-03 12:42:53 AM"}, 
{"ctrl": {"type": 64, "len": 0, "pad": 0, "seq": 13}}, {"ctrl": {"type": 128, "len": 9, "pad": 0, "seq": 14}, "cmd": {"type": 128, "tc": 5, "sid": 0, "tid": 1, "iid": 1, "rqid_lo": 55, "rqid_hi": 7, "cid": 14}, "payload": [3], "time": "2023-12-03 12:42:53 AM"}, 

{"ctrl": {"type": 64, "len": 0, "pad": 0, "seq": 126}}, {"ctrl": {"type": 128, "len": 12, "pad": 0, "seq": 17}, "cmd": {"type": 128, "tc": 3, "sid": 0, "tid": 1, "iid": 0, "rqid_lo": 58, "rqid_hi": 7, "cid": 3}, "payload": [4, 0, 0, 0], "time": "2023-12-03 12:42:58 AM"}, 
{"ctrl": {"type": 64, "len": 0, "pad": 0, "seq": 18}}, {"ctrl": {"type": 128, "len": 9, "pad": 0, "seq": 19}, "cmd": {"type": 128, "tc": 5, "sid": 0, "tid": 1, "iid": 1, "rqid_lo": 60, "rqid_hi": 7, "cid": 14}, "payload": [4], "time": "2023-12-03 12:42:58 AM"}, 

{"ctrl": {"type": 64, "len": 0, "pad": 0, "seq": 130}}, {"ctrl": {"type": 128, "len": 12, "pad": 0, "seq": 24}, "cmd": {"type": 128, "tc": 3, "sid": 0, "tid": 1, "iid": 0, "rqid_lo": 65, "rqid_hi": 7, "cid": 3}, "payload": [1, 0, 0, 0], "time": "2023-12-03 12:43:01 AM"}, 
{"ctrl": {"type": 64, "len": 0, "pad": 0, "seq": 25}}, {"ctrl": {"type": 128, "len": 9, "pad": 0, "seq": 26}, "cmd": {"type": 128, "tc": 5, "sid": 0, "tid": 1, "iid": 1, "rqid_lo": 67, "rqid_hi": 7, "cid": 14}, "payload": [2], "time": "2023-12-03 12:43:01 AM"}, 

```

Shows a fan command going out with a platform change, probably switches the mode? But from the fan dump we know there's just two profiles, Quiet and Override. ~Switching this actively from linux with a hot tablet does not change the fan speeds.~

```
/home/ivor/.nix-profile/bin/python ./ctrl.py request 5 1 14 1 0 0
```

### CID rest
```
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
# /home/ivor/.nix-profile/bin/python ./ctrl.py request 5 1 17 1 1
1d
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
```

## CID 11 being sent;

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



## Some notes on tracing and logging

Dtrace for windows is a thing.

## Logman
`logman` is also a thing; https://learn.microsoft.com/en-us/previous-versions/dynamicsnav-2018-developer/How-to--Use-Logman-to-Collect-Event-Trace-Data

[From here](https://library.netapp.com/ecmdocs/ECMP12404601/html/GUID-6324FD89-DD16-401A-8B2D-933326B4922F.html):

> Enabling boot-time tracing is done by appending "autosession" to the session name:

```
logman create trace "autosession\<session_name>"
```
Doesn't seem to work... 


https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/logman-create-trace

Also tried setting LogPages as per [this page](https://github.com/MicrosoftDocs/windows-driver-docs/blob/staging/windows-driver-docs-pr/wdf/using-wpp-software-tracing-in-kmdf-and-umdf-2-drivers.md)
so;

```
[HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\SurfaceSerialHubDriver\Parameters]
"WppRecorder_TraceGuid"="{fa755ced-72df-44db-95a3-ef1009107e54}"
"LogPages"=dword:00000005
```
But that didn't allow any retrieval of events in WinDbg.

```
logman create trace IW-serial-hub -p Microsoft-Surface-SurfaceSerialHubDriver -o C:\perflogs\IW-serial-hub.etl
```
And then converting with;
```
tracerpt IW-serial-hub_000001.etl -o IW-serial-hub_000001.xml
```

Did yield some things, but not the things of interest (like the data)
```
<Message>Surface Serial Hub Driver get response timeout, TargetID = 2, TargetCategory = REG, TargetCategoryInstance = 0, CommandID = 2, RequestID = 1079. </Message>
```


Maybe on the uart!?... nope, all we get is the length of the data written.
```
logman create trace IW-uart2 -p Intel-iaLPSS2-UART2 -o C:\perflogs\iw-uart2.etl
tracerpt.exe .\iw-uart2_000001.etl -o .\iw-uart2_000001.xml
```

May be able to trace syscalls at boot with something like [this](https://techcommunity.microsoft.com/t5/core-infrastructure-and-security/becoming-an-xperf-xpert-the-slow-boot-case-of-the/ba-p/255634)
```
xbootmgr -trace boot -traceFlags Latency+DISPATCHER -postBootDelay 120 -stackWalk Profile+ProcessCreate+CSwitch+ReadyThread+Mark+SyscallEnter+ThreadCreate
```
That should at least tell us when the relevant drivers come up relative to the others.

From with debugger, [irp stands for IO Request Packet](https://learn.microsoft.com/en-us/windows-hardware/drivers/debuggercmds/-irp), [tracing during boot](https://learn.microsoft.com/en-us/windows-hardware/drivers/devtest/tracing-during-boot)


Performed a trace with:

```
xbootmgr -trace boot -traceFlags Latency+DISPATCHER -postBootDelay 120
```

That shows that `irpmndrv` comes up as driver line 29, at 2.567s. Our target, `iaLPSS2_UART2_ADL` comes up as driver line 57, at 5.5287s. So if we can manage to get the irpmon driver to record the UART from its creation, we should be good. That is probably easier than the other options...



# Logging at boot with irpmon
```
# Ensure driver is set to startup at boot.

# To enable run the following, written logs go to C:\Windows\
irpmonc.exe --input=D:\\.\irpmndrv  --hook-driver=ICD:\Driver\iaLPSS2_UART2_ADL --boot-log=1 --save-settings=1
# Writing happens in chunks, current log may be zero bytes until flushed, or just disable it and reboot.

# To disable
irpmonc.exe --input=D:\\.\irpmndrv  --unhook-driver=\Driver\iaLPSS2_UART2_ADL --boot-log=0 --save-settings=1 
```

