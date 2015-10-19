#!/usr/bin/python3

import os, sys
import argparse
from ipc_util import *

arg_table = {'play':IpcCmd.IPC_PLAY, 'pause':IpcCmd.IPC_PAUSE, 'next':IpcCmd.IPC_NEXT, \
    'prev':IpcCmd.IPC_PREV, 'info':IpcCmd.IPC_INFO, 'config':IpcCmd.IPC_CONFIG}

configargs = ('-dir', '-intv')

parser = argparse.ArgumentParser(description='controller program for auto-bgchd')

parser.add_argument("cmd", choices=arg_table.keys())

# TODO check if there are other useless arguments except config
args = parser.parse_args(sys.argv[1:2])
print(args)

if args.cmd != 'config':
    cmd = arg_table[args.cmd]
    res = send_ipcmsg_by_payload_obj(Payload(CMD=cmd, DATA=''))
else:
    # TODO parse and verify config arg
    pass

if res != None:
    p = get_payload_obj_from_ipcmsg(res)
    print(p)
else:
    print(None)
