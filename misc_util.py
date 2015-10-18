#!/usr/bin/python3
import os, sys
import re

def is_dir_and_exist(path):
    return os.path.exists(path) and os.path.isdir(path)

def is_image(filename):
    return filename.lower().endswith(('.jpg', '.jpeg', '.gif', '.png', '.tiff', '.svg', '.bmp'))

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
