#!/usr/bin/python3
from setuptools import setup, find_packages
from os import path

setup(
    name='auto background changer',
    version='0.2.1',
    description='A simple wallpaper changer',
    long_description='A simple wallpaper changer based on feh for Linux(X11)',
    url='https://github.com/AlvinJian/auto_background_changer',
    author='AlvinJian',
    author_email='alvinchien0624@gmail.com',
    keywords='wallpaper changer',
    packages=find_packages(),
    dependency_links = ['http://feh.finalrewind.org/'],
    entry_points={
        'console_scripts': [
            'bgchd=autobgch.bgchd:run',
            'bgctl=autobgch.bgctl:run'
        ],
    },
)
