#!/usr/bin/python3
import os
import sys
import time
import random
import subprocess

class BgChCore:
    def __init__(self, bgdir, interval=60):
        absp=os.path.abspath(bgdir)
        if self.is_dir_and_exist(absp):
            self.__bg_dir = absp
        else:
            raise AttributeError('no such directory')

        if interval > 0:
            self.__intv = interval
        else:
            raise AttributeError('interval error')

        t = time.time()
        random.seed(t)
        self.__cmd = ['feh', '--bg-scale']

    def main_func(self):
        sys.stdout.write('in main routine\n')
        while True:
            self.play()

    def is_dir_and_exist(self, path):
        rslt = os.path.exists(path) and os.path.isdir(path)
        return rslt

    def set_bgdir(self, d):
        absp=os.path.abspath(d)
        if is_dir_and_exist(absp):
            self.__bg_dir = absp
        else:
            raise AttributeError('no such directory')

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
