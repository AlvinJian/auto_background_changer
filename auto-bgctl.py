#!/usr/bin/python3
import os, sys
from ipc_util import *

res = send_ipc_msg('hello world')
print(res)
