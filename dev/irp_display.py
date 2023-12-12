#!/usr/bin/env python3

import json
import sys
from enum import Enum
from collections import namedtuple
import argparse
import gzip
import ctypes
import time
import glob

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

# IW(Todo) The below is copied from another project from long ago, does it need to be this complex?
# Amazing this actually works.

# Convenience mixin to allow construction of struct from a byte like object.
class Readable:
    @classmethod
    def read(cls, byte_object):
        a = cls()
        ctypes.memmove(ctypes.addressof(a), bytes(byte_object),
                       min(len(byte_object), ctypes.sizeof(cls)))
        return a


# Mixin to allow conversion of a ctypes structure to and from a dictionary.
class Dictionary:
    # Implement the iterator method such that dict(...) results in the correct
    # dictionary.
    def __iter__(self):
        v = self.to_dict(self)
        def gen():
            nonlocal v
            z = v.items()
            for k,v in z:
                yield (k, v)

        return gen()


    def to_dict(self, v):
        if (isinstance(v, Dictionary)):
            res = dict()
            for k, t in v._fields_:
                entry = getattr(v, k)
                try:
                    res[k] = entry.__iter__()
                except (TypeError, AttributeError):
                    res[k] = self.to_dict(entry)
            return res
        elif (isinstance(v, ctypes.Array)):
            res = []
            for x in v:
                try:
                    res.append(x.__iter__())
                except (TypeError, AttributeError):
                    res.append(self.to_dict(x))
            return res
        elif (isinstance(v, ctypes.Structure)):
            res = dict()
            for k,t in v._fields_:
                res[k] = self.to_dict(entry)
            return res
        return v

    # Implement the reverse method, with some special handling for dict's and
    # lists.
    def from_dict(self, dict_object):
        for k, t in self._fields_:
            set_value = dict_object[k]
            if (isinstance(set_value, dict)):
                v = t()
                v.from_dict(set_value)
                setattr(self, k, v)
            elif (isinstance(set_value, list)):
                v = getattr(self, k)
                for j in range(0, len(set_value)):
                    if (isinstance(v[j], Dictionary)):
                        v[j].from_dict(set_value[j])
                    else:
                        v[j] = set_value[j]
                setattr(self, k, v)
            else:
                setattr(self, k, set_value)

    def __str__(self):
        return str(self.to_dict(self))


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

class Role(Enum):
    Request = 0
    Response = 1
"""
    Helper class to collapse raw irp records into transactions.
"""
class Consolidator:
    def __init__(self, entries):
        self.entries = entries
        self.transactions = []


    def seek_ack(self, i, lookahead=10):
        if i >= len(self.entries):
            return
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
                current["cmd"]["role"] = Role.Request
            if ack_index is None:
                fail(f"could not find ack or nak for: {current}")
            else:
                current_ack["processed"] = True

            

            response_index = self.seek_response(i)
            response = None
            response_ack = None
            if response_index is not None:
                response = self.entries[response_index]
                response.get("cmd", {})["role"] = Role.Response
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
    def format_msg(entry, entry_ack):
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
        if entry_ack:
            ack = entry_ack.get("ctrl", {}).get("type").shortstr()
        else:
            ack = "???"
        return f'{ack: >5} {d: >3} {tc} t{tid:0>2x} i{iid:0>2x} c 0x{cid:0>2x} ({pld_len: >3}): {hexpayload}'

    @staticmethod
    def format_transaction(t):
        # <tc> <tid> <cid> <iid>
        # ssam:dd:cc:tt:ii:ff
        # followed by domain, category, target ID, instance ID
        ts = t.src.get("time", "")

        initiator = Consolidator.format_msg(t.src, t.src_ack)
        response = Consolidator.format_msg(t.response, t.response_ack)

        decoded_src = str(t.src.get("decoded", ""))
        decoded_response = str(t.response.get("decoded", "[]") if t.response else "")

        pad = len(ts) * " "

        if initiator and response:
            resp_payload = hfmt(t.response["payload"])
            # return f'{ts} {initiator}', f'{pad} {response}'
            return f'{ts} {initiator} => {resp_payload}   {decoded_src} -> {decoded_response}'

        else:
            return f'{ts} {initiator} {decoded_src}'
        
def load(p):
    opener = gzip.open if p.endswith("gz") else open
    with opener(p) as f:
        d = json.load(f)

    for e in d:
        convert_entry(e)

    return d

def filter_tc(records, ignore, allow):
    ignored = set(Tc[z] for z in ignore.split(",") if z)
    allow = set(Tc[z] for z in allow.split(",") if z)
    filtered = []
    for e in records:
        t = e.get("cmd", {}).get("tc")
        ignore = False
        if allow:
            ignore = not t in allow
        if t in ignored:
            ignore = True
        if not ignore:
            filtered.append(e)
    return filtered
    

def run_hexdump(args, records):
    for p in records:
        p = Transaction(
                        src = p,
                        src_ack = None,
                        response = None,
                        response_ack = None
                    )
        interpret(p)
        init = Consolidator.format_msg(p.src, None)
        if init:
            print(init)

def run_print(args, records):
    c = Consolidator(records)
    c.process()
    for p in c.transactions:
        interpret(p)
        init = Consolidator.format_transaction(p)
        if init:
            print(init)




class Base(ctypes.LittleEndianStructure, Dictionary, Readable):
    _pack_ = 1

MatchTuple = namedtuple("MatchTuple", ["tc", "cid", "role"])
def make_matcher(tc=None, cid=None, role=None):
    return MatchTuple(tc=tc, cid=cid, role=role)

def cmd_matches(candidate, msg_dict):
    if candidate.tc != msg_dict.get("tc", None):
        return False
    if candidate.cid != msg_dict.get("cid", None):
        return False
    if candidate.role != msg_dict.get("role", None):
        return False
    return True


class Tmp_GetTemp(Base):
    matches = make_matcher(tc=Tc.TMP, cid=0x01, role=Role.Response)
    _fields_ = [("temp", ctypes.c_uint8), ("unknown", ctypes.c_uint8)]

class Tmp_GetTempProactive(Base):
    matches = make_matcher(tc=Tc.TMP, cid=0x01, role=Role.Request)
    _fields_ = [("temp", ctypes.c_uint16)]

class Fan_SetSpeed(Base):
    matches = make_matcher(tc=Tc.FAN, cid=0x0b, role=Role.Request)
    _fields_ = [("rpm", ctypes.c_uint16)]

class Fan_Set08(Base):
    matches = make_matcher(tc=Tc.FAN, cid=0x08, role=Role.Request)
    _fields_ = [("c8_lo", ctypes.c_uint16), ("c8_hi", ctypes.c_uint16)]

class Fan_GetSpeed(Base):
    matches = make_matcher(tc=Tc.FAN, cid=0x01, role=Role.Response)
    _fields_ = [("rpm", ctypes.c_uint16)]

known_messages = [
    Fan_GetSpeed,
    Fan_SetSpeed,
    Tmp_GetTemp,
    Tmp_GetTempProactive,
    Fan_Set08,
]
def get_msg_handler(msg):
    for v in known_messages:
        if cmd_matches(v.matches, msg):
            return v

def attempt_parse(msg, payload):
    t = get_msg_handler(msg)
    if t:
        return t.read(bytes(payload))
    

def interpret(transaction):
    for side in (transaction.src, transaction.response):
        if side and "cmd" in side:
            msg = side["cmd"]
            parsed = attempt_parse(msg, side.get("payload", []))
            if parsed:
                side["decoded"] = parsed

def run_interpret(args, records):
    c = Consolidator(records)
    c.process()

    parsed_records = []
    for p in c.transactions:
        interpret(p)

        t = p.src["time"]
        t =  time.mktime(time.strptime(t, '%Y-%m-%d %I:%M:%S %p'))
        something = False
        if "decoded" in p.src:
            # print(p.src["parsed"])
            something = True
        if p.response and "decoded" in p.response:
            # print(p.response["parsed"])
            something = True
        if something:
            src_parsed = p.src.get("decoded")
            src_parsed = dict(src_parsed) if src_parsed else None
            resp_parsed = p.response.get("decoded")  if p.response else None
            resp_parsed = dict(resp_parsed) if resp_parsed else None
            entry = {}
            entry["t"] = t
            entry["src"] = src_parsed
            entry["response"] = resp_parsed
            entry["tc"] = p.src["cmd"]["tc"]._value_
            entry["cid"] = p.src["cmd"]["cid"]
            entry["tid"] = p.src["cmd"]["tid"]
            entry["iid"] = p.src["cmd"]["iid"]
    
            parsed_records.append(entry)

    if args.output:
        with open(args.output, "w") as f:
            json.dump(parsed_records, f)


import contextlib
class MockSam:
    REQUEST_HAS_RESPONSE = 1
    @staticmethod
    @contextlib.contextmanager
    def Controller():
        yield MockSam()

    def request(*arg):
        return []
    @staticmethod
    def Request(tc, tid, cid, iid, hasresp, data):
        return MockSam()

def run_replay(args, records):
    try:
        import libssam
    except ImportError:
        print("Using MockSam!")
        import time
        time.sleep(2)
        libssam = MockSam

    def sam_cmd(ctrl, tc, tid, cid, iid, data, hasresp):
            #print('TC %02x CID %02x:' % (tc, cid), hfmt(data) if data else None)
            req = libssam.Request(tc, tid, cid, iid, libssam.REQUEST_HAS_RESPONSE if hasresp else 0, data)
            resp = ctrl.request(req)
            #print('\t=>', hfmt(resp) if resp else None)
            return resp



    t = Consolidator(records)
    t.process()
    with libssam.Controller() as c:
        for p in t.transactions:
            # Only send things for which we are the source.
            if p.src.get("cmd", {}).get("sid", "") != Direction.Host:
                continue

            # Craft the request to be sent
            msg = p.src["cmd"]
            tc = msg["tc"]._value_
            tid = msg["tid"]
            cid = msg["cid"]
            iid = msg["iid"]
            data = p.src["payload"]

            hasresp = p.response is not None

            # Actually send the request! O_o
            result = sam_cmd(c, tc, tid, cid, iid, data, hasresp)
            # Compare the received result with the original result.
            if hasresp:
                # Do a result comparison and print
                printable = Consolidator.format_transaction(p)
                if p.response["payload"] != result:
                    printable += f" || {hfmt(result)}" 
                else:
                    printable += f" MATCH"
                print(printable)
            else:
                printable = Consolidator.format_transaction(p)
                print(printable)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="irp_tool")
    if len(sys.argv) < 2 or (len(sys.argv) >= 2 and sys.argv[1] == "--help"):
        print(f"{sys.argv[0]} converted_irp.json")

    parser.add_argument("--ignore-tc", default="HID,TCL", help="The SAM target categories to ignore at intake. Defaults to %(default)s, overrides accept")
    parser.add_argument("--accept-tc", default="", help="The SAM target categories to accept. Defaults to %(default)s.")

    subparsers = parser.add_subparsers(dest="command")

    def subparser_with_default(name):
        sub = subparsers.add_parser(name)
        sub.add_argument("path", help="The file to read from.")
        return sub

    hexdump_parser = subparser_with_default('hexdump')
    hexdump_parser.set_defaults(func=run_hexdump)

    print_parser = subparser_with_default('print')
    print_parser.set_defaults(func=run_print)

    replay_parser = subparser_with_default('replay')
    replay_parser.set_defaults(func=run_replay)

    interpret_parser = subparser_with_default('interpret')
    interpret_parser.add_argument("-o", "--output", default=None, help="Write json output to this path")
    interpret_parser.set_defaults(func=run_interpret)

    args = parser.parse_args()

    data = load(args.path)

    data = filter_tc(data, args.ignore_tc, args.accept_tc)

    if (args.command is None):
        parser.print_help()
        parser.exit()

    args.func(args, data)

    # Drop HID stuff
