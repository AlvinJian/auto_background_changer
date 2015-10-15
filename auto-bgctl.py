#!/usr/bin/python3
import os, sys
from ipc_util import *

res = send_ipcmsg_by_payload_obj(Payload(CMD='INFO', DATA=''))
print(res)
