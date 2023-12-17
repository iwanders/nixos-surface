#!/usr/bin/env python3

import gzip
from matplotlib import pyplot as plt
import numpy as np
import sys
import json
from plot_sensorlog_win import make_series


def load(d):
    opener = gzip.open if d.endswith("gz") else open
    with opener(d) as f:
        return json.load(f)

def retrieve_series(d, key):
    def ret(v, a):
        for k in key:
            v = v[k]
        return v
    return [ret(v, key) for v in d]

def load_values(path):
    d = load(path)

    t0 = d[0][0]
    t = [a[0] - t0 for a in d]

    readings = [a[1] for a in d]

    values = {
        "fan_rpm": retrieve_series(readings, ["fan_rpm"]),
        "pci1": retrieve_series(readings, ["nvme-pci-0200", "Composite", "temp1_input"]),
        "pci2": retrieve_series(readings, ["nvme-pci-0200", "Sensor 1", "temp2_input"]),
        "wifi": retrieve_series(readings, ["iwlwifi_1-virtual-0", "temp1", "temp1_input"]),
        "package0": retrieve_series(readings, ["coretemp-isa-0000", "Package id 0", "temp1_input"]),
        "core0": retrieve_series(readings, ["coretemp-isa-0000", "Core 0", "temp2_input"]),
        "t": t,
    }

    def t_shifter(t):
        # Salvage recorded value.
        r = int(t * 100.0)
        print(r)

        offset = -273.15
        res = 0.1
        r = r * res + offset
        return r

    # print(readings)
    for i in range(1, 11):
        values[f"temp_{i}"] = retrieve_series(readings, ["ssam_thermal-virtual-0", f"temp{i}", f"temp{i}_input"])
        values[f"temp_{i}"] = [t_shifter(t) for t in values[f"temp_{i}"]]

    # values["usr%"] = retrieve_series(readings, ["system_load", "us"]),

    return values

def make_plot(values, title):

    t0 = values["t"][0]
    tshifted = [t - t0 for t in values["t"]]
    fig, ax1 = plt.subplots(figsize=[16, 9])

    ax1.set_xlabel('time (s)')
    ax1.set_ylabel('sensosr')

    for i in range(1, 11):
        name = f"temp_{i}"
        # print(values[name])
        ax1.plot(tshifted, values[name], label=name)


    for name in ("wifi", "pci1", "pci2"):
        ax1.plot(tshifted, values[name], label=name, linewidth=1, linestyle=":")
    ax1.tick_params(axis='y')
    # ax1.set_ylim([0, 100])
    # ax1.set_xlim([-100, 900])
    ax1.legend(loc="upper right")


    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
    ax2.set_ylabel('rpm')
    # ax2.plot(t, values["fan"], color="black", label="rpm")
    ax2.plot(tshifted, values["fan_rpm"], label="fan", color="black")
    ax2.tick_params(axis='y')
    ax2.legend(loc="lower right")
    ax2.set_ylim([0, 8000])
    fig.tight_layout()


    fig.tight_layout()

    fig.suptitle(title, fontsize=13, y=0.95)

    return fig



if True:
    #/home/ivor/Documents/Code/nixos-surface/sensor_logs/load_with_fan_profiles/power_saver_with_fan_profile.json.gz
    values = load_values("../../sensor_logs/thermal_hub_with_speed_load_stress.json.gz")
    saver_f1 = make_plot(values, "thermals")
    saver_f1.savefig("/tmp/thermals.png", figsize=(100, 200))
    plt.show()
