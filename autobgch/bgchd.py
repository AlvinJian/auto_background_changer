#!/usr/bin/python3
import argparse
import os
import sys
import time

from autobgch.bgch_libs.daemon_util import *
from autobgch.bgch_libs.misc_util import *
from autobgch.bgch_libs.bgch_core import *

def run():
    parser = argparse.ArgumentParser(description='random wallpaper changer daemon')
    parser.add_argument('-dir', dest='bg_dir', type=str, required=True, help='wallpaper directory')
    parser.add_argument('-intv', dest='intv', type=str, default='30s', metavar='MIN_OR_SEC', help='interval of changing wallpaper(i.e. 10s or 5m). default: 30s')
    parser.add_argument('-bcknd', dest='bcknd', type=str, required=True, metavar='SCRIPT', \
        help='script in /etc/autobgch/scripts/ as backend. official support: mate, gnome3, unity, feh')
    parser.add_argument('-dbginfo', dest='dbginfo', action='store_true', help='enable extra info for debug')
    args = parser.parse_args()

    if args.dbginfo:
        info='/tmp/bgchd-info.log'
    else:
    	info=os.devnull

    try:
        intv_num = handle_interval_arg(args.intv)
        bg_core_obj = BgChCore(bcknd=args.bcknd, bgdir = args.bg_dir, interval = intv_num)
        # bg_core_obj.main_func()
        daemonize(bg_core_obj.main_func, infolog=info)
    except Exception as e:
        print('Error: {0}'.format(e))

if __name__ == '__main__':
    run()
