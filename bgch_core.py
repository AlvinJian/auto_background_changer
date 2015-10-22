#!/usr/bin/python3
import os, sys
import time
import random
import subprocess
import collections
import threading
import queue
import enum

from ipc_util import *
from misc_util import *
from ipcmsg_handling import *

class Stat(enum.IntEnum):
    PAUSE = 0
    PLAY = 1

class BgChCore:
    def __init__(self, bgdir, interval=60):
        # a lock syncing get_all_info, is_play methods and all properties: bg_dir,
        # status, current pic and interval
        self.__info_lck = threading.Lock()

        self.__set_bgdir(bgdir)
        self.__set_intv(interval)

        t = time.time()
        random.seed(t)
        self.__cmd = ['feh', '--bg-scale']
        self.__status = Stat.PLAY
        self.__playing_cv = threading.Condition()
        self.__build_func_map()

        self.__ipc_sv_thrd = None
        # BgChCore's properties are changed by itself within main thread only,
        # so ipc commands which modify those properties are put to queue
        # and exec in main thread
        self.__ipc_cmdq = queue.Queue()

        self.__max_prev_img_num = 10
        self.__prev_imgs = []
        self.__cur_img = ''

    def main_func(self):
        sys.stdout.write('in main routine\n')
        ipc_handler = create_ipc_handler(self)
        self.__ipc_sv_thrd = start_server_thrd(ipc_handler)
        while True:
            self.__exec_all_cmdq()
            self.__status_map[self.__status]()
            if not self.__ipc_sv_thrd.is_alive():
                sys.stderr.write('ipc server is dead. restarting...\n')
                sys.stderr.flush()
                self.__ipc_sv_thrd = start_server_thrd(ipc_handler)

    def get_all_info(self):
        with self.__info_lck:
            info_str = '{0},{1},{2},{3}s'.format(self.__status, self.__bg_dir, \
                self.__cur_img, self.__intv)
            return info_str

    def get_support_cmds(self):
        cmds = self.__ipc_cmd_map.keys()
        return cmds

    def enque_ipc_cmd(self, cmd, data=None):
        task = (cmd, data)
        self.__ipc_cmdq.put(task)
        with self.__playing_cv:
            self.__playing_cv.notify()

    def is_play(self):
        with self.__info_lck:
            return self.__status is Stat.PLAY

    def __exec_all_cmdq(self):
        while not self.__ipc_cmdq.empty():
            task = self.__ipc_cmdq.get()
            sys.stdout.write('consume cmd queue: {0}\n'.format(task))
            sys.stdout.flush()
            func = self.__ipc_cmd_map[task[0]]
            func(task[1])

    def __set_bgdir(self, d):
        bgdir = abspath_lnx(d)
        if is_dir_and_exist(bgdir):
            with self.__info_lck:
                self.__bg_dir = bgdir
        else:
            raise AttributeError('no such directory: {0}'.format(bgdir))

    def __set_intv(self, interval):
        if interval > 0:
            with self.__info_lck:
                self.__intv = interval
        else:
            raise AttributeError('interval error')

    def __play(self):
        with self.__playing_cv:
            self.__next_pic()
            self.__playing_cv.wait(self.__intv)

    def __pause(self):
        with self.__playing_cv:
            self.__playing_cv.wait()

    def __rand_picpath(self):
        allimgs = []
        for (root, subFolders, filenames) in os.walk(self.__bg_dir):
            allimgs += list(filter(is_image, map(lambda arg: os.path.join(root, arg), filenames)))

        if len(allimgs) > 0:
            random.shuffle(allimgs)
            return allimgs[0]
        else:
            raise FileNotFoundError('No image found')

    def __next_pic(self):
        sys.stdout.write('next pic...\n')
        try:
            imgpath = self.__rand_picpath()
        except Exception as e:
            sys.stderr.write('Error: {0}\n'.format(e))
        else:
            self.__add_to_prev_img(self.__cur_img)
            self.__do_chbg(imgpath)

        sys.stderr.flush()
        sys.stdout.flush()

    def __do_chbg(self, imgpath):
        self.__cmd.append(imgpath)
        sys.stdout.write('apply: {0}\n'.format(self.__cmd))
        ver = float(sys.version.split()[0][0:3])
        if (ver >= 3.5):
            exec_func = subprocess.run
        else:
            exec_func = subprocess.call

        with self.__info_lck:
            exec_func(self.__cmd, stdout=sys.stdout, stderr=sys.stderr)
            self.__cur_img = self.__cmd.pop()

    def __add_to_prev_img(self, img):
        if img == '':
            return
        if len(self.__prev_imgs) >= self.__max_prev_img_num:
            del self.__prev_imgs[0:1]
        self.__prev_imgs.append(img)

    def __set_status(self, stat):
        with self.__info_lck:
            self.__status = stat

    def __build_func_map(self):
        def ipc_cmd_play(data):
            self.__set_status(Stat.PLAY)

        def ipc_cmd_pause(data):
            self.__set_status(Stat.PAUSE)

        def ipc_cmd_next(data):
            if self.__status is Stat.PAUSE:
                self.__next_pic()

        def ipc_cmd_prev(data):
            if len(self.__prev_imgs) < 1:
                return

            img = self.__prev_imgs.pop()
            self.__do_chbg(img)
            if self.__status is Stat.PLAY:
                with self.__playing_cv:
                    self.__playing_cv.wait(self.__intv)

        def ipc_cmd_config(data):
            bg_dir, intv = data.split(',')
            intv = intv.strip() # get rid of space if it exists...
            try:
                if bg_dir != '':
                    self.__set_bgdir(bg_dir)
                if intv.isdigit():
                    self.__set_intv(int(intv))
            except Exception as err:
                sys.stderr.write('Error: {0}\n'.format(err))
                sys.stderr.flush()

        def ipc_cmd_info(data):
            # dummy
            pass

        self.__ipc_cmd_map = dict()
        self.__ipc_cmd_map[IpcCmd.IPC_PLAY] = ipc_cmd_play
        self.__ipc_cmd_map[IpcCmd.IPC_PAUSE] = ipc_cmd_pause
        self.__ipc_cmd_map[IpcCmd.IPC_NEXT] = ipc_cmd_next
        self.__ipc_cmd_map[IpcCmd.IPC_PREV] = ipc_cmd_prev
        self.__ipc_cmd_map[IpcCmd.IPC_CONFIG] = ipc_cmd_config
        self.__ipc_cmd_map[IpcCmd.IPC_INFO] = ipc_cmd_info

        self.__status_map = dict()
        self.__status_map[Stat.PLAY] = self.__play
        self.__status_map[Stat.PAUSE] = self.__pause
