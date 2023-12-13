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


def make_plot(series):
    t0 = series[list(series.keys())[0]][0][0]

    def plot_series(ax, name, factor=1.0,  *args, **kwargs):
        if not name in series:
            return
        this_t = [a[0] - t0 for a in series[name]][1:-1]
        this_v = [a[1] * factor for a in series[name]][1:-1]
        ax.plot(this_t, this_v, *args, label=name, **kwargs)

    fig, ax1 = plt.subplots(figsize=[16, 9])

    ax1.set_xlabel('time (s)')
    ax1.set_ylabel('temperature (??)')


    plot_series(ax1, "tc_3_cid_1_iid_9_resp_temp")
    plot_series(ax1, "tc_3_cid_1_iid_5_resp_temp")
    # plot_series(ax1, "tc_3_cid_1_iid_2_resp_temp")

    ax1.tick_params(axis='y')

    ax1.legend(loc="upper right")

    ax1.set_xlim([0, 1800])

    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
    ax2.set_ylabel('rpm')
    plot_series(ax2, "tc_5_cid_1_iid_1_resp_rpm", color="black", marker="+")

    plot_series(ax2, "tc_5_cid_11_iid_1_req_rpm", color="magenta", marker="x", linestyle='none')

    plot_series(ax2, "tc_5_cid_8_iid_1_req_c8_lo", color="red", marker="*", linestyle='none')
    plot_series(ax2, "tc_5_cid_8_iid_1_req_c8_hi", color="green", marker="o", linestyle='none')
    ax2.tick_params(axis='y')
    ax2.legend(loc="lower right")
    ax2.set_ylim([0, 8000])
    fig.tight_layout()

    return fig


def make_series(z):
    series = {}
    for e in z:
        t = e["t"]
        src_token = f"tc_{e['tc']}_cid_{e['cid']}_iid_{e['iid']}"
        for (role, rolestr) in (("src", "req"), ("response", "resp")):
            if e[role] is not None:
                for k, v in e[role].items():
                    full_key = src_token + "_" + rolestr + "_" + k
                    if not full_key in series:
                        series[full_key] = []
                    series[full_key].append((t, v))
    return series
        

if __name__ == "__main__":
    #entries = load("../../sensor_logs/windows/load_perfmode_ac_15mins_load_stop_load_with_sensors.json.gz")
    #entries = process_windows_log(entries)

    # irp_entries = load("../../irp_logs/load_perfmode_ac_15mins_load_stop_load_with_sensors.interpret.json")
    # irp_entries = load("../../irp_logs/load_perfmode_ac_15mins_load_start_at_profile_stop_at_1702422833_utc_time_is_EST.interpret.json.gz")
    irp_entries = load("../../irp_logs/load_perfmode_battery_10min_perfmode_ac_10min_noload_15min.interpet.json")
    irp_series = make_series(irp_entries)
    print("\n".join(irp_series.keys()))
    fig = make_plot(irp_series)
    fig.savefig("/tmp/windows_fan.svg", figsize=(100, 200))
    plt.show()
    
    