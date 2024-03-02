# Battery


## Towards smart charging

It still (after weeks on the charger) hasn't enabled...

Manually enabling smart charging is a no go:

> ruled out by `BatteryDm.cs`, it explicitly throws when trying to ste it to true.

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


On battery:
```
  ???  IN BAT:02 t00 i00 c 0x22 (119): 01 c0 00 87 03 40 00 04 04 00 00 40 19 09 00 00 00 00 00 00 00 00 00 48 00 64 00 60 22 fd 0b b1 1e 6e f9 18 00 e8 b7 67 0f 4b 0f 00 00 00 00 6f 34 ed 1e 50 00 2e 1f 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00

$ cat 2024_02_29_uart_battery_general_on_battery.txt 
PS C:\Users\ivor> sdmc batterypropget GeneralStandard AnythingType
GeneralStandard : [Complex (23 Properties]
BatteryPhysicalDetect   1 (uint)
BatteryStatus           192 (uint)
OperationStatus         4195207 (uint)
ChargingStatus          1028 (uint)
GaugingStatus           596288 (uint)
SafetyStatus            0 (uint)
PfStatus                0 (uint)
RelativeStateOfCharge   72 (uint)
StateOfHealth           100 (uint)
ChargingVoltage_mV      8800 (uint)
ChargingCurrent_mA      3069 (uint)
Voltage_mV              7857 (uint)
Current_mA              63854 (uint)
TemperatureRaw_dC       24 (uint)
TemperatureVtsMax_dC    47080 (uint)
CellVoltage1_mV         3943 (uint)
CellVoltage2_mV         3915 (uint)
CellVoltage3_mV         0 (uint)
CellVoltage4_mV         0 (uint)
MaxTurboPwr_cW          13423 (uint)
SusTurboPwr_cW          7917 (uint)
TurboRhfEffective_mOhm  80 (uint)
TurboVload              7982 (uint)

```

on AC

```
  ???  IN BAT:02 t00 i00 c 0x22 (119): 01 80 00 87 03 40 10 08 04 00 00 10 18 09 00 00 00 00 00 00 00 00 00 47 00 64 00 60 22 c8 10 f6 20 c6 0f 1a 00 e8 b7 73 10 7b 10 00 00 00 00 c1 35 96 1f 50 00 54 20 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00

$ cat 2024_02_29_uart_battery_general_on_ac.txt 
PS C:\Users\ivor> sdmc batterypropget GeneralStandard AnythingType
GeneralStandard : [Complex (23 Properties]
BatteryPhysicalDetect   1 (uint)
BatteryStatus           128 (uint)
OperationStatus         272630663 (uint)
ChargingStatus          1032 (uint)
GaugingStatus           595984 (uint)
SafetyStatus            0 (uint)
PfStatus                0 (uint)
RelativeStateOfCharge   71 (uint)
StateOfHealth           100 (uint)
ChargingVoltage_mV      8800 (uint)
ChargingCurrent_mA      4296 (uint)
Voltage_mV              8438 (uint)
Current_mA              4038 (uint)
TemperatureRaw_dC       26 (uint)
TemperatureVtsMax_dC    47080 (uint)
CellVoltage1_mV         4211 (uint)
CellVoltage2_mV         4219 (uint)
CellVoltage3_mV         0 (uint)
CellVoltage4_mV         0 (uint)
MaxTurboPwr_cW          13761 (uint)
SusTurboPwr_cW          8086 (uint)
TurboRhfEffective_mOhm  80 (uint)
TurboVload              8276 (uint)

```

