#!/usr/bin/env python3

import argparse
import subprocess
import time
import os
import json

"""
From cycle_through_power_profiles.json

2023-12-03 12:42:53 AM   Seq OUT TMP:03 t01 i00 c 0x03 (  4): 03 00 00 00
2023-12-03 12:42:53 AM   Seq OUT BKL:17 t02 i01 c 0x01 (  1): 00
2023-12-03 12:42:53 AM   Seq OUT FAN:05 t01 i01 c 0x0e (  1): 03
2023-12-03 12:42:53 AM   Seq OUT SAM:01 t01 i00 c 0x33 (  0): [] => 00
2023-12-03 12:42:58 AM   Seq OUT SAM:01 t01 i00 c 0x34 (  0): [] => 00


2023-12-03 12:42:58 AM   Seq OUT TMP:03 t01 i00 c 0x03 (  4): 04 00 00 00
2023-12-03 12:42:58 AM   Seq OUT BKL:17 t02 i01 c 0x01 (  1): 00
2023-12-03 12:42:58 AM   Seq OUT FAN:05 t01 i01 c 0x0e (  1): 04
2023-12-03 12:42:58 AM   Seq OUT SAM:01 t01 i00 c 0x33 (  0): [] => 00
2023-12-03 12:42:58 AM   Seq OUT SAM:01 t01 i00 c 0x34 (  0): [] => 00


2023-12-03 12:43:01 AM   Seq OUT TMP:03 t01 i00 c 0x03 (  4): 01 00 00 00
2023-12-03 12:43:01 AM   Seq OUT BKL:17 t02 i01 c 0x01 (  1): 00
2023-12-03 12:43:01 AM   Seq OUT FAN:05 t01 i01 c 0x0e (  1): 02
2023-12-03 12:43:01 AM   Seq OUT SAM:01 t01 i00 c 0x33 (  0): [] => 00
2023-12-03 12:43:05 AM   Seq OUT SAM:01 t01 i00 c 0x34 (  0): [] => 00

# from the platform profile module;
enum ssam_tmp_profile {
	SSAM_TMP_PROFILE_NORMAL             = 1,
	SSAM_TMP_PROFILE_BATTERY_SAVER      = 2,
	SSAM_TMP_PROFILE_BETTER_PERFORMANCE = 3,
	SSAM_TMP_PROFILE_BEST_PERFORMANCE   = 4,
};

So the mapping becomes

performance profile -> fan profile
better performance, 3 -> 3
best performance, 4 -> 4
normal, 1 -> 2



# Keeping the main platform profile at performance for now.

```
best fan profile:
/home/ivor/.nix-profile/bin/python ./ctrl.py request 5 1 14 1 0 4

normal fan profile
/home/ivor/.nix-profile/bin/python ./ctrl.py request 5 1 14 1 0 2

better fan profile
/home/ivor/.nix-profile/bin/python ./ctrl.py request 5 1 14 1 0 3
```

Testing methodology:
    Environment:
        Room temperature
        Surface at 45 degrees on kickstand.
        Keyboard attached
        Power attached

    - Ensure 'fresh' state, reboot.
    - Switch platform to 'performance' in gnome.
    - Start logging, immediately followed by `stress -c 12`.


2023_platform_profile_performance_fan_best_2023_12_10__13_33.json:
/home/ivor/.nix-profile/bin/python ./ctrl.py request 5 1 14 1 0 4
At certain moment in, after it appeared to be at steady state
    fan jumped from 6000 to max, maxing out at 7334, dropped to 6000
    Definitely appears to have found steady state.
    Cancelling stress at 1702233740.




Noticed that the platform profile to performance doesn't switch the CPU governor
to performance, from `cpufreq-info`... or thermald did this?
    analyzing CPU 11:
      driver: intel_pstate
      CPUs which run at the same hardware frequency: 11
      CPUs which need to have their frequency coordinated by software: 11
      maximum transition latency: 4294.55 ms.
      hardware limits: 400 MHz - 3.50 GHz
      available cpufreq governors: performance, powersave
      current policy: frequency should be within 400 MHz and 3.50 GHz.
                      The governor "powersave" may decide which speed to use
                      within this range.
      current CPU frequency is 2.90 GHz.


"""

def get_sensors(sensors_bin):
    # nixos 23.11's sensors supports json output!
    res = subprocess.run([sensors_bin, "-j"], stdout=subprocess.PIPE)
    if res.returncode == 0:
        return json.loads(res.stdout)

def capture(sensors_bin):
    sensors = get_sensors(sensors_bin)
    t = time.time()
    return (t, sensors)

def load_current(p):
    if not os.path.isfile(p):
        return []

    with open(p) as f:
        return json.load(f)

def write_tmp_json(records, p):
    with open(p + ".tmp", "w") as f:
        json.dump(records, f)
    
def rename_tmp_to_real(p):
    # rename is atomic, so even ctrl+c can't corrupt data here.
    os.rename(p +".tmp", p)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--delay", type=float, default=1.0, help="period between records")
    parser.add_argument("--sensors-path", default="sensors", help="binary to sensors")
    parser.add_argument("output", help="The path to write to.")
    args = parser.parse_args()

    while True:
        new_record = capture(args.sensors_path)
        records = load_current(args.output)
        time.sleep(args.delay)
        records.append(new_record)
        # Write to temp file and rename, to ensure atomic operation such that
        # we can't truncate the file and cancel during the write.
        write_tmp_json(records, args.output)
        rename_tmp_to_real(args.output)
