#!/usr/bin/env python3

import gzip
from matplotlib import pyplot as plt
import numpy as np
import sys
import json


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

def make_plot(path, title, vbar=None):

    d = load(path)

    t0 = d[0][0]
    t = [a[0] - t0 for a in d]

    readings = [a[1] for a in d]

    print(d[0][1])

    values = {
        "fan": retrieve_series(readings, ["fan-virtual-0", "fan1", "fan1_input"]),
        "pci1": retrieve_series(readings, ["nvme-pci-0200", "Composite", "temp1_input"]),
        "pci2": retrieve_series(readings, ["nvme-pci-0200", "Sensor 1", "temp2_input"]),
        "wifi": retrieve_series(readings, ["iwlwifi_1-virtual-0", "temp1", "temp1_input"]),
        "package0": retrieve_series(readings, ["coretemp-isa-0000", "Package id 0", "temp1_input"]),
        "core0": retrieve_series(readings, ["coretemp-isa-0000", "Core 0", "temp2_input"]),
    }


    fig, ax1 = plt.subplots(figsize=[16, 9])

    ax1.set_xlabel('time (s)')
    ax1.set_ylabel('temperature (C)')
    ax1.plot(t, values["pci1"], label="pci1")
    ax1.plot(t, values["wifi"], label="wifi")
    ax1.plot(t, values["package0"], label="package0")
    # ax1.plot(t, values["core0"], label="core0")
    ax1.tick_params(axis='y')
    ax1.set_ylim([20, 95])

    if vbar:
        ax1.vlines(x = vbar - t0, ymin = 0, ymax = 100,
                   colors = 'purple',
                   label = 'Abort `stress -c 12`')
    ax1.legend(loc="upper right")

    ax1.set_xlim([0, 1800])

    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
    ax2.set_ylabel('rpm')
    ax2.plot(t, values["fan"], color="black", label="rpm")
    ax2.tick_params(axis='y')
    ax2.legend(loc="lower right")
    fig.tight_layout()

    fig.suptitle(title, fontsize=10)

    values["t"] = t
    return fig, values

if True:
    f1, f1_values = make_plot("../../sensor_logs/platform_profile_performance_fan_normal_2023_12_10__14_30.json.gz", "fan normal", vbar=1702237369)
    f1.savefig("/tmp/normal.svg", figsize=(100, 200))
    f2, f2_values = make_plot("../../sensor_logs/sensors_log_platform_profile_performance_fan_best_2023_12_10__13_33.json.gz", "fan best", vbar=1702233740)
    f2.savefig("/tmp/best.svg", figsize=(100, 200))

    fig, ax = plt.subplots(figsize=[16,9])
    ax.plot(f1_values["t"], f1_values["fan"], label="normal")
    ax.plot(f2_values["t"], f2_values["fan"], label="best")
    ax.legend()
    fig.tight_layout()
    fig.savefig("/tmp/fans.svg", figsize=(100, 200))

