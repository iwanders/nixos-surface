#!/usr/bin/env python3

import sys
sys.path.insert(1, '../../surface-aggregator-module/scripts/ssam/')
import libssam

from irp_display import Fan_Set08, Fan_GetSpeed, Fan_SetSpeed

def hfmt(b):
    if type(b) is int:
        return f"{b:0>2x}"
    return " ".join(f"{x:0>2x}" for x in b)

def sam_cmd(ctrl, tc, cid, data, hasresp):
	print('TC %02x CID %02x:' % (tc, cid), hfmt(data) if data else None)
	req = libssam.Request(tc, 1, cid, 1, libssam.REQUEST_HAS_RESPONSE if hasresp else 0, data)
	resp = ctrl.request(req)
	print('\t=>', hfmt(resp) if resp else None)
	return resp

def fan_cmd(ctrl, cid, data, hasresp):
    return sam_cmd(ctrl, 5, cid, data, hasresp)




if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print(sys.argv[0] + " -> get speed")
        print(sys.argv[0] + " value -> sends 11")
        print(sys.argv[0] + " lower upper -> sends 8")



    if len(sys.argv) == 1:
        with libssam.Controller() as c:
            speed_bytes = Fan_GetSpeed.read(bytes(fan_cmd(c, 1, [], hasresp=True)))
            print(speed_bytes.rpm)

    if len(sys.argv) == 2:
        desired_speed = int(sys.argv[1])
        speed_cmd = Fan_SetSpeed()
        speed_cmd.rpm = desired_speed
        with libssam.Controller() as c:
            fan_cmd(c, 11, bytes(speed_cmd), hasresp=False)


    if len(sys.argv) == 3:
        speed_cmd = Fan_Set08()
        speed_cmd.c8_lo = int(sys.argv[1])
        speed_cmd.c8_hi = int(sys.argv[2])
        with libssam.Controller() as c:
            fan_cmd(c, 11, bytes(speed_cmd), hasresp=False)

        