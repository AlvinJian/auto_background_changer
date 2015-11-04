#!/usr/bin/python3
import os, sys

from autobgch.bgch_libs.ipc_util import *
from autobgch.bgch_libs.misc_util import *
from autobgch.bgch_libs.bgch_core import *

def create_ipc_handler(bg_obj):
    def ipc_handler(sv, msg):
        payload = get_payload_obj_from_ipcmsg(msg)
        sys.stdout.write('payload: {0} from ipc\n'.format(payload))
        sys.stdout.flush()
        cmd = payload.CMD
        if cmd in bg_obj.get_support_cmds():
            if cmd is IpcCmd.IPC_PLAY or cmd is IpcCmd.IPC_PAUSE:
                c1 = bg_obj.is_play() and cmd is IpcCmd.IPC_PAUSE
                c2 = not bg_obj.is_play() and cmd is IpcCmd.IPC_PLAY
                if c1 or c2:
                    bg_obj.enque_ipc_cmd(sv, cmd, payload.DATA)
                else:
                    data = 'already in {0} state'.format(cmd.value.lower())
                    p = Payload(CMD=IpcCmd.IPC_MSG, DATA=data)
                    sv.send_ipcmsg_to_cl(p)
            elif cmd is IpcCmd.IPC_INFO:
                # get info without interrupting current playback
                p = Payload(CMD=IpcCmd.IPC_MSG, DATA=bg_obj.get_all_info())
                sv.send_ipcmsg_to_cl(p)
            else:
                bg_obj.enque_ipc_cmd(sv, cmd, payload.DATA)
        else:
            data = '{0} is not supported'.format(cmd)
            p = Payload(CMD=IpcCmd.IPC_MSG, DATA=data)
            sv.send_ipcmsg_to_cl(p)

    return ipc_handler
