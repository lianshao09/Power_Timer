# Power Timer

A small Linux desktop app that suspends, restarts or shuts down your computer
after a delay or at a set time.

I made this for my own use. If you find it useful, you're welcome to take it
and use it.

- **Actions:** Suspend, Restart, Shutdown
- **Modes:** Countdown (hours/minutes/seconds) or At time (HH:MM, rolls to the next day if already passed)
- **Countdown window:** minimal black screen with the system clock and remaining time
  - `F11` or double-click: toggle full screen
  - `Esc`: leave full screen, then cancel and return to settings

## Install (Debian / Ubuntu / Linux Mint)

Download `power-timer_1.0.0_all.deb` from the
[Releases](../../releases) page, then:

```bash
sudo apt install ./power-timer_1.0.0_all.deb
```

Launch it from the application menu ("Power Timer") or run `power-timer`.

Requires `python3` and `python3-tk` (installed automatically as dependencies).

## Run from source

```bash
sudo apt install python3 python3-tk
python3 usr/lib/power-timer/power_timer.py
```

## Build the .deb

From the repository root:

```bash
chmod +x usr/bin/power-timer
mkdir -p build && cp -r DEBIAN usr build/
dpkg-deb --build build power-timer_1.0.0_all.deb
rm -rf build
```

(A staging folder is used so `README.md`, `LICENSE` and `.git` don't end up inside the package.)

## How it works

When the timer ends, the app runs `systemctl suspend|reboot|poweroff`
(falling back to `loginctl`). On a normal desktop session this needs no root
password.

## License

[MIT](LICENSE)
