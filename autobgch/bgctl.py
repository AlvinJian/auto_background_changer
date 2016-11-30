#!/usr/bin/python3
import os, sys
import argparse

from autobgch.bgch_libs.ipc_util import *
from autobgch.bgch_libs.misc_util import *
from autobgch.bgch_libs.bgch_core import *
from autobgch.bgch_libs.daemon_util import *

help_msg = """\
usage: bgctl [play|pause|prev|next|info|config -dir BG_DIR -intv MIN_OR_SEC]

controll program for bgchd

Commands:
  play      Start playing
  pause     Stop playing
  prev      Previous Wallpaper
  next      Next Wallpaper
  info      Show information of bgchd
  config    Change configuration of bgchd. check 'bgctl config --help' for detail\
"""

def print_help():
    print(help_msg)

def run():
    if not is_daemon_start(pidfile):
        print('bgchd is not running')
        sys.exit(0)

    arg_to_ipccmd = {'play':IpcCmd.IPC_PLAY, 'pause':IpcCmd.IPC_PAUSE, 'next':IpcCmd.IPC_NEXT, \
        'prev':IpcCmd.IPC_PREV, 'info':IpcCmd.IPC_INFO, 'config':IpcCmd.IPC_CONFIG}

    if len(sys.argv) < 2 or sys.argv[1] == '-h' or sys.argv[1] == '--help':
        print_help()
        sys.exit(0)

    if sys.argv[1] not in arg_to_ipccmd.keys():
        print('Command: {0} is not supported.'.format(sys.argv[1]))
        print_help()
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == 'config':
        # create additional parser for config
        conf_parser = argparse.ArgumentParser(\
            usage='bgctl config -dir BG_DIR -intv MIN_OR_SEC')
        conf_parser.add_argument('-dir', dest='bg_dir', type=str,  nargs='+', help='wallpaper directories')
        conf_parser.add_argument('-intv', dest='intv', type=str, metavar='MIN_OR_SEC', \
            help='interval of changing wallpaper(i.e. 10s or 5m)')
        conf_args = conf_parser.parse_args(sys.argv[2:])
        if conf_args.bg_dir is None and conf_args.intv is None:
            print('you have to specify one of -dir and -intv at least')
            sys.exit(1)

        bgdirs = ''
        if conf_args.bg_dir is not None:
            for d in conf_args.bg_dir:
                bgdirs += '{0}:'.format(d)
        bgdirs = bgdirs[0:len(bgdirs)-1]
        intv = conf_args.intv if conf_args.intv is not None else ''
        data = '{0},{1}'.format(bgdirs, intv)
        payload = Payload(CMD=arg_to_ipccmd[cmd], DATA=data)
    else:
        if len(sys.argv) > 2:
            no_use_arg = '{0}'.format(sys.argv[2:])
            no_use_arg = no_use_arg.strip('[]')
            print('{0} doesn\'t support further arguments: {1}'.format(cmd, no_use_arg))
            sys.exit(1)

        payload = Payload(CMD=arg_to_ipccmd[cmd], DATA='')

    try:
        res_msg = send_ipcmsg_to_sv(payload)
    except Exception as err:
        print('Error: {0}'.format(err))
        print('bgchd is busy')
        sys.exit(1)
    else:
        res_p = get_payload_obj_from_ipcmsg(res_msg)

    if cmd == 'info':
        status, bgdir, cur_img, intv = res_p.DATA.split(',')

        status = int(status)
        if Stat(status) is Stat.PLAY:
            status = 'Playing'
        elif Stat(status) is Stat.PAUSE:
            status = 'Paused'

        print('Status: {0}'.format(status))
        print('Wallpaper Directory: {0}'.format(bgdir))
        print('Current Wallpaper: {0}'.format(cur_img))
        print('Interval: {0}'.format(intv))
    else:
        print(res_p.DATA)

if __name__ == '__main__':
    run()
