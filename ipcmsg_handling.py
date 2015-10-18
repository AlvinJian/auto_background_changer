#!/usr/bin/python3
import os, sys

from ipc_util import *
from misc_util import *
# from bgch_core import *
import bgch_core

def create_ipc_handler(bg_obj):
    # import bgch_core

    def handle_ipc_play_pause(p):
        if p.CMD != bg_obj.get_status():
            bg_obj.enque_ipc_cmd(p.CMD, p.DATA)

    def ipc_handler(msg):
        payload = get_payload_obj_from_ipcmsg(msg)
        sys.stdout.write('payload: {0} from ipc\n'.format(payload))
        sys.stdout.flush()
        # TODO verify payload.DATA
        if payload.CMD in bg_obj.get_support_cmds():
            if payload.CMD == bgch_core.IPC_PLAY or payload.CMD == bgch_core.IPC_PAUSE:
                handle_ipc_play_pause(payload)
            else:
                bg_obj.enque_ipc_cmd(payload.CMD, payload.DATA)
            return 'Sucess'
        else:
            return '0'

    return ipc_handler
