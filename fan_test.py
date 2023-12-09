#!/usr/bin/env python3

import sys
sys.path.insert(1, 'surface-aggregator-module/scripts/ssam/')
import libssam


def hfmt(b):
    if type(b) is int:
        return f"{b:0>2x}"
    return " ".join(f"{x:0>2x}" for x in b)


"""
grep 'tc": 5' IRPMon-2023-12-08\ 01-26-51.json

{"ctrl": {"type": 128, "len": 12, "pad": 0, "seq": 2}, "cmd": {"type": 128, "tc": 5, "sid": 0, "tid": 1, "iid": 1, "rqid_lo": 43, "rqid_hi": 0, "cid": 8}, "payload": [0, 0, 0, 0], "time": "2023-12-08 1:26:57 AM"},
{"ctrl": {"type": 128, "len": 9, "pad": 0, "seq": 31}, "cmd": {"type": 128, "tc": 5, "sid": 1, "tid": 0, "iid": 1, "rqid_lo": 43, "rqid_hi": 0, "cid": 8}, "payload": [0], "time": "2023-12-08 1:26:57 AM"},
{"ctrl": {"type": 128, "len": 8, "pad": 0, "seq": 8}, "cmd": {"type": 128, "tc": 5, "sid": 0, "tid": 1, "iid": 1, "rqid_lo": 49, "rqid_hi": 0, "cid": 1}, "payload": [], "time": "2023-12-08 1:26:58 AM"},
{"ctrl": {"type": 128, "len": 10, "pad": 0, "seq": 37}, "cmd": {"type": 128, "tc": 5, "sid": 1, "tid": 0, "iid": 1, "rqid_lo": 49, "rqid_hi": 0, "cid": 1}, "payload": [182, 11], "time": "2023-12-08 1:26:58 AM"},
{"ctrl": {"type": 128, "len": 12, "pad": 0, "seq": 12}, "cmd": {"type": 128, "tc": 5, "sid": 0, "tid": 1, "iid": 1, "rqid_lo": 53, "rqid_hi": 0, "cid": 8}, "payload": [109, 7, 60, 15], "time": "2023-12-08 1:26:58 AM"},
{"ctrl": {"type": 128, "len": 9, "pad": 0, "seq": 42}, "cmd": {"type": 128, "tc": 5, "sid": 1, "tid": 0, "iid": 1, "rqid_lo": 53, "rqid_hi": 0, "cid": 8}, "payload": [0], "time": "2023-12-08 1:26:58 AM"},
{"ctrl": {"type": 128, "len": 10, "pad": 0, "seq": 94}, "cmd": {"type": 128, "tc": 5, "sid": 0, "tid": 1, "iid": 1, "rqid_lo": 135, "rqid_hi": 0, "cid": 11}, "payload": [0, 0], "time": "2023-12-08 1:26:59 AM"},
{"ctrl": {"type": 128, "len": 12, "pad": 0, "seq": 97}, "cmd": {"type": 128, "tc": 5, "sid": 0, "tid": 1, "iid": 1, "rqid_lo": 138, "rqid_hi": 0, "cid": 12}, "payload": [0, 0, 0, 0], "time": "2023-12-08 1:26:59 AM"},
{"ctrl": {"type": 128, "len": 9, "pad": 0, "seq": 101}, "cmd": {"type": 128, "tc": 5, "sid": 0, "tid": 1, "iid": 1, "rqid_lo": 142, "rqid_hi": 0, "cid": 14}, "payload": [2], "time": "2023-12-08 1:26:59 AM"},
{"ctrl": {"type": 128, "len": 9, "pad": 0, "seq": 104}, "cmd": {"type": 128, "tc": 5, "sid": 0, "tid": 1, "iid": 1, "rqid_lo": 145, "rqid_hi": 0, "cid": 15}, "payload": [0], "time": "2023-12-08 1:26:59 AM"},
{"ctrl": {"type": 128, "len": 9, "pad": 0, "seq": 106}, "cmd": {"type": 128, "tc": 5, "sid": 0, "tid": 1, "iid": 1, "rqid_lo": 147, "rqid_hi": 0, "cid": 15}, "payload": [1], "time": "2023-12-08 1:26:59 AM"},
{"ctrl": {"type": 128, "len": 10, "pad": 0, "seq": 163}, "cmd": {"type": 128, "tc": 5, "sid": 0, "tid": 1, "iid": 1, "rqid_lo": 204, "rqid_hi": 2, "cid": 11}, "payload": [255, 11], "time": "2023-12-08 1:27:19 AM"},
{"ctrl": {"type": 128, "len": 10, "pad": 0, "seq": 179}, "cmd": {"type": 128, "tc": 5, "sid": 0, "tid": 1, "iid": 1, "rqid_lo": 220, "rqid_hi": 2, "cid": 11}, "payload": [178, 12], "time": "2023-12-08 1:27:20 AM"},
{"ctrl": {"type": 128, "len": 10, "pad": 0, "seq": 180}, "cmd": {"type": 128, "tc": 5, "sid": 0, "tid": 1, "iid": 1, "rqid_lo": 221, "rqid_hi": 2, "cid": 11}, "payload": [121, 13], "time": "2023-12-08 1:27:21 AM"},
{"ctrl": {"type": 128, "len": 10, "pad": 0, "seq": 181}, "cmd": {"type": 128, "tc": 5, "sid": 0, "tid": 1, "iid": 1, "rqid_lo": 222, "rqid_hi": 2, "cid": 11}, "payload": [18, 13], "time": "2023-12-08 1:27:22 AM"},
{"ctrl": {"type": 128, "len": 10, "pad": 0, "seq": 184}, "cmd": {"type": 128, "tc": 5, "sid": 0, "tid": 1, "iid": 1, "rqid_lo": 225, "rqid_hi": 2, "cid": 11}, "payload": [140, 12], "time": "2023-12-08 1:27:24 AM"},
{"ctrl": {"type": 128, "len": 10, "pad": 0, "seq": 187}, "cmd": {"type": 128, "tc": 5, "sid": 0, "tid": 1, "iid": 1, "rqid_lo": 228, "rqid_hi": 2, "cid": 11}, "payload": [185, 11], "time": "2023-12-08 1:27:27 AM"},
{"ctrl": {"type": 128, "len": 10, "pad": 0, "seq": 190}, "cmd": {"type": 128, "tc": 5, "sid": 0, "tid": 1, "iid": 1, "rqid_lo": 231, "rqid_hi": 2, "cid": 11}, "payload": [0, 0], "time": "2023-12-08 1:27:28 AM"},
"""

def sam_cmd(ctrl, tc, cid, data, hasresp):
	print('TC %02x CID %02x:' % (tc, cid), hfmt(data) if data else None)
	req = libssam.Request(tc, 1, cid, 1, libssam.REQUEST_HAS_RESPONSE if hasresp else 0, data)
	resp = ctrl.request(req)
	print('\t=>', hfmt(resp) if resp else None)
	return resp

def fan_cmd(ctrl, cid, data, hasresp):
    return sam_cmd(ctrl, 5, cid, data, hasresp)

def replay():
    with libssam.Controller() as c:
        fan_cmd(c, 8, [0, 0, 0, 0], hasresp=True)
        fan_cmd(c, 1, [], hasresp=True)
        fan_cmd(c, 8, [109, 7, 60, 15], hasresp=True)
        fan_cmd(c, 11, [0, 0], hasresp=False)
        fan_cmd(c, 12, [0, 0, 0, 0], hasresp=False)
        fan_cmd(c, 14, [2], hasresp=False)
        fan_cmd(c, 15, [0], hasresp=False)
        fan_cmd(c, 15, [1], hasresp=False)
        fan_cmd(c, 11, [255, 21], hasresp=False)
        

if __name__ == '__main__':
    replay()