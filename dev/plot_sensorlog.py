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
        "fan": retrieve_series(readings, ["fan-virtual-0", "fan1", "fan1_input"]),
        "pci1": retrieve_series(readings, ["nvme-pci-0200", "Composite", "temp1_input"]),
        "pci2": retrieve_series(readings, ["nvme-pci-0200", "Sensor 1", "temp2_input"]),
        "wifi": retrieve_series(readings, ["iwlwifi_1-virtual-0", "temp1", "temp1_input"]),
        "package0": retrieve_series(readings, ["coretemp-isa-0000", "Package id 0", "temp1_input"]),
        "core0": retrieve_series(readings, ["coretemp-isa-0000", "Core 0", "temp2_input"]),
        "t": t,
    }

    return values

def make_plot(values, title, vbar=None):
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
    ax2.tick_params(axis='y')
    ax2.legend(loc="lower right")
    ax2.set_ylim([0, 8000])
    fig.tight_layout()

    fig.suptitle(title, fontsize=10)

    values["t"] = t
    return fig, values


def make_temperature_plot(values):




if False:
    f1_values = load_values("../../sensor_logs/platform_profile_performance_fan_normal_2023_12_10__14_30.json.gz")
    f1,f1_values  = make_plot(f1_values, "fan normal", vbar=1702237369)
    f1.savefig("/tmp/normal.svg", figsize=(100, 200))
    f2_values = load_values("../../sensor_logs/sensors_log_platform_profile_performance_fan_best_2023_12_10__13_33.json.gz")
    f2, f2_values = make_plot(f2_values, "fan best", vbar=1702233740)
    f2.savefig("/tmp/best.svg", figsize=(100, 200))

if True:
    f1_values = load_values("../../sensor_logs/platform_profile_performance_fan_normal_2023_12_10__14_30.json.gz")
    f2_values = load_values("../../sensor_logs/sensors_log_platform_profile_performance_fan_best_2023_12_10__13_33.json.gz")
    fig, ax = plt.subplots(figsize=[16,9])
    ax.plot(f1_values["t"], f1_values["fan"], label="linux_normal", linewidth=0.4)
    ax.plot(f2_values["t"], f2_values["fan"], label="linux_best", linewidth=0.4)

    win_battery = make_series(load("../../irp_logs/load_perfmode_battery_10min_perfmode_ac_10min_noload_15min.interpet.json"))
    win_ac_15min = make_series(load("../../irp_logs/load_perfmode_ac_15mins_load_stop_load_with_sensors.interpret.json"))
    win_ac_15min_2nd = make_series(load("../../irp_logs/load_perfmode_ac_15mins_load_start_at_profile_stop_at_1702422833_utc_time_is_EST.interpret.json.gz"))

    def plot_series(ax, data, series, name, factor=1.0, shift=0.0,  *args, **kwargs):
        if not series in data:
            return
        t0 = data[series][0][0]
        this_t = [a[0] - t0 + shift for a in data[series]]
        this_v = [a[1] * factor for a in data[series]]
        ax.plot(this_t, this_v, *args, label=name, **kwargs)


    plot_series(ax, win_battery, series="tc_5_cid_1_iid_1_resp_rpm", name="win_battery_then_ac", marker="+", shift=-545.0) 
    plot_series(ax, win_ac_15min, series="tc_5_cid_1_iid_1_resp_rpm", name="win_ac_15min", marker="+", shift=77.0) 
    plot_series(ax, win_ac_15min_2nd, series="tc_5_cid_1_iid_1_resp_rpm", name="win_ac_15min_2nd", marker="o", shift=77.0) 

    fig.suptitle("fans from tc_5_cid_1_iid_1_resp_rpm", fontsize=20, y=0.95)
    ax.legend()
    ax.set_ylim([0, 8000])
    ax.set_xlim([0, 1800])
    ax.set_ylabel('rpm')
    fig.tight_layout()
    fig.savefig("/tmp/fans.svg", figsize=(100, 200))
    plt.show()

