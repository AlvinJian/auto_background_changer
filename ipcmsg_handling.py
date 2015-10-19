#!/usr/bin/python3
import os, sys

from ipc_util import *
from misc_util import *
from bgch_core import *

def create_ipc_handler(bg_obj):
    def handle_ipc_play_pause(p):
        c1 = bg_obj.is_play() and p.CMD is IpcCmd.IPC_PAUSE
        c2 = not bg_obj.is_play() and p.CMD is IpcCmd.IPC_PLAY
        if c1 or c2:
            bg_obj.enque_ipc_cmd(p.CMD, p.DATA)

    def ipc_handler(msg):
        payload = get_payload_obj_from_ipcmsg(msg)
        sys.stdout.write('payload: {0} from ipc\n'.format(payload))
        sys.stdout.flush()
        cmd = payload.CMD
        if cmd in bg_obj.get_support_cmds():
            if cmd is IpcCmd.IPC_PLAY or cmd is IpcCmd.IPC_PAUSE:
                handle_ipc_play_pause(payload)
            elif cmd is IpcCmd.IPC_INFO:
                return bg_obj.get_all_info()
            else:
                bg_obj.enque_ipc_cmd(payload.CMD, payload.DATA)
            return 'Sucess'
        else:
            return '0'

    return ipc_handler
