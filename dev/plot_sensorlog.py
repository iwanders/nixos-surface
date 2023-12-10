#!/usr/bin/env python3

import gzip
from matplotlib import pyplot as plt
import numpy as np
import sys
import json


def load(d):
    with gzip.open(d) as f:
        return json.load(f)

def retrieve_series(d, key):
    def ret(v, a):
        for k in key:
            v = v[k]
        return v
    return [ret(v, key) for v in d]

d = load(sys.argv[1])

t = [a[0] - d[0][0] for a in d]

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



fig, ax1 = plt.subplots()


ax1.set_xlabel('time (s)')
ax1.set_ylabel('temperature (C)')
ax1.plot(t, values["pci1"], label="pci1")
ax1.plot(t, values["wifi"], label="wifi")
ax1.plot(t, values["package0"], label="package0")
# ax1.plot(t, values["core0"], label="core0")
ax1.tick_params(axis='y')
ax1.legend(loc="upper right")
ax1.set_ylim([20, 90])

ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

# color = 'tab:blue'
ax2.set_ylabel('rpm')
ax2.plot(t, values["fan"], color="black", label="rpm")
ax2.tick_params(axis='y')
ax2.legend(loc="lower right")
fig.tight_layout()  # otherwise the right y-label is slightly clipped
plt.show()
