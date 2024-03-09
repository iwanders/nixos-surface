# Thermald configuration for surface pro 9

## Documentation

https://www.kernel.org/doc/html/next/power/powercap/powercap.html

## The SP9:
```
.
├── intel-rapl -> ../../devices/virtual/powercap/intel-rapl
├── intel-rapl:0 -> ../../devices/virtual/powercap/intel-rapl/intel-rapl:0
├── intel-rapl:0:0 -> ../../devices/virtual/powercap/intel-rapl/intel-rapl:0/intel-rapl:0:0
├── intel-rapl:0:1 -> ../../devices/virtual/powercap/intel-rapl/intel-rapl:0/intel-rapl:0:1
└── intel-rapl:1 -> ../../devices/virtual/powercap/intel-rapl/intel-rapl:1
```

Names:
 - `intel-rapl:0`: `package-0`
   - `intel-rapl:0:0`: `core`
   - `intel-rapl:0:0`: `uncore`
 - `intel-rapl:1`: `psys`

Uncore may be the gpu, psys is the entire soc.

`rapl-read` is useful.


## Thermald configuration



```
Mar 03 15:31:52 papyrus thermald[24232]: [1709497912][INFO]--adaptive option failed on this platform
Mar 03 15:31:52 papyrus thermald[24232]: [1709497912][INFO]Ignoring --adaptive option
```

Adaptive is clearly a no-go.

We need something handwritten, we can likely piggyback on `iwlwifi_1`'s sensor for now and use that as a proxy for the case temperature.

```
Mar 03 16:30:39 papyrus thermald[24306]: [1709501439][DEBUG]Sensor iwlwifi_1 :temp 31000
Mar 03 16:30:39 papyrus thermald[24306]: [1709501439][DEBUG]pref 0 type 3 temp 31000 trip 35000
Mar 03 16:30:39 papyrus thermald[24306]: [1709501439][DEBUG]Passive Trip point applicable
Mar 03 16:30:39 papyrus thermald[24306]: [1709501439][DEBUG]Trip point applicable <  0:35000
Mar 03 16:30:39 papyrus thermald[24306]: [1709501439][DEBUG]cdev size for this trippoint 1
Mar 03 16:30:39 papyrus thermald[24306]: [1709501439][DEBUG]cdev at index 15:rapl_controller
Mar 03 16:30:39 papyrus thermald[24306]: [1709501439][DEBUG]Need to switch to next cdev
```

Well, that's odd... it states `iwlwifi_1` is at `31000` and then the trip point is applicable? The [source code](https://github.com/intel/thermal_daemon/blob/9ac497badd88d9a31b0dfde98d8a9054a4087008/src/thd_trip_point.cpp#L234-L242) is confusing to me, we have both an `off` and an `on` boolean... The cooling device is clearly active, as seen from `Need to switch to next cdev`.


With `PPCC` config specified it definitely does something. It throttles everything tremendously.

