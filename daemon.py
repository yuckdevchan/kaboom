import keyboard, sys, subprocess, win32gui, win32process, os

open = False

def run():
    global open
    if not open:
        subprocess.Popen([sys.executable, "main.py"])
        open = True
    elif open:
        # Find the window with the title 'kaboom'
        hwnd = win32gui.FindWindow(None, 'kaboom')
        if hwnd:
            # Get the process ID associated with the window
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            # Use os.kill to send a termination signal to the process
            os.kill(pid, 9)
        open = False

keyboard.add_hotkey('alt + d', run)

keyboard.wait()