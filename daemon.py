import keyboard, sys, subprocess, win32gui, win32con, win32process, os, config

open_ = False

def run():
    global open_
    hwnd = win32gui.FindWindow(None, config.program_title)
    if not open_:
        open_ = True
        win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
    elif open_:
        win32gui.ShowWindow(hwnd, win32con.SW_HIDE)
        open_ = False

keyboard.add_hotkey(config.hotkey, run)
subprocess.Popen([sys.executable, "main.py"])
keyboard.wait()