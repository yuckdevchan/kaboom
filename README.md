# kaboom
explosively fast app launcher using Qt.

## Installation
### Windows
1. [Download Python 3.12](https://www.python.org/ftp/python/3.12.2/python-3.12.2-amd64.exe) and install it.
2. [Download kaboom Installer](https://github.com/yuckdevchan/kaboom/releases/latest/download/kaboom-installer-windows-x86_64.exe) and install it.
3. Press **Alt-Space** to activate kaboom. The hotkey can be changed in the settings.

## Usage
### Windows
```python3 -m pip install -r requirements-windows.txt```
```python3 main.py```

### Linux
```python3 -m pip install -r requirements-linux.txt```
```python3 main.py```
#### KDE
Open kaboom, press `Alt+F3` and open `More Actions > Special Window Settings` which opens a settings page. On this page you can configure how the window should be dealt with. You can add a new setting to the window by clicking `Add Property`. The following settings are recommended:

- `Skip Taskbar`, `Force`, `Yes`
    - Doesn't show kaboom in the taskbar.
- `Focus Protection`, `Force`, `Extreme`
    - Further protects window focus for kaboom.

### MacOS
To have the keyboard shortcut working on MacOS you must register a keyboard shortcut in Automator that runs your python executable (python3) and the path to the file 'toggle_window.py' which is located in your kaboom installation directory. For example this command might look like this:

```shell
python3 "/Users/john/Documents/kaboom/toggle_window.py"
```

## Supported Functionality
- **Windows Start Menu Shortcuts** (bit broken but mostly works)
    - Just type the program you want and hitting enter will launch the first one.
- **Inline Maths Processor**
    - just do a calculation e.g `3*2` or `1+1`
    - more complex calculations work as well e.g `sqrt(25)*2` or `2e+3 * pi`
    - multiply = *
    - divide = /
    - brackets = ()
    - to power of = **
    - square root = sqrt()
    - π = pi
    - sin, cos, tan = sin(), cos(), tan()
    - e = e
- **Steam Games**
    - type `steam:` and your list of games should appear. Then type the game you want to launch.
- **BSManager Instances** (Windows only)
    - type `bsman:` and your list of instances should appear. Then type the instance you want to launch.
 
