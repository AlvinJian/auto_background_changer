#!/usr/bin/python3
try:
    from setuptools import setup, find_packages, Extension
except ImportError:
    import ez_setup
    ez_setup.use_setuptools()
    from setuptools import setup, find_packages, Extension

data_files=[
    ('/etc/autobgch/scripts/',['autobgch/scripts/feh', 'autobgch/scripts/mate',
        'autobgch/scripts/gnome3', 'autobgch/scripts/unity', 'autobgch/scripts/xfce4', 
        'autobgch/scripts/plasma5', 'autobgch/scripts/lxqt']),
    ('/etc/autobgch/autostart/', ['autobgch/autostart/bgchd-gnome.desktop',
        'autobgch/autostart/bgchd-mate.desktop'])
]

from autobgch.bgch_libs.bgch_core import __version__

setup(
    name='auto background changer',
    version=__version__,
    description='A simple wallpaper changer',
    long_description="""A simple wallpaper changer supporting multiple backends
        for Linux or other X11 system""",
    url='https://github.com/AlvinJian/auto_background_changer',
    author='AlvinJian',
    author_email='alvinchien0624@gmail.com',
    keywords='wallpaper changer',
    packages=find_packages(),
    package_data = {'autobgch':['scripts/*']},
    data_files=data_files,
    entry_points={
        'console_scripts': [
            'bgchd=autobgch.bgchd:run',
            'bgctl=autobgch.bgctl:run'
        ],
    },
)
