#!/usr/bin/python3

import os, sys
import argparse
from ipc_util import *

allars = ('play', 'pause', 'next', 'prev', 'info', 'config')
configargs = ('-dir', '-intv')

parser = argparse.ArgumentParser(description='controller program for auto-bgchd')

parser.add_argument("cmd", choices=allars)

# TODO check if there are other useless arguments except config
args = parser.parse_args(sys.argv[1:2])
print(args)

if args.cmd != 'config':
    res = send_ipcmsg_by_payload_obj(Payload(CMD=args.cmd.upper(), DATA=''))
else:
    # TODO parse and verify config arg
    pass

if res != None:
    p = get_payload_obj_from_ipcmsg(res)
    print(p)
else:
    print(None)
