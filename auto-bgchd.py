#!/usr/bin/python3
import argparse
import os
import sys
import time
import re

from daemon_util import *

pidfile='/tmp/auto-bgchd.pid'

def handle_interval_arg(intv):
	if intv.isdigit():
		return int(intv)
	pttrn=re.compile('^[0-9]{1,}[sm]$')
	rslt = pttrn.match(intv)
	if rslt != None:
		intv_str = rslt.group(0)
		intv_num = int(intv_str[0:-1])
		if intv_str.endswith('m'):
			intv_num *= 60
		return intv_num
	else:
		raise Exception('interval format error...')

parser = argparse.ArgumentParser(description='random wallpaper changer daemon')
parser.add_argument('-dir', dest='bg_dir', type=str, required=True, help='wallpaper directory')
parser.add_argument('-intv', dest='intv', type=str, default='20s', metavar='MIN_OR_SEC', help='interval of changing wallpaper(i.e. 10s or 5m)')
parser.add_argument('-dbginfo', dest='dbginfo', action='store_true', help='enable extra info for debug')
args = parser.parse_args()

if args.dbginfo:
	info='/tmp/auto-bgchd-info.log'
else:
	info=os.devnull

from bgch_core import *
try:
	intv_num = handle_interval_arg(args.intv)
	bg_core_obj = BgChCore(bgdir = args.bg_dir, interval = intv_num)
	daemonize(pidfile, bg_core_obj.main_func, infolog=info)
except Exception as e:
    print('Error: {0}'.format(e))
