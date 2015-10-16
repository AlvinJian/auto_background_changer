#!/usr/bin/python3
import os, sys
import time
import random
import subprocess
import collections
import threading
import queue

from ipc_util import *
from misc_util import *

IPC_PLAY = 'PLAY'
IPC_PAUSE = 'PAUSE'
IPC_NEXT = 'NEXT'
IPC_PREV = 'PREV'
IPC_CONFIG = 'CONFIG'
IPC_INFO = 'INFO'

class BgChCore:
    def __init__(self, bgdir, interval=60):
        self.set_bgdir(bgdir)

        if interval > 0:
            self.__intv = interval
        else:
            raise AttributeError('interval error')

        t = time.time()
        random.seed(t)
        self.__cmd = ['feh', '--bg-scale']
        self.__status='PLAY'
        self.__playing_cv = threading.Condition()
        self.__build_func_map()

        # self.__status might be changed by ipc server thread
        # but read by main thread, so a lock is needed
        self.__ipc_sv_thrd = None
        self.__status_lck = threading.Lock()

        # bg_dir and intv are changed by main thread only,
        # so ipc commands are put to queue and exec by main thread
        self.__ipc_cmdq = queue.Queue()

    def main_func(self):
        sys.stdout.write('in main routine\n')
        self.__ipc_sv_thrd = start_server_thrd(self.ipc_handler)
        while True:
            self.exec_all_cmdq()
            st = self.get_status_lck()
            self.__status_map[st]()

            if not self.__ipc_sv_thrd.is_alive():
                sys.stderr.write('ipc server is dead. restarting...\n')
                sys.stderr.flush()
                self.__ipc_sv_thrd = start_server_thrd(self.ipc_handler)

    def ipc_handler(self, msg):
        # TODO verify payload.DATA
        payload = get_payload_obj_from_ipcmsg(msg)
        sys.stdout.write('payload: {0} from ipc\n'.format(payload))
        sys.stdout.flush()
        if payload.CMD in self.__ipc_cmd_map:
            func = self.__ipc_cmd_map[payload.CMD]
            res = func(payload.DATA)
            # self.__ipc_cmdq.put((func, payload.DATA))
            # self.__playing_cv.notify()
            return '{0}'.format(res)
        else:
            return '0'

    def exec_all_cmdq(self):
        while not self.__ipc_cmdq.empty():
            cmd = self.__ipc_cmdq.get()
            cmd[0](cmd[1])

    def set_bgdir(self, d):
        bgdir = None
        if d.startswith('~'):
            bgdir = os.path.expanduser(d)
        else:
            bgdir=os.path.abspath(d)

        if is_dir_and_exist(bgdir):
            self.__bg_dir = bgdir
        else:
            raise AttributeError('no such directory: {0}'.format(bgdir))

    # __status is a primitive type, so st is not reference
    def get_status_lck(self):
        with self.__status_lck:
            st = self.__status
        return st

    def set_status_lck(self, st):
        with self.__status_lck:
            self.__status_lck = st

    def play(self):
        with self.__playing_cv:
            self.__play()
            self.__playing_cv.wait(self.__intv)

    def pause(self):
        with self.__playing_cv:
            self.__playing_cv.wait()

    def get_rand_picpath(self):
        allimgs = []
        for (root, subFolders, filenames) in os.walk(self.__bg_dir):
            allimgs += list(filter(is_image, map(lambda arg: os.path.join(root, arg), filenames)))

        if len(allimgs) > 0:
            random.shuffle(allimgs)
            return allimgs[0]
        else:
            raise FileNotFoundError('No image found')

    def __play(self):
        sys.stdout.write('playing...\n')
        try:
            imgpath = self.get_rand_picpath()
        except Exception as e:
            sys.stderr.write('Error: {0}\n'.format(e))
        else:
            self.do_chbg(imgpath)
        sys.stderr.flush()
        sys.stdout.flush()

    def do_chbg(self, imgpath):
        self.__cmd.append(imgpath)
        sys.stdout.write('apply: {0}\n'.format(self.__cmd))
        ver = float(sys.version.split()[0][0:3])
        if (ver >= 3.5):
            exec_func = subprocess.run
        else:
            exec_func = subprocess.call
        exec_func(self.__cmd, stdout=sys.stdout, stderr=sys.stderr)
        self.__cmd.pop()

    def __build_func_map(self):
        def ipc_cmd_play(data):
            if self.get_status_lck() == 'PAUSE':
                with self.__status_lck:
                    self.set_status_lck('PLAY')
                    self.__playing_cv.notify()
                return 'Begin playing'

        def ipc_cmd_pause(data):
            if self.get_status_lck() == 'PLAY':
                with self.__status_lck:
                    self.__status = 'PAUSE'
                    self.__playing_cv.notify()

        def ipc_cmd_next(data):
            pass
        def ipc_cmd_prev(data):
            pass
        def ipc_cmd_config(data):
            pass
        def ipc_cmd_info(data):
            pass

        self.__ipc_cmd_map = dict()
        self.__ipc_cmd_map[IPC_PLAY] = ipc_cmd_play
        self.__ipc_cmd_map[IPC_PAUSE] = ipc_cmd_pause
        self.__ipc_cmd_map[IPC_NEXT] = ipc_cmd_next
        self.__ipc_cmd_map[IPC_PREV] = ipc_cmd_prev
        self.__ipc_cmd_map[IPC_CONFIG] = ipc_cmd_config
        self.__ipc_cmd_map[IPC_INFO] = ipc_cmd_info

        self.__status_map = dict()
        self.__status_map['PLAY'] = self.play
        self.__status_map['PAUSE'] = self.pause
