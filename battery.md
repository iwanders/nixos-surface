# Battery


## Towards smart charging

It still (after weeks on the charger) hasn't enabled...

### BatteryPropGet

```
PS C:\Users\ivor> sdmc batterypropget 1 1
IsSmartChargingEnabled : False
```

Results in:
```
$ irp_display.py hexdump 2024_02_16_batteryprop_1_1_get.json 
  ??? OUT SAM:01 t01 i00 c 0x34 (  0): []
  ???  IN SAM:01 t00 i00 c 0x34 (  1): 00
  ??? OUT SAM:01 t01 i00 c 0x41 (  0): []
  ???  IN SAM:01 t00 i00 c 0x41 (  2): 00 00
  ??? OUT SAM:01 t01 i00 c 0x42 (  0): []
  ???  IN SAM:01 t00 i00 c 0x42 (  4): 00 00 00 00
  ??? OUT SAM:01 t01 i00 c 0x33 (  0): []
  ???  IN SAM:01 t00 i00 c 0x33 (  1): 00
```

### BIOS Battery Limit

In bios we can enable 50% battery limit. When we do that and run the surface app, the 0x41 and 0x42 become:

```
  ??? OUT SAM:01 t01 i00 c 0x41 (  0): []
  ???  IN SAM:01 t00 i00 c 0x41 (  2): 80 03
  ??? OUT SAM:01 t01 i00 c 0x42 (  0): []
  ???  IN SAM:01 t00 i00 c 0x42 (  4): 00 00 00 00

```

The `80` is suspiciously 128 / 256 (50%?), 03 probably some mode / enum.


## Other bits
This command;

```
PS C:\Users\ivor> sdmc batterypropget GeneralStandard AnythingType
GeneralStandard : [Complex (23 Properties]
BatteryPhysicalDetect   1 (uint)
BatteryStatus           224 (uint)
OperationStatus         4211587 (uint)
ChargingStatus          18448 (uint)
GaugingStatus           596058 (uint)
SafetyStatus            0 (uint)
PfStatus                0 (uint)
RelativeStateOfCharge   99 (uint)
StateOfHealth           100 (uint)
ChargingVoltage_mV      0 (uint)
ChargingCurrent_mA      0 (uint)
Voltage_mV              8720 (uint)
Current_mA              0 (uint)
TemperatureRaw_dC       34 (uint)
TemperatureVtsMax_dC    48950 (uint)
CellVoltage1_mV         4359 (uint)
CellVoltage2_mV         4361 (uint)
CellVoltage3_mV         0 (uint)
CellVoltage4_mV         0 (uint)
MaxTurboPwr_cW          15522 (uint)
SusTurboPwr_cW          8937 (uint)
TurboRhfEffective_mOhm  78 (uint)
TurboVload              8721 (uint)
```

Hands us loads of things on a silver platter, the irpmon dump from that is;
```
  ??? OUT BAT:02 t01 i00 c 0x22 (  0): []
  ???  IN BAT:02 t00 i00 c 0x22 (119): 01 e0 00 83 43 40 00 10 48 00 00 5a 18 09 00 00 00 00 00 00 00 00 00 63 00 64 00 00 00 00 00 10 22 00 00 22 00 36 bf 07 11 09 11 00 00 00 00 a2 3c e9 22 4e 00 11 22 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
```

Numbers seem to match up perfectly, should get a few recordings where it's not on the charger to obtain location of charging voltage and current.


