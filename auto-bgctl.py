#!/usr/bin/python3
import os, sys
from ipc_util import *

playagrs = ('play', )
pauseargs = ('pause', )
nextargs = ('next', )
prevargs = ('prev', )
infoargs = ('info', )
configargs = ('config', '-dir', '-intv', )

#test
res = send_ipcmsg_by_payload_obj(Payload(CMD='PLAY', DATA=''))
print(res)
