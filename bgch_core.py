#!/usr/bin/python3
import os, sys
import time
import random
import subprocess
import collections
import threading
import queue

from ipc_util import *

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
        self.__ipc_sv_thrd = None

        self.__status='PLAY'
        self.__build_func_map()
        self.__ipc_cmdq = queue.Queue()

    def main_func(self):
        sys.stdout.write('in main routine\n')
        self.__ipc_sv_thrd = start_server_thrd(self.ipc_handler)
        while True:
            self.play()

            if not self.__ipc_sv_thrd.is_alive():
                sys.stderr.write('ipc server is dead. restarting...\n')
                sys.stderr.flush()
                self.__ipc_sv_thrd = start_server_thrd(self.ipc_handler)

    def ipc_handler(self, msg):
        # dummy output
        payload = get_payload_obj_from_ipcmsg(msg)
        sys.stdout.write('payload: {0} from ipc\n'.format(payload))
        sys.stdout.flush()
        if payload.CMD in self.__ipc_cmd_map:
            func = self.__ipc_cmd_map[payload.CMD]
            self.__ipc_cmdq.put((func, payload.DATA))

        return 'Gotcha. Payload size: {0}'.format(len(payload))

    def is_dir_and_exist(self, path):
        rslt = os.path.exists(path) and os.path.isdir(path)
        return rslt

    def set_bgdir(self, d):
        bgdir = None
        if d.startswith('~'):
            bgdir = os.path.expanduser(d)
        else:
            bgdir=os.path.abspath(d)

        if self.is_dir_and_exist(bgdir):
            self.__bg_dir = bgdir
        else:
            raise AttributeError('no such directory: {0}'.format(bgdir))

    def get_bgdir(self):
        return self.__bg_dir

    def get_rand_picpath(self):
        allimgs = []
        for (root, subFolders, filenames) in os.walk(self.__bg_dir):
            allimgs += list(filter(self.__is_image, map(lambda arg: os.path.join(root, arg), filenames)))

        if len(allimgs) > 0:
            random.shuffle(allimgs)
            return allimgs[0]
        else:
            raise FileNotFoundError('No image found')

    def play(self):
        sys.stdout.write('playing...\n')
        try:
            imgpath = self.get_rand_picpath()
        except Exception as e:
            sys.stderr.write('Error: {0}\n'.format(e))
        else:
            self.do_chbg(imgpath)
        sys.stderr.flush()
        sys.stdout.flush()
        time.sleep(self.__intv)

    def pause(self):
        pass

    def __is_image(self, filename):
        return filename.lower().endswith(('.jpg', '.jpeg', '.gif', '.png', '.tiff', '.svg', '.bmp'))

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
            self.__status = 'PLAY'
        def ipc_cmd_pause(data):
            self.__status = 'PAUSE'
        def ipc_cmd_next(data):
            pass
        def ipc_cmd_prev(data):
            pass
        def ipc_cmd_config(data):
            pass
        def ipc_cmd_info(data):
            pass

        self.__ipc_cmd_map = dict()
        self.__ipc_cmd_map['PLAY'] = ipc_cmd_play
        self.__ipc_cmd_map['PAUSE'] = ipc_cmd_pause
        self.__ipc_cmd_map['NEXT'] = ipc_cmd_next
        self.__ipc_cmd_map['PREV'] = ipc_cmd_prev
        self.__ipc_cmd_map['CONFIG'] = ipc_cmd_config
        self.__ipc_cmd_map['INFO'] = ipc_cmd_info

        self.__status_map['PLAY'] = self.play
        self.__status_map['PAUSE'] = self.pause
