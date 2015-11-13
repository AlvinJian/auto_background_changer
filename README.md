A simple wallpaper changer supporting various backends. It Currently supports Gnome 3, Unity, Mate Desktop and feh(for lightweight window manager, such as i3, openbox...etc.). User can also add custom scripts in ```/etc/autobgch/scripts/``` and pass the script name by ```-bcknd YOUR_SCRIPT``` to the daemon.

This program has two parts: bgchd(the daemon) and bgctl(the controller).

* bgchd (the daemon). ```bgchd``` is responsible for changing wallpaper periodically :
```
usage: bgchd [-h] -dir BG_DIR [-intv MIN_OR_SEC] -bcknd SCRIPT

random wallpaper changer daemon

optional arguments:
  -h, --help        show this help message and exit
  -dir BG_DIR       wallpaper directory
  -intv MIN_OR_SEC  interval of changing wallpaper(i.e. 10s or 5m). default:
                    30s
  -bcknd SCRIPT     script in /etc/autobgch/scripts/ as backend. official
                    support: mate, gnome3, unity, feh
```

* bgctl (the controller). ```bgctl``` is responsible for controlling bgchd during its runtime.
```
usage: bgctl [play|pause|prev|next|info|config -dir BG_DIR -intv MIN_OR_SEC]

controll program for bgchd

Commands:
  play      Start playing
  pause     Stop playing
  prev      Previous Wallpaper
  next      Next Wallpaper
  info      Show information of bgchd
  config    Change configuration of bgchd. check 'bgctl config --help' for detail
```
