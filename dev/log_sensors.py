#!/usr/bin/env python3

import argparse
import subprocess
import time
import os
import json

import sys
sys.path.insert(1, '../../surface-aggregator-module/scripts/ssam/')

"""

"""

def get_fan_speed_directly():
    from irp_display import Fan_Set08, Fan_GetSpeed, Fan_SetSpeed
    import libssam
    def sam_cmd(ctrl, tc, cid, data, hasresp):
            req = libssam.Request(tc, 1, cid, 1, libssam.REQUEST_HAS_RESPONSE if hasresp else 0, data)
            resp = ctrl.request(req)
            return resp

    def fan_cmd(ctrl, cid, data, hasresp):
        return sam_cmd(ctrl, 5, cid, data, hasresp)

    with libssam.Controller() as c:
        speed_bytes = Fan_GetSpeed.read(bytes(fan_cmd(c, 1, [], hasresp=True)))
        return speed_bytes.rpm

def get_top_percentages():
    # top -n 2 -b -d 0.2
    res = subprocess.run(["top", "-n", "2", "-b", "-d", "0.2"], stdout=subprocess.PIPE)
    if res.returncode == 0:
        lines = res.stdout.decode("ascii").split("\n")
        pctline = [l for l in lines if l.startswith("%Cpu")]
        if not pctline:
            return {}
        rel = pctline[0]
        header, rem = rel.split(":")
        elements = [x.strip() for x in rem.split(",")]
        res = {}
        for z in elements:
            num, name = z.split(" ")
            res[name] = float(num)
        return res
    return {}

def get_sensors(sensors_bin):
    # nixos 23.11's sensors supports json output!
    res = subprocess.run([sensors_bin, "-j"], stdout=subprocess.PIPE)
    if res.returncode == 0:
        parsed = json.loads(res.stdout)
        return parsed


def capture(sensors_bin, with_speed=False, with_load=False):
    sensors = get_sensors(sensors_bin)

    if with_speed:
        sensors["fan_rpm"] = get_fan_speed_directly()

    if with_load:
        sensors["system_load"] = get_top_percentages()

    t = time.time()
    return (t, sensors)

def load_current(p):
    if not os.path.isfile(p):
        return []

    with open(p) as f:
        return json.load(f)

def write_tmp_json(records, p):
    with open(p + ".tmp", "w") as f:
        json.dump(records, f)
    
def rename_tmp_to_real(p):
    # rename is atomic, so even ctrl+c can't corrupt data here.
    os.rename(p +".tmp", p)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--delay", type=float, default=1.0, help="period between records")
    parser.add_argument("--sensors-path", default="sensors", help="binary to sensors")
    parser.add_argument("--with-speed", default=False, action="store_true", help="Record the fan speed from the cdev plugin")
    parser.add_argument("--with-load", default=False, action="store_true", help="Store system load")
    parser.add_argument("output", help="The path to write to.")
    args = parser.parse_args()

    while True:
        new_record = capture(args.sensors_path, with_speed=args.with_speed, with_load=args.with_load)
        records = load_current(args.output)
        time.sleep(args.delay)
        records.append(new_record)
        # Write to temp file and rename, to ensure atomic operation such that
        # we can't truncate the file and cancel during the write.
        write_tmp_json(records, args.output)
        rename_tmp_to_real(args.output)
