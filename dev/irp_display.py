#!/usr/bin/env python3

import json
import sys
from enum import Enum
from collections import namedtuple

class Direction(Enum):
    Host = 0
    Sam = 1
    KIP = 2
    Debug = 3
    Surflink = 4
    def shortstr(self):
        l = {0: "OUT", 1: "IN", 2: "K", 3: "D", 4:"S"}
        return l.get(self._value_, "-")

class Type(Enum):
    Seq = 0x80
    Nseq = 0x00
    Ack = 0x40
    Nak = 0x04
    def shortstr(self):
        return self._name_

class PldType(Enum):
    Cmd = 0x80

class Tc(Enum):
    SAM  = 0x01 # /* Generic system functionality, real-time clock. */
    BAT  = 0x02 # /* Battery/power subsystem. */
    TMP  = 0x03 # /* Thermal subsystem. */
    PMC  = 0x04
    FAN  = 0x05
    PoM  = 0x06
    DBG  = 0x07
    KBD  = 0x08  # /* Legacy keyboard (Laptop 1/2). */
    FWU  = 0x09
    UNI  = 0x0a
    LPC  = 0x0b
    TCL  = 0x0c
    SFL  = 0x0d
    KIP  = 0x0e  # /* Manages detachable peripherals (Pro X/8 keyboard cover) */
    EXT  = 0x0f
    BLD  = 0x10
    BAS  = 0x11  # /* Detachment system (Surface Book 2/3). */
    SEN  = 0x12
    SRQ  = 0x13
    MCU  = 0x14
    HID  = 0x15  # /* Generic HID input subsystem. */
    TCH  = 0x16
    BKL  = 0x17
    TAM  = 0x18
    ACC0 = 0x19
    UFI  = 0x1a
    USC  = 0x1b
    PEN  = 0x1c
    VID  = 0x1d
    AUD  = 0x1e
    SMC  = 0x1f
    KPD  = 0x20
    REG  = 0x21  # /* Extended event registry. */
    SPT  = 0x22
    SYS  = 0x23
    ACC1 = 0x24
    SHB  = 0x25
    POS  = 0x26  # /* For obtaining Laptop Studio screen position. */
    def shortstr(self):
        return self._name_ + f":{self._value_:0>2x}"

def load(p):
    with open(p) as f:
        return json.load(f)

def hfmt(b):
    if type(b) is int:
        return f"{b:0>2x}"
    return " ".join(f"{x:0>2x}" for x in b)

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def fail(*args, **kwargs):
    eprint(*args, **kwargs)
    eprint("fail.")
    sys.exit(1)

"""
[{"ctrl": {"type": 128, "len": 8, "pad": 0, "seq": 118}, "cmd": {"type": 128, "tc": 1, "sid": 0, "tid": 1, "iid": 0, "rqid_lo": 159, "rqid_hi": 20, "cid": 52}, "payload": [], "time": "2023-12-10 3:46:21 AM"},
{"ctrl": {"type": 64, "len": 0, "pad": 0, "seq": 118}},
{"ctrl": {"type": 128, "len": 9, "pad": 0, "seq": 41}, "cmd": {"type": 128, "tc": 1, "sid": 1, "tid": 0, "iid": 0, "rqid_lo": 159, "rqid_hi": 20, "cid": 52}, "payload": [0], "time": "2023-12-10 3:46:21 AM"},
{"ctrl": {"type": 64, "len": 0, "pad": 0, "seq": 41}},
"""

def convert_entry(entry):
    ctrl = entry.get("ctrl")
    if ctrl:
        ctrl["type"] = Type(ctrl["type"])
    msg = entry.get("cmd")
    if msg:
        msg["type"] = PldType(msg["type"])
        msg["tc"] = Tc(msg["tc"])
        msg["sid"] = Direction(msg["sid"])


Transaction = namedtuple("Transaction", ["src", "src_ack", "response", "response_ack"])

class Consolidator:
    def __init__(self, entries):
        self.entries = entries
        self.transactions = []


    def seek_ack(self, i, lookahead=10):
        ours = self.entries[i].get("ctrl", {}).get("seq")
        for j in range(i, i + lookahead):
            candidate = self.entries[j].get("ctrl", {}).get("seq")
            if candidate == ours:
                return j

    def seek_response(self, i, lookahead=10):
        ours = self.entries[i].get("cmd", {})
        rqid_hi = ours.get("rqid_hi")
        rqid_lo = ours.get("rqid_lo")
        cid = ours.get("cid")
        our_key = (rqid_hi, rqid_lo, cid)
        for j in range(i + 1, min(i + lookahead, len(self.entries))):
            candidate = self.entries[j].get("cmd", {})
            cand_our_hi = candidate.get("rqid_hi")
            cand_qid_lo = candidate.get("rqid_lo")
            cand_cid = candidate.get("cid")
            cand_key = (cand_our_hi, cand_qid_lo, cand_cid)
            if our_key == cand_key:
                return j
            

    def process(self):
        for i in range(0, len(self.entries) - 1):
            current = self.entries[i]
            if current.get("processed"):
                continue
            if not "cmd" in current:
                continue

            ack_index = self.seek_ack(i)
            current_ack = self.entries[ack_index]
            if current is not None:
                current["processed"] = True
            if ack_index is None:
                fail(f"could not find ack or nak for: {current}")
            else:
                current_ack["processed"] = True

            

            response_index = self.seek_response(i)
            response = None
            response_ack = None
            if response_index is not None:
                response = self.entries[response_index]
                response["processed"] = True
                resp_ack_index = self.seek_ack(response_index + 1)
                if resp_ack_index is not None:
                    response_ack = self.entries[resp_ack_index]
                    response_ack["processed"] = True

            transaction = Transaction(
                src = current,
                src_ack = current_ack,
                response = response,
                response_ack = response_ack
            )
            self.transactions.append(transaction)


    @staticmethod
    def format_transaction(t):
        # <tc> <tid> <cid> <iid>
        # ssam:dd:cc:tt:ii:ff
        # followed by domain, category, target ID, instance ID
        def format_pair(entry, entry_ack):
            if entry is None:
                return None
            
            entry_msg = entry.get("cmd")
            if entry_msg is None:
                return None

            d = entry_msg["sid"].shortstr()
            tid = entry_msg["tid"]
            tc = entry_msg["tc"].shortstr()
            iid = entry_msg["iid"]
            cid = entry_msg["cid"]
            payload = entry.get("payload", [])
            hexpayload = hfmt(payload) if payload else "[]"
            pld_len = len(payload)
            ack = entry_ack.get("ctrl", {}).get("type").shortstr()
            return f'{ack: >5} {d: >3} {tc} t{tid:0>2x} i{iid:0>2x} c 0x{cid:0>2x} ({pld_len: >3}): {hexpayload}'
    
        ts = t.src.get("time", "")

        initiator = format_pair(t.src, t.src_ack)
        response = format_pair(t.response, t.response_ack)

        pad = len(ts) * " "

        if initiator and response:
            resp_payload = hfmt(t.response["payload"])
            # return f'{ts} {initiator}', f'{pad} {response}'
            return f'{ts} {initiator} => {resp_payload}', None

        else:
            return f'{ts} {initiator}', None
        



if __name__ == "__main__":
    if len(sys.argv) < 2 or (len(sys.argv) >= 2 and sys.argv[1] == "--help"):
        print(f"{sys.argv[0]} converted_irp.json")

    d = load(sys.argv[1])

    for e in d:
        convert_entry(e)

    # Drop HID stuff
    filtered = []
    for e in d:
        t = e.get("cmd", {}).get("tc")
        ignore = False
        if t in (Tc.HID, Tc.TCL):
            ignore = True
        if not ignore:
            filtered.append(e)

    c = Consolidator(filtered)
    c.process()
    for p in c.transactions:
        init, resp = Consolidator.format_transaction(p)
        if init:
            print(init)
        if resp:
            print(resp)
