#!/usr/bin/python3
import os, sys
import argparse
from ipc_util import *

arg_to_ipccmd = {'play':IpcCmd.IPC_PLAY, 'pause':IpcCmd.IPC_PAUSE, 'next':IpcCmd.IPC_NEXT, \
    'prev':IpcCmd.IPC_PREV, 'info':IpcCmd.IPC_INFO, 'config':IpcCmd.IPC_CONFIG}

parser = argparse.ArgumentParser(description='controller program for auto-bgchd')
arggrp = parser.add_mutually_exclusive_group(required=True)

arggrp.add_argument('-play', action='store_true', help='start playing')
arggrp.add_argument('-pause', action='store_true', help='pause playing')
arggrp.add_argument('-next', action='store_true', help='next background')
arggrp.add_argument('-prev', action='store_true', help='previous background')
arggrp.add_argument('-info', action='store_true', help='get current info of auto-bgchd')
arggrp.add_argument('-config', action='store_true', \
    help='change config of auto-bgchd. ex. auto-bgctl -config -dir BG_DIR -intv MIN_OR_SEC')

pargs = parser.parse_args(sys.argv[1:2])
print(pargs)
args_d = vars(pargs)
cmd = ''
for k in args_d.keys():
    if args_d[k] == True:
        cmd = k
        break

if cmd == 'config':
    # TODO parse and verify config args
    conf_parser = argparse.ArgumentParser(\
        usage='auto-bgctl -config -dir BG_DIR -intv MIN_OR_SEC')
    conf_parser.add_argument('-dir', dest='bg_dir', type=str, help='wallpaper directory')
    conf_parser.add_argument('-intv', dest='intv', type=str, metavar='MIN_OR_SEC', \
        help='interval of changing wallpaper(i.e. 10s or 5m)')
    conf_args = conf_parser.parse_args(sys.argv[2:])
    print(conf_args)
    if conf_args.bg_dir is None and conf_args.intv is None:
        print('you have to specify either -dir or -intv')
        sys.exit(1)
    bg_dir = conf_args.bg_dir if conf_args.bg_dir is not None else ''
    intv = conf_args.intv if conf_args.intv is not None else ''
    data = '{0},{1}'.format(bg_dir, intv)
    payload = Payload(CMD=arg_to_ipccmd[cmd], DATA=data)
else:
    if len(sys.argv) > 2:
        print('{0} doesn\'t support these arguments: {1}'.format(cmd, sys.argv[2:]))
        sys.exit(1)
    payload = payload = Payload(CMD=arg_to_ipccmd[cmd], DATA='')

res = send_ipcmsg_by_payload_obj(payload)
print(res)
