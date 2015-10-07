#!/usr/bin/python3
import os
import sys
import time

class BgChCore:
    def __init__(self, bgdir, interval=60):
        absp=os.path.abspath(bgdir)
        if os.path.exists(absp):
            self.__bg_dir = absp
        else:
            raise AttributeError('no such directory')

        if interval > 0:
            self.__intv = interval
        else:
            raise AttributeError('interval error')

    def main_func(self):
        # dummy
        while True:
            pass

    def set_bgdir(self, d):
        absp=os.path.abspath(d)
        if os.path.exists(absp):
            self.__bg_dir = absp
        else:
            raise AttributeError('no such directory')

    def get_bgdir(self):
        return self.__bg_dir
