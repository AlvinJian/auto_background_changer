### Description
A simple wallpaper changer supporting various backends. It currently supports Gnome 3, Unity, Mate Desktop and feh(for lightweight window manager, such as i3, openbox...etc.). User can also add custom scripts in ```/etc/autobgch/scripts/``` and pass the script name by ```-bcknd YOUR_SCRIPT``` to the daemon.
### Installation
Download the tarball from <a href=https://github.com/AlvinJian/auto_background_changer/releases>release archives</a> and decompress it. Execute the following command in the source code directory to install:
```
$ sudo python3 setup.py install
```
There is also an <a href=https://aur.archlinux.org/packages/python-autobgch/>AUR</a> for Arch Linux users.
### Usage
This program has two parts: <b>bgchd</b>(the daemon) and <b>bgctl</b>(the controller).

* <b>bgchd</b> (the daemon). <b>bgchd</b> is responsible for changing wallpaper periodically :
```
usage: bgchd [-h] -dir BG_DIR [BG_DIR ...] [-intv MIN_OR_SEC] -bcknd SCRIPT
             [-rpl]

random wallpaper changer daemon

optional arguments:
  -h, --help            show this help message and exit
  -dir BG_DIR [BG_DIR ...]
                        wallpaper directories
  -intv MIN_OR_SEC      interval of changing wallpaper(i.e. 10s or 5m).
                        default: 30s
  -bcknd SCRIPT         script in /etc/autobgch/scripts/ as backend. official
                        support: mate, gnome3, unity, feh, plasma5
  -rpl                  replace exsiting daemon if any
```

* <b>bgctl</b> (the controller). <b>bgctl</b> is responsible for controlling bgchd during its runtime.
```
usage: bgctl [play|pause|prev|next|info|config -dir BG_DIR -intv MIN_OR_SEC]

control program for bgchd

Commands:
  play      Start playing
  pause     Stop playing
  prev      Previous Wallpaper
  next      Next Wallpaper
  info      Show information of bgchd
  config    Change configuration of bgchd. check 'bgctl config --help' for detail
```
### Demo
YouTube: <a href="https://www.youtube.com/watch?v=SQKqVjSjbuY">https://www.youtube.com/watch?v=SQKqVjSjbuY</a>
<iframe width="640" height="360" src="https://www.youtube.com/embed/SQKqVjSjbuY" frameborder="0" allowfullscreen></iframe>
### Autostart
For GNOME and Mate users, copy the template in ```/etc/autobgch/autostart/``` to ```$HOME/.config/autostart/``` and modify it as you need. For the users of lightweight window manager(i3, openbox...etc.), just add <b>bgchd</b> and arguments that you need to the startup script of your window manager.
