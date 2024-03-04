# Thermald configuration for surface pro 9

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