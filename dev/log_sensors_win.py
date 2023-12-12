#!/usr/bin/env python3


import argparse
import subprocess
import time
import os
import json

#load_perfmode_ac_15mins_load_stop_load_with_sensors

def powershell(cmdline):
    as_arg = cmdline
    res = subprocess.run(["powershell", "-Command", as_arg], stdout=subprocess.PIPE)
    if res.returncode == 0:
        return res.stdout.decode("ascii")
    return None

def get_cpu_freq_win():
    return powershell('Get-Counter -Counter "\\Processor Information(*)\\Processor Frequency"')

def get_temperatures_win():
    return powershell('Get-WmiObject MSAcpi_ThermalZoneTemperature -Namespace "root/wmi"')    

def capture(sensors_bin):
    freqs = get_cpu_freq_win();
    temps = get_temperatures_win();
    t = time.time()
    return (t, freqs, temps)

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
    if os.path.exists(p):
        os.unlink(p)
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
        print(".")
        # Write to temp file and rename, to ensure atomic operation such that
        # we can't truncate the file and cancel during the write.
        write_tmp_json(records, args.output)
        rename_tmp_to_real(args.output)