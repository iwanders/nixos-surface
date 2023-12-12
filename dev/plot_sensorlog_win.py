#!/usr/bin/env python3

import gzip
from matplotlib import pyplot as plt
import numpy as np
import sys
import json
import time


def load(d):
    opener = gzip.open if d.endswith("gz") else open
    with opener(d) as f:
        return json.load(f)

def parse_freq(s):
    # print(s)
    lines = [z.strip() for z in s.split("\n")]
    
    # Throw out the first two, header and line
    lines = lines[3:]
    with_time = lines[0]
    lines = lines[1:]
    t, first_cpu_id = with_time.split("\\\\")
    t =  time.mktime(time.strptime(t.strip(), '%Y-%m-%d %I:%M:%S %p'))
    remainder = ["\\\\" + first_cpu_id] + lines
    freqs = {}
    for i in range(int(len(remainder) / 3)):
        name = remainder[i * 3]
        if not name:
            break
        clock = int(remainder[i * 3+1])
        name = name.replace("\\\\papyrus\\processor information(", "").replace(")\\processor frequency", "")
        freqs[name] = clock
    res =  (t, freqs)
    # print(res)
    return res

def parse_temp(s):
    # First, split on __GENUS, all records have this.
    zones = s.split("__GENUS")
    temperatures = {}
    for z in zones:
        name = None
        temperature = None
        for l in z.split("\n"):
            if l.startswith("InstanceName"):
                name = l.split(": ")[1]
            if l.startswith("CurrentTemperature"):
                temperature = int(l.split(": ")[1])
        if name and temperature is not None:
            temperatures[name] = temperature
    print(temperatures)
    return temperatures

def process_windows_log(raw_json):
    clean = []
    for t, freq, temp in raw_json:
        freq = parse_freq(freq)
        temp = parse_temp(temp)
        clean.append((t, freq, temp))
    return clean

if __name__ == "__main__":
    #entries = load("../../sensor_logs/windows/load_perfmode_ac_15mins_load_stop_load_with_sensors.json.gz")
    #entries = process_windows_log(entries)

    
    