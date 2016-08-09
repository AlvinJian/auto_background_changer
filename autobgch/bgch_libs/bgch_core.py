#!/usr/bin/python3
import os, sys
import time
import random
import subprocess
import collections
import threading
import queue
import enum

from autobgch.bgch_libs.ipc_util import *
from autobgch.bgch_libs.misc_util import *
from autobgch.bgch_libs.ipcmsg_handling import *

class Stat(enum.IntEnum):
    PAUSE = 0
    PLAY = 1

class BgChCore:
    def __init__(self, bcknd, bgdir, interval=60):
        self.__set_backend(bcknd)
        self.__set_bgdir(bgdir)
        self.__set_intv(interval)

        t = time.time()
        random.seed(t)
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
        info_str = '{0},{1},{2},{3}s'.format(self.__status, self.__bg_dir, \
            self.__cur_img, self.__intv)
        return info_str

    def get_support_cmds(self):
        cmds = self.__ipc_cmd_map.keys()
        return cmds

    def enque_ipc_cmd(self, sock, cmd, data=None):
        task = (sock, cmd, data)
        self.__ipc_cmdq.put(task)
        with self.__playing_cv:
            self.__playing_cv.notify()

    def is_play(self):
        return self.__status is Stat.PLAY

    def __exec_all_cmdq(self):
        while not self.__ipc_cmdq.empty():
            sock, cmd, data = self.__ipc_cmdq.get()
            sys.stdout.write('consume cmd queue: {0}, {1}, {2}\n'.format(sock, \
                cmd, data))
            sys.stdout.flush()
            func = self.__ipc_cmd_map[cmd]
            func(sock, data)

    def __set_backend(self, script):
        script_path = os.path.join(get_bcknd_dir(), script)
        if os.path.exists(script_path):
            self.__cmd = ['/bin/sh', script_path]
        else:
            raise AttributeError('{0} does not exist'.format(script_path))

    def __set_bgdir(self, d):
        bgdir = abspath_lnx(d)
        if is_dir_and_exist(bgdir):
            self.__bg_dir = bgdir
        else:
            raise AttributeError('{0} does not exist'.format(bgdir))

    def __set_intv(self, interval):
        if interval > 0:
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
        for (root, subFolders, filenames) in os.walk(self.__bg_dir, followlinks=True):
            allimgs += list(filter(is_image, map(lambda arg: os.path.join(root, \
                arg), filenames)))

        if len(allimgs) > 0:
            if len(allimgs) == 1:
                return allimgs[0]
            else:
                random.shuffle(allimgs)
                for img in allimgs:
                    if img != self.__cur_img:
                        return img
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

        exec_func(self.__cmd, stdout=sys.stdout, stderr=sys.stderr)
        self.__cur_img = self.__cmd.pop()

    def __add_to_prev_img(self, img):
        if img == '':
            return
        if len(self.__prev_imgs) >= self.__max_prev_img_num:
            del self.__prev_imgs[0:1]
        self.__prev_imgs.append(img)

    def __build_func_map(self):
        def ipc_cmd_play(sock, data):
            self.__status = Stat.PLAY
            p = Payload(CMD=IpcCmd.IPC_MSG, DATA='Start playing')
            sock.send_ipcmsg_to_cl(p)

        def ipc_cmd_pause(sock, data):
            self.__status = Stat.PAUSE
            p = Payload(CMD=IpcCmd.IPC_MSG, DATA='Pause')
            sock.send_ipcmsg_to_cl(p)

        def ipc_cmd_next(sock, data):
            if self.__status is Stat.PAUSE:
                self.__next_pic()
            p = Payload(CMD=IpcCmd.IPC_MSG, DATA='Done')
            sock.send_ipcmsg_to_cl(p)

        def ipc_cmd_prev(sock, data):
            if len(self.__prev_imgs) < 1:
                p = Payload(CMD=IpcCmd.IPC_MSG, DATA='No previous images')
            else:
                img = self.__prev_imgs.pop()
                self.__do_chbg(img)
                p = Payload(CMD=IpcCmd.IPC_MSG, DATA='Done')

            sock.send_ipcmsg_to_cl(p)
            if self.__status is Stat.PLAY:
                with self.__playing_cv:
                    # prevent socket server from blocking
                    sock.force_release()
                    self.__playing_cv.wait(self.__intv)

        def ipc_cmd_config(sock, data):
            bg_dir, intv_str = data.split(',')
            try:
                if bg_dir != '':
                    self.__set_bgdir(bg_dir)
                if intv_str != '':
                    intv = handle_interval_arg(intv_str)
                    self.__set_intv(intv)
            except Exception as err:
                data = '{0}'.format(err)
            else:
                data = 'Done'

            p = Payload(CMD=IpcCmd.IPC_MSG, DATA = data)
            sock.send_ipcmsg_to_cl(p)

        def ipc_cmd_info(sock, data):
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
