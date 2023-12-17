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
        "fan": retrieve_series(readings, ["fan_rpm"]),
        "pci1": retrieve_series(readings, ["nvme-pci-0200", "Composite", "temp1_input"]),
        "pci2": retrieve_series(readings, ["nvme-pci-0200", "Sensor 1", "temp2_input"]),
        "wifi": retrieve_series(readings, ["iwlwifi_1-virtual-0", "temp1", "temp1_input"]),
        "package0": retrieve_series(readings, ["coretemp-isa-0000", "Package id 0", "temp1_input"]),
        "core0": retrieve_series(readings, ["coretemp-isa-0000", "Core 0", "temp2_input"]),
        "t": t,
    }

    return values

def make_plot(values, title, vbar=None, cutoff=None):
    t = values["t"]
    t0 = t[0]
    
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
    if cutoff:
        ax2.plot(cutoff[0], cutoff[1], color="black", label="cutoff", marker="x")
    ax2.tick_params(axis='y')
    ax2.legend(loc="lower right")
    ax2.set_ylim([0, 8000])
    fig.tight_layout()

    fig.suptitle(title, fontsize=10)

    values["t"] = t
    return fig, values


def make_rpm_plot(entries, title):

    
    fig, ax1 = plt.subplots(figsize=[16, 9])

    ax1.set_xlabel('time (s), x denotes `stress -c 12` cutoff')
    ax1.set_ylabel('fan (rpm)')

    for name, entry in entries.items():
        for t0, fan_value in zip( entry["values"]["t"], entry["values"]["fan"]):
            if fan_value != 0:
                break

        ax1.plot([t - t0 for t in entry["values"]["t"]], entry["values"]["fan"], label=name, color=entry["color"])
        ax1.plot(entry["cutoff"][0] - t0, entry["cutoff"][1], marker="x", color=entry["color"])

    ax1.tick_params(axis='y')
    ax1.set_ylim([0, 8000])
    ax1.set_xlim([-100, 900])
    ax1.legend(loc="upper right")

    fig.tight_layout()

    fig.suptitle(title, fontsize=13, y=0.95)

    return fig

def get_last_rpm(fname):
    values = load_values(fname)
    t = values["t"][-1]
    rpm = values["fan"][-1]
    return (t, rpm)


if True:
    #/home/ivor/Documents/Code/nixos-surface/sensor_logs/load_with_fan_profiles/power_saver_with_fan_profile.json.gz
    saver_values = load_values("../../sensor_logs/load_with_fan_profiles/power_saver_with_fan_profile.json.gz")
    saver_last = get_last_rpm("../../sensor_logs/load_with_fan_profiles/power_saver_with_fan_profile_first.json.gz")
    saver_f1,saver_values  = make_plot(saver_values, "powersaver", cutoff=saver_last)
    saver_f1.savefig("/tmp/saver.png", figsize=(100, 200))

    balanced_values = load_values("../../sensor_logs/load_with_fan_profiles/balanced_with_fan_profile.json.gz")
    balanced_last = get_last_rpm("../../sensor_logs/load_with_fan_profiles/balanced_with_fan_profile_first.json.gz")
    balanced_fig, balanced_values = make_plot(balanced_values, "balanced", cutoff=balanced_last)
    balanced_fig.savefig("/tmp/balanced.png", figsize=(100, 200))

    performance_values = load_values("../../sensor_logs/load_with_fan_profiles/performance_with_fan_profile.json.gz")
    performance_last = get_last_rpm("../../sensor_logs/load_with_fan_profiles/performance_with_fan_profile_first.json.gz")
    performance_fig, performance_values = make_plot(performance_values, "performance", cutoff=performance_last)
    performance_fig.savefig("/tmp/performance.png", figsize=(100, 200))

    normal_values = load_values("../../sensor_logs/load_with_fan_profiles/balanced_performance_with_fan_profile.json.gz")
    normal_last = get_last_rpm("../../sensor_logs/load_with_fan_profiles/balanced_performance_with_fan_profile_first.json.gz")
    normal_fig, normal_values = make_plot(normal_values, "normal", cutoff=normal_last)
    normal_fig.savefig("/tmp/normal.png", figsize=(100, 200))

    z = {
        "low power/power saver": {"values": saver_values, "cutoff":saver_last, "color": "green"},
        "balanced": {"values": balanced_values, "cutoff":balanced_last, "color": "blue"},
        "balanced-performance/normal": {"values": normal_values, "cutoff":normal_last, "color":"orange"},
        "performance": {"values": performance_values, "cutoff":performance_last, "color": "red"},
    }
    fig = make_rpm_plot(z, title="fan profile comparison")
    fig.savefig("/tmp/comparison.png", figsize=(100, 200))
    fig.show()
    plt.show()
    # plt.show()
