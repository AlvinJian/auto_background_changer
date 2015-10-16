#!/usr/bin/python3
import os, sys

def is_dir_and_exist(path):
    return os.path.exists(path) and os.path.isdir(path)

def is_image(filename):
    return filename.lower().endswith(('.jpg', '.jpeg', '.gif', '.png', '.tiff', '.svg', '.bmp'))
